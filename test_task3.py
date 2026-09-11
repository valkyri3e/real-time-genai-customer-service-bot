import unittest
from unittest.mock import patch

import ticket_workflow as task3


class TestTask3(unittest.TestCase):

    # -------------------------------
    # Priority Tests
    # -------------------------------

    def test_calculate_priority_critical(self):
        result = task3.calculate_priority(
            "critical",
            "angry",
            120,
            "high"
        )
        self.assertEqual(result, "Critical")

    def test_calculate_priority_high(self):
        result = task3.calculate_priority(
            "high",
            "neutral",
            0,
            "high"
        )
        self.assertEqual(result, "High")

    def test_calculate_priority_medium(self):
        result = task3.calculate_priority(
            "medium",
            "neutral",
            0,
            "medium"
        )
        self.assertEqual(result, "Medium")

    def test_calculate_priority_low(self):
        result = task3.calculate_priority(
            "low",
            "positive",
            0,
            "low"
        )
        self.assertEqual(result, "Low")

    # -------------------------------
    # Working Day Tests
    # -------------------------------

    def test_working_day(self):
        test_date = task3.datetime(2026, 9, 16)

        result = task3.is_working_day(test_date)

        self.assertTrue(result)

    def test_weekend_is_not_working_day(self):
        test_date = task3.datetime(2026, 9, 12)

        result = task3.is_working_day(test_date)

        self.assertFalse(result)

    def test_holiday_is_not_working_day(self):
        test_date = task3.datetime(2026, 9, 10)

        result = task3.is_working_day(test_date)

        self.assertFalse(result)

    # -------------------------------
    # SLA Tests
    # -------------------------------

    @patch("ticket_workflow.is_working_day", return_value=True)
    def test_sla_on_time(self, mock_working_day):
        result = task3.calculate_sla(
            "Critical",
            30
        )

        self.assertEqual(
            result["allowed_minutes"],
            60
        )

        self.assertEqual(
            result["working_minutes"],
            30
        )

        self.assertEqual(
            result["status"],
            "ON TIME"
        )

    @patch("ticket_workflow.is_working_day", return_value=True)
    def test_sla_warning(self, mock_working_day):
        result = task3.calculate_sla(
            "Critical",
            50
        )

        self.assertEqual(
            result["allowed_minutes"],
            60
        )

        self.assertEqual(
            result["working_minutes"],
            50
        )

        self.assertEqual(
            result["status"],
            "WARNING"
        )

    @patch("ticket_workflow.is_working_day", return_value=True)
    def test_sla_breached(self, mock_working_day):
        result = task3.calculate_sla(
            "Critical",
            60
        )

        self.assertEqual(
            result["allowed_minutes"],
            60
        )

        self.assertEqual(
            result["working_minutes"],
            60
        )

        self.assertEqual(
            result["status"],
            "BREACHED"
        )

    # -------------------------------
    # Escalation Tests
    # -------------------------------

    def test_escalation_when_breached(self):
        result = task3.check_escalation(
            "BREACHED"
        )

        self.assertEqual(
            result,
            "Escalated"
        )

    def test_no_escalation_when_not_breached(self):
        result = task3.check_escalation(
            "ON TIME"
        )

        self.assertEqual(
            result,
            "Not Escalated"
        )

    # -------------------------------
    # Routing Tests
    # -------------------------------

    @patch(
        "ticket_workflow.is_business_hours",
        return_value=True
    )
    def test_route_ticket_to_available_agent(
        self,
        mock_business_hours
    ):
        result = task3.route_ticket(
            "technical"
        )

        self.assertEqual(
            result,
            "Agent A"
        )

    @patch(
        "ticket_workflow.is_business_hours",
        return_value=True
    )
    def test_route_ticket_no_available_agent(
        self,
        mock_business_hours
    ):
        original_availability = [
            agent["available"]
            for agent in task3.AGENTS
        ]

        try:
            for agent in task3.AGENTS:
                agent["available"] = False

            result = task3.route_ticket(
                "technical"
            )

            self.assertEqual(
                result,
                "No available agent"
            )

        finally:
            for index, agent in enumerate(task3.AGENTS):
                agent["available"] = (
                    original_availability[index]
                )

    @patch(
        "ticket_workflow.is_business_hours",
        return_value=False
    )
    def test_route_ticket_after_hours(
        self,
        mock_business_hours
    ):
        result = task3.route_ticket(
            "technical"
        )

        self.assertEqual(
            result,
            "After-hours queue"
        )

    # -------------------------------
    # Duplicate Ticket Tests
    # -------------------------------

    def test_duplicate_ticket(self):
        ticket = {
            "order": "12345",
            "issue": "Keyboard is not working"
        }

        existing_tickets = [
            {
                "order": "12345",
                "issue": "Keyboard is not working"
            }
        ]

        result = task3.is_duplicate_ticket(
            ticket,
            existing_tickets
        )

        self.assertTrue(result)

    def test_non_duplicate_ticket(self):
        ticket = {
            "order": "12345",
            "issue": "Keyboard is not working"
        }

        existing_tickets = [
            {
                "order": "99999",
                "issue": "Mouse is not working"
            }
        ]

        result = task3.is_duplicate_ticket(
            ticket,
            existing_tickets
        )

        self.assertFalse(result)

    # -------------------------------
    # Related Ticket Tests
    # -------------------------------

    def test_related_ticket_same_order(self):
        ticket1 = {
            "order": "12345",
            "product": "Wireless Keyboard"
        }

        ticket2 = {
            "order": "12345",
            "product": "Different Product"
        }

        result = task3.are_related_tickets(
            ticket1,
            ticket2
        )

        self.assertTrue(result)

    def test_related_ticket_same_product(self):
        ticket1 = {
            "order": "12345",
            "product": "Wireless Keyboard"
        }

        ticket2 = {
            "order": "99999",
            "product": "Wireless Keyboard"
        }

        result = task3.are_related_tickets(
            ticket1,
            ticket2
        )

        self.assertTrue(result)

    def test_unrelated_tickets(self):
        ticket1 = {
            "order": "12345",
            "product": "Wireless Keyboard"
        }

        ticket2 = {
            "order": "99999",
            "product": "Laptop Bag"
        }

        result = task3.are_related_tickets(
            ticket1,
            ticket2
        )

        self.assertFalse(result)

    # -------------------------------
    # Handoff Summary Tests
    # -------------------------------

    def test_create_handoff_summary(self):
        ticket = {
            "customer": "Anjali",
            "order": "12345",
            "product": "Wireless Keyboard",
            "issue": "Keyboard not working",
            "evidence": "Invoice",
            "contact": "customer@example.com",
            "priority": "High",
            "sla_status": "WARNING",
            "escalation": "Not Escalated",
            "assigned_agent": "Agent A"
        }

        result = task3.create_handoff_summary(
            ticket
        )

        self.assertEqual(
            result["Customer"],
            "A***"
        )

        self.assertEqual(
            result["Order"],
            "12345"
        )

        self.assertEqual(
            result["Product"],
            "Wireless Keyboard"
        )

        self.assertEqual(
            result["Issue"],
            "Keyboard not working"
        )

        self.assertEqual(
            result["Evidence"],
            "Invoice"
        )

        self.assertEqual(
            result["Contact"],
            "[REDACTED]"
        )

        self.assertEqual(
            result["Priority"],
            "High"
        )

    def test_create_handoff_summary_without_customer(self):
        ticket = {
            "customer": None,
            "order": "12345",
            "product": "Wireless Keyboard",
            "issue": "Keyboard not working",
            "evidence": "Invoice",
            "contact": None,
            "priority": "High",
            "sla_status": "ON TIME",
            "escalation": "Not Escalated",
            "assigned_agent": "Agent A"
        }

        result = task3.create_handoff_summary(
            ticket
        )

        self.assertEqual(
            result["Customer"],
            "[REDACTED]"
        )

        self.assertEqual(
            result["Contact"],
            "[NOT PROVIDED]"
        )

    # -------------------------------
    # SLA Rule Update Tests
    # -------------------------------

    def test_update_sla_rule_valid(self):
        original_value = (
            task3.SLA_RULES["Critical"]
        )

        try:
            result = task3.update_sla_rule(
                "Critical",
                120
            )

            self.assertTrue(result)

            self.assertEqual(
                task3.SLA_RULES["Critical"],
                120
            )

        finally:
            task3.SLA_RULES["Critical"] = (
                original_value
            )

    def test_update_sla_rule_invalid_priority(self):
        result = task3.update_sla_rule(
            "Unknown",
            120
        )

        self.assertFalse(result)

    def test_update_sla_rule_invalid_minutes(self):
        original_value = (
            task3.SLA_RULES["Critical"]
        )

        try:
            result = task3.update_sla_rule(
                "Critical",
                0
            )

            self.assertFalse(result)

            self.assertEqual(
                task3.SLA_RULES["Critical"],
                original_value
            )

        finally:
            task3.SLA_RULES["Critical"] = (
                original_value
            )

    # -------------------------------
    # Support Ticket Creation Tests
    # -------------------------------

    @patch(
        "ticket_workflow.route_ticket",
        return_value="Agent A"
    )
    @patch("ticket_workflow.calculate_sla")
    def test_create_support_ticket(
        self,
        mock_calculate_sla,
        mock_route
    ):

        mock_calculate_sla.return_value = {
            "allowed_minutes": 60,
            "warning_minutes": 45,
            "working_minutes": 30,
            "status": "ON TIME"
        }

        conversation = """
        Customer: Anjali
        Order ID: 12345
        Product: Wireless Keyboard
        Issue: Keyboard is not working
        Evidence: Invoice and product image
        Email: customer@example.com
        """

        with patch("builtins.print"):
            ticket = task3.create_support_ticket(
                conversation
            )

        self.assertEqual(
            ticket["customer"],
            "Anjali"
        )

        self.assertEqual(
            ticket["order"],
            "12345"
        )

        self.assertEqual(
            ticket["product"],
            "Wireless Keyboard"
        )

        self.assertEqual(
            ticket["issue"],
            "Keyboard is not working"
        )

        self.assertEqual(
            ticket["evidence"],
            "Invoice and product image"
        )

        self.assertEqual(
            ticket["contact"],
            "customer@example.com"
        )

        self.assertEqual(
            ticket["sla_status"],
            "ON TIME"
        )

        self.assertEqual(
            ticket["assigned_agent"],
            "Agent A"
        )

    @patch(
        "ticket_workflow.route_ticket",
        return_value="Agent A"
    )
    @patch("ticket_workflow.calculate_sla")
    def test_support_ticket_missing_information(
        self,
        mock_calculate_sla,
        mock_route
    ):

        mock_calculate_sla.return_value = {
            "allowed_minutes": 60,
            "warning_minutes": 45,
            "working_minutes": 30,
            "status": "ON TIME"
        }

        conversation = """
        Customer: Anjali
        Order ID: 12345
        Product: Wireless Keyboard
        """

        with patch("builtins.print"):
            ticket = task3.create_support_ticket(
                conversation
            )

        self.assertEqual(
            ticket["customer"],
            "Anjali"
        )

        self.assertEqual(
            ticket["order"],
            "12345"
        )

        self.assertEqual(
            ticket["product"],
            "Wireless Keyboard"
        )

        self.assertIsNone(
            ticket["issue"]
        )

        self.assertIsNone(
            ticket["evidence"]
        )

        self.assertIsNone(
            ticket["contact"]
        )

    # -------------------------------
    # Business Hours Tests
    # -------------------------------

    @patch("ticket_workflow.datetime")
    def test_business_hours_inside_hours(
        self,
        mock_datetime
    ):
        mock_datetime.now.return_value.hour = 12

        result = task3.is_business_hours()

        self.assertTrue(result)

    @patch("ticket_workflow.datetime")
    def test_business_hours_outside_hours(
        self,
        mock_datetime
    ):
        mock_datetime.now.return_value.hour = 20

        result = task3.is_business_hours()

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
import re
from datetime import datetime, timedelta


# -----------------------------
# SLA CONFIGURATION
# -----------------------------

SLA_RULES = {
    "Low": 480,
    "Medium": 240,
    "High": 120,
    "Critical": 60
}

WORKING_DAYS = {0, 1, 2, 3, 4}  # Monday to Friday

HOLIDAYS = {
    "2026-09-10",
    "2026-12-25"
}

BUSINESS_START = 9
BUSINESS_END = 18


# -----------------------------
# AGENT CONFIGURATION
# -----------------------------

AGENTS = [
    {
        "name": "Agent A",
        "skills": ["technical", "billing"],
        "available": True,
        "workload": 2
    },
    {
        "name": "Agent B",
        "skills": ["technical"],
        "available": False,
        "workload": 1
    },
    {
        "name": "Agent C",
        "skills": ["general", "billing"],
        "available": True,
        "workload": 4
    }
]


# -----------------------------
# PRIORITY CALCULATION
# -----------------------------

def calculate_priority(
    severity,
    sentiment,
    waiting_minutes,
    customer_impact
):
    """Calculate ticket priority."""

    score = 0

    severity_scores = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }

    sentiment_scores = {
        "positive": 0,
        "neutral": 1,
        "negative": 2,
        "angry": 3
    }

    impact_scores = {
        "low": 1,
        "medium": 2,
        "high": 3
    }

    score += severity_scores.get(
        severity.lower(), 1
    )

    score += sentiment_scores.get(
        sentiment.lower(), 1
    )

    score += impact_scores.get(
        customer_impact.lower(), 1
    )

    if waiting_minutes >= 120:
        score += 2
    elif waiting_minutes >= 60:
        score += 1

    if score >= 9:
        return "Critical"
    elif score >= 7:
        return "High"
    elif score >= 4:
        return "Medium"
    else:
        return "Low"


# -----------------------------
# SLA FUNCTIONS
# -----------------------------

def is_working_day(date):
    """Check whether a date is a configured working day."""

    date_string = date.strftime("%Y-%m-%d")

    return (
        date.weekday() in WORKING_DAYS
        and date_string not in HOLIDAYS
    )


def calculate_sla(priority, waiting_minutes):
    """Calculate SLA using only working days."""

    allowed_minutes = SLA_RULES.get(
        priority,
        240
    )

    working_minutes = 0
    current_date = datetime.now()

    for _ in range(waiting_minutes):

        if is_working_day(current_date):
            working_minutes += 1

        current_date = current_date + timedelta(minutes=1)

    warning_minutes = allowed_minutes * 0.75

    if working_minutes >= allowed_minutes:
        status = "BREACHED"
    elif working_minutes >= warning_minutes:
        status = "WARNING"
    else:
        status = "ON TIME"

    return {
        "allowed_minutes": allowed_minutes,
        "warning_minutes": warning_minutes,
        "working_minutes": working_minutes,
        "status": status
    }


def check_escalation(sla_status):
    """Escalate the ticket if the SLA is breached."""

    if sla_status == "BREACHED":
        return "Escalated"

    return "Not Escalated"


# -----------------------------
# ROUTING FUNCTIONS
# -----------------------------

def is_business_hours():
    """Check whether the current time is within business hours."""

    current_hour = datetime.now().hour

    return (
        BUSINESS_START <= current_hour < BUSINESS_END
    )


def route_ticket(issue_type):
    """Route ticket to the best available agent."""

    if not is_business_hours():
        return "After-hours queue"

    suitable_agents = [
        agent
        for agent in AGENTS
        if issue_type.lower() in agent["skills"]
        and agent["available"]
    ]

    if not suitable_agents:
        return "No available agent"

    best_agent = min(
        suitable_agents,
        key=lambda agent: agent["workload"]
    )

    return best_agent["name"]


# -----------------------------
# DUPLICATE / RELATED TICKETS
# -----------------------------

def is_duplicate_ticket(ticket, existing_tickets):
    """Check whether a ticket is a duplicate."""

    for existing in existing_tickets:

        if (
            ticket["order"] == existing["order"]
            and ticket["issue"] == existing["issue"]
        ):
            return True

    return False


def are_related_tickets(ticket1, ticket2):
    """Check whether two tickets are related."""

    if ticket1["order"] == ticket2["order"]:
        return True

    if ticket1["product"] == ticket2["product"]:
        return True

    return False


# -----------------------------
# MASKED HANDOFF SUMMARY
# -----------------------------

def create_handoff_summary(ticket):
    """Create a masked summary for another agent."""

    customer = ticket["customer"]

    if customer:
        masked_customer = customer[0] + "***"
    else:
        masked_customer = "[REDACTED]"

    contact = ticket["contact"]

    if contact:
        masked_contact = "[REDACTED]"
    else:
        masked_contact = "[NOT PROVIDED]"

    summary = {
        "Customer": masked_customer,
        "Order": ticket["order"],
        "Product": ticket["product"],
        "Issue": ticket["issue"],
        "Evidence": ticket["evidence"],
        "Contact": masked_contact,
        "Priority": ticket["priority"],
        "SLA Status": ticket["sla_status"],
        "Escalation": ticket["escalation"],
        "Assigned Agent": ticket["assigned_agent"]
    }

    return summary


# -----------------------------
# RUNTIME SLA UPDATE
# -----------------------------

def update_sla_rule(priority, new_minutes):
    """Update SLA rules while the program is running."""

    if priority in SLA_RULES and new_minutes > 0:
        SLA_RULES[priority] = new_minutes

        print(
            f"{priority} SLA updated to {new_minutes} minutes."
        )

        return True

    print("Invalid SLA update.")
    return False


# -----------------------------
# CREATE SUPPORT TICKET
# -----------------------------

def create_support_ticket(conversation):
    """Convert an unresolved conversation into a structured ticket."""

    ticket = {
        "customer": None,
        "order": None,
        "product": None,
        "issue": None,
        "evidence": None,
        "contact": None,
        "severity": "high",
        "sentiment": "negative",
        "waiting_minutes": 90,
        "customer_impact": "high",
        "priority": None
    }

    customer_match = re.search(
        r"customer\s*:\s*(.+)",
        conversation,
        re.IGNORECASE
    )

    order_match = re.search(
        r"order\s*(?:id)?\s*:\s*([A-Za-z0-9-]+)",
        conversation,
        re.IGNORECASE
    )

    product_match = re.search(
        r"product\s*:\s*(.+)",
        conversation,
        re.IGNORECASE
    )

    issue_match = re.search(
        r"issue\s*:\s*(.+)",
        conversation,
        re.IGNORECASE
    )

    evidence_match = re.search(
        r"evidence\s*:\s*(.+)",
        conversation,
        re.IGNORECASE
    )

    contact_match = re.search(
        r"(?:email|phone|contact)\s*:\s*(.+)",
        conversation,
        re.IGNORECASE
    )

    if customer_match:
        ticket["customer"] = customer_match.group(1).strip()

    if order_match:
        ticket["order"] = order_match.group(1).strip()

    if product_match:
        ticket["product"] = product_match.group(1).strip()

    if issue_match:
        ticket["issue"] = issue_match.group(1).strip()

    if evidence_match:
        ticket["evidence"] = evidence_match.group(1).strip()

    if contact_match:
        ticket["contact"] = contact_match.group(1).strip()

    mandatory_fields = [
        "customer",
        "order",
        "product",
        "issue",
        "evidence",
        "contact"
    ]

    missing = [
        field
        for field in mandatory_fields
        if ticket[field] is None
    ]

    # Priority
    ticket["priority"] = calculate_priority(
        ticket["severity"],
        ticket["sentiment"],
        ticket["waiting_minutes"],
        ticket["customer_impact"]
    )

    # SLA
    sla = calculate_sla(
        ticket["priority"],
        ticket["waiting_minutes"]
    )

    ticket["sla_status"] = sla["status"]

    ticket["escalation"] = check_escalation(
        ticket["sla_status"]
    )

    # Agent routing
    ticket["assigned_agent"] = route_ticket(
        "technical"
    )

    ticket["sla_allowed_minutes"] = (
        sla["allowed_minutes"]
    )

    ticket["sla_warning_minutes"] = (
        sla["warning_minutes"]
    )

    ticket["sla_working_minutes"] = (
        sla["working_minutes"]
    )

    # Display ticket
    print("\n--- Support Ticket ---")

    for field, value in ticket.items():
        print(f"{field.title()}: {value}")

    if missing:
        print("\nMissing mandatory information:")
        print(", ".join(missing))
        print("Please provide the missing information.")
    else:
        print("\nTicket is complete.")

    return ticket


# -----------------------------
# MAIN PROGRAM
# -----------------------------

if __name__ == "__main__":

    conversation = """
    Customer: Anjali
    Order ID: 12345
    Product: Wireless Keyboard
    Issue: Keyboard is not working
    Evidence: Invoice and product image
    Email: customer@example.com
    """

    ticket = create_support_ticket(
        conversation
    )

    # Duplicate test
    existing_tickets = [
        {
            "order": "12345",
            "issue": "Keyboard is not working"
        }
    ]

    if is_duplicate_ticket(
        ticket,
        existing_tickets
    ):
        print("\nDuplicate ticket detected.")
    else:
        print("\nNo duplicate ticket detected.")

    # Related ticket test
    related_ticket = {
        "order": "99999",
        "product": "Wireless Keyboard",
        "issue": "Keyboard keys are stuck"
    }

    # Unrelated ticket test
    unrelated_ticket = {
        "order": "88888",
        "product": "Laptop Bag",
        "issue": "Bag zipper is damaged"
    }

    if are_related_tickets(
        ticket,
        related_ticket
    ):
        print("Related ticket detected.")
    else:
        print("Unrelated ticket detected.")

    if are_related_tickets(
        ticket,
        unrelated_ticket
    ):
        print("Related ticket detected.")
    else:
        print("Unrelated ticket detected.")

    # Runtime SLA update test
    print("\n--- Runtime SLA Update ---")

    update_sla_rule("Critical", 120)

    updated_sla = calculate_sla(
        ticket["priority"],
        ticket["waiting_minutes"]
    )

    ticket["sla_status"] = updated_sla["status"]

    ticket["escalation"] = check_escalation(
        ticket["sla_status"]
    )

    print(
        "Updated Critical SLA:",
        SLA_RULES["Critical"],
        "minutes"
    )

    print(
        "Updated SLA Status:",
        ticket["sla_status"]
    )

    print(
        "Updated Escalation:",
        ticket["escalation"]
    )


    # Masked handoff summary
    handoff = create_handoff_summary(
        ticket
    )

    print("\n--- Masked Handoff Summary ---")

    for field, value in handoff.items():
        print(f"{field}: {value}")

    # -----------------------------
    # FINAL EVALUATION TESTS
    # -----------------------------

    print("\n--- No Available Agent Test ---")

    original_availability = []

    for agent in AGENTS:
        original_availability.append(agent["available"])
        agent["available"] = False

    no_agent_result = route_ticket("technical")

    print("Routing result:", no_agent_result)

    # Restore original availability
    for index, agent in enumerate(AGENTS):
        agent["available"] = original_availability[index]


    print("\n--- After-Hours Test ---")

    original_start = BUSINESS_START
    original_end = BUSINESS_END

    # Temporarily change business hours
    # so the current time is outside them
    BUSINESS_START = 0
    BUSINESS_END = 0

    after_hours_result = route_ticket("technical")

    print("Routing result:", after_hours_result)

    # Restore original business hours
    BUSINESS_START = original_start
    BUSINESS_END = original_end
import unittest
import sentiment_escalation as se


class TestTask5SentimentEscalation(unittest.TestCase):

    # 1. Test English language detection
    def test_english_language(self):
        result = se.detect_language("My keyboard is not working.")
        self.assertEqual(result, "English")

    # 2. Test Spanish language detection
    def test_spanish_language(self):
        result = se.detect_language("Hola, tengo un problema.")
        self.assertEqual(result, "Spanish")

    # 3. Test French language detection
    def test_french_language(self):
        result = se.detect_language("Bonjour, j'ai un problème.")
        self.assertEqual(result, "French")

    # 4. Test Hindi language detection
    def test_hindi_language(self):
        result = se.detect_language("नमस्ते, मुझे समस्या है.")
        self.assertEqual(result, "Hindi")

    # 5. Test positive sentiment
    def test_positive_sentiment(self):
        result = se.analyse_sentiment(
            "Thank you, the service was excellent."
        )

        self.assertEqual(result["sentiment"], "Positive")
        self.assertFalse(result["urgent"])
        self.assertFalse(result["frustrated"])

    # 6. Test negative sentiment
    def test_negative_sentiment(self):
        result = se.analyse_sentiment(
            "My keyboard is bad and there is a problem."
        )

        self.assertEqual(result["sentiment"], "Negative")

    # 7. Test frustrated sentiment
    def test_frustrated_sentiment(self):
        result = se.analyse_sentiment(
            "I am frustrated and this is unacceptable."
        )

        self.assertEqual(result["sentiment"], "Frustrated")
        self.assertTrue(result["frustrated"])

    # 8. Test urgent message
    def test_urgent_message(self):
        result = se.analyse_sentiment(
            "This is urgent. Please fix it immediately."
        )

        self.assertTrue(result["urgent"])

    # 9. Test sarcastic sentiment
    def test_sarcastic_sentiment(self):
        result = se.analyse_sentiment(
            "Great job, my keyboard is still not working."
        )

        self.assertEqual(result["sentiment"], "Sarcastic")
        self.assertTrue(result["sarcastic"])

    # 10. Test neutral sentiment
    def test_neutral_sentiment(self):
        result = se.analyse_sentiment(
            "I would like information about my order."
        )

        self.assertEqual(result["sentiment"], "Neutral")

    # 11. Test confidence score
    def test_confidence_score(self):
        result = se.analyse_sentiment(
            "This is terrible and urgent."
        )

        self.assertGreaterEqual(result["confidence"], 0.50)
        self.assertLessEqual(result["confidence"], 0.95)

    # 12. Test repeated negative messages
    def test_repeated_negative_messages(self):
        history = [
            "My keyboard is not working.",
            "There is a problem with my keyboard.",
            "This is still not fixed."
        ]

        result = se.analyse_sentiment(
            "Please help me.",
            history
        )

        self.assertTrue(result["repeated_negative"])

    # 13. Test no repeated negative messages
    def test_no_repeated_negative_messages(self):
        history = [
            "Thank you for the help.",
            "I received my order."
        ]

        result = se.analyse_sentiment(
            "I need some information."
            , history
        )

        self.assertFalse(result["repeated_negative"])

    # 14. Test duplicate payment detection
    def test_duplicate_payment_detection(self):
        risks = se.detect_high_risk_issue(
            "I was charged twice for the same order."
        )

        self.assertIn("Duplicate payment", risks)

    # 15. Test account compromise detection
    def test_account_compromise_detection(self):
        risks = se.detect_high_risk_issue(
            "Someone else accessed my account."
        )

        self.assertIn("Account compromise", risks)

    # 16. Test legal threat detection
    def test_legal_threat_detection(self):
        risks = se.detect_high_risk_issue(
            "I will take legal action if this is not resolved."
        )

        self.assertIn("Legal threat", risks)

    # 17. Test no high-risk issue
    def test_no_high_risk_issue(self):
        risks = se.detect_high_risk_issue(
            "My keyboard is not working."
        )

        self.assertEqual(risks, [])

    # 18. Test escalation for high-risk issue
    def test_high_risk_escalation(self):
        sentiment = se.analyse_sentiment(
            "Someone else accessed my account."
        )

        risks = se.detect_high_risk_issue(
            "Someone else accessed my account."
        )

        escalations = se.check_escalation(
            sentiment,
            risks,
            5,
            "Customer reports possible account compromise."
        )

        self.assertGreaterEqual(len(escalations), 1)
        self.assertEqual(
            escalations[0]["reason"],
            "Account compromise"
        )

    # 19. Test escalation for repeated negative messages
    def test_repeated_negative_escalation(self):
        history = [
            "My keyboard is not working.",
            "This problem is still not fixed.",
            "The issue is wrong again."
        ]

        sentiment = se.analyse_sentiment(
            "Please help me.",
            history
        )

        escalations = se.check_escalation(
            sentiment,
            [],
            5,
            "Customer has repeatedly reported a problem."
        )

        reasons = [
            escalation["reason"]
            for escalation in escalations
        ]

        self.assertIn(
            "Repeated negative messages",
            reasons
        )

    # 20. Test negative conversation over 15 minutes
    def test_negative_conversation_time_escalation(self):
        sentiment = se.analyse_sentiment(
            "This problem is still not working."
        )

        escalations = se.check_escalation(
            sentiment,
            [],
            20,
            "Customer has an unresolved negative conversation."
        )

        reasons = [
            escalation["reason"]
            for escalation in escalations
        ]

        self.assertIn(
            "Negative conversation unresolved",
            reasons
        )

    # 21. Test no time escalation under 15 minutes
    def test_no_negative_time_escalation_under_limit(self):
        sentiment = se.analyse_sentiment(
            "My keyboard is not working."
        )

        escalations = se.check_escalation(
            sentiment,
            [],
            10,
            "Customer reports a keyboard problem."
        )

        reasons = [
            escalation["reason"]
            for escalation in escalations
        ]

        self.assertNotIn(
            "Negative conversation unresolved",
            reasons
        )

    # 22. Test escalation record structure
    def test_escalation_record(self):
        escalation = se.create_escalation(
            "Test reason",
            "Test condition",
            "Test conversation"
        )

        self.assertEqual(
            escalation["reason"],
            "Test reason"
        )
        self.assertEqual(
            escalation["activated_condition"],
            "Test condition"
        )
        self.assertEqual(
            escalation["conversation_summary"],
            "Test conversation"
        )

    # 23. Test after-hours urgent routing
    def test_after_hours_urgent_routing(self):
        route = se.route_complaint(
            "This is urgent. Please help immediately.",
            current_hour=22
        )

        self.assertEqual(route, "On-call queue")

    # 24. Test after-hours normal routing
    def test_after_hours_normal_routing(self):
        route = se.route_complaint(
            "My keyboard is not working.",
            current_hour=22
        )

        self.assertEqual(route, "Next working day")

    # 25. Test business-hours routing
    def test_business_hours_routing(self):
        route = se.route_complaint(
            "My keyboard is not working.",
            current_hour=10
        )

        self.assertEqual(route, "Normal support queue")

    # 26. Test urgent message during business hours
    def test_urgent_business_hours_routing(self):
        route = se.route_complaint(
            "This is urgent. Please help immediately.",
            current_hour=10
        )

        self.assertEqual(route, "Normal support queue")

    # 27. Test calm high-risk issue
    def test_calm_high_risk_issue(self):
        message = (
            "I noticed that my account was accessed "
            "by someone else."
        )

        sentiment = se.analyse_sentiment(message)
        risks = se.detect_high_risk_issue(message)

        escalations = se.check_escalation(
            sentiment,
            risks,
            5,
            "Customer calmly reports possible account compromise."
        )

        self.assertEqual(sentiment["sentiment"], "Neutral")
        self.assertIn("Account compromise", risks)
        self.assertGreaterEqual(len(escalations), 1)

    # 28. Test empty message
    def test_empty_message(self):
        result = se.analyse_sentiment("")

        self.assertEqual(result["sentiment"], "Neutral")
        self.assertEqual(result["language"], "English")
        self.assertFalse(result["urgent"])
        self.assertFalse(result["frustrated"])
        self.assertFalse(result["sarcastic"])


if __name__ == "__main__":
    unittest.main()

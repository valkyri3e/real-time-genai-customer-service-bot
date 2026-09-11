import unittest
from datetime import datetime, timedelta

import multilingual_sessions as ms


class TestTask6MultilingualSessions(unittest.TestCase):

    # 1. English language detection
    def test_english_language(self):
        result = ms.detect_language(
            "Hello, my keyboard is not working."
        )

        self.assertEqual(result["language"], "English")
        self.assertGreaterEqual(result["confidence"], 0.60)

    # 2. Spanish language detection
    def test_spanish_language(self):
        result = ms.detect_language(
            "Hola, mi teclado no funciona."
        )

        self.assertEqual(result["language"], "Spanish")
        self.assertGreaterEqual(result["confidence"], 0.60)

    # 3. French language detection
    def test_french_language(self):
        result = ms.detect_language(
            "Bonjour, mon clavier ne fonctionne pas."
        )

        self.assertEqual(result["language"], "French")
        self.assertGreaterEqual(result["confidence"], 0.60)

    # 4. Hindi language detection
    def test_hindi_language(self):
        result = ms.detect_language(
            "नमस्ते, मेरा कीबोर्ड काम नहीं कर रहा है।"
        )

        self.assertEqual(result["language"], "Hindi")
        self.assertGreaterEqual(result["confidence"], 0.60)

    # 5. Transliterated Hindi detection
    def test_transliterated_hindi(self):
        result = ms.detect_language(
            "Mera keyboard kaam nahi kar raha"
        )

        self.assertEqual(result["language"], "Hindi")
        self.assertGreaterEqual(result["confidence"], 0.60)

    # 6. Unknown language
    def test_unknown_language(self):
        result = ms.detect_language(
            "xyz abc qwerty"
        )

        self.assertEqual(result["language"], "Unknown")
        self.assertEqual(result["confidence"], 0.0)

    # 7. Detect multiple languages
    def test_mixed_language_detection(self):
        result = ms.detect_languages(
            "Hello, mi teclado no funciona."
        )

        self.assertIn("English", result)
        self.assertIn("Spanish", result)

    # 8. Mixed-language conversation detection
    def test_mixed_language_conversation(self):
        result = ms.update_conversation_language(
            "Hello, mi teclado no funciona."
        )

        self.assertTrue(result["mixed_language"])
        self.assertIn("English", result["languages_detected"])
        self.assertIn("Spanish", result["languages_detected"])

    # 9. Language switching
    def test_language_switching(self):
        result1 = ms.update_conversation_language(
            "Hello, my keyboard is not working.",
            "English"
        )

        self.assertEqual(result1["language"], "English")

        result2 = ms.update_conversation_language(
            "Hola, mi teclado no funciona.",
            result1["language"]
        )

        self.assertEqual(result2["language"], "Spanish")

        result3 = ms.update_conversation_language(
            "Bonjour, mon clavier ne fonctionne pas.",
            result2["language"]
        )

        self.assertEqual(result3["language"], "French")

    # 10. No language detected
    def test_no_language_detected(self):
        result = ms.update_conversation_language(
            "xyz abc"
        )

        self.assertEqual(result["language"], "Unknown")
        self.assertFalse(result["mixed_language"])

    # 11. Extract order ID
    def test_extract_order_id(self):
        details = ms.extract_customer_details(
            "My order is ORD12345."
        )

        self.assertEqual(details["order_id"], "ORD12345")

    # 12. Extract product code
    def test_extract_product_code(self):
        details = ms.extract_customer_details(
            "The product code is KB-100."
        )

        self.assertEqual(details["product_code"], "KB-100")

    # 13. Extract date
    def test_extract_date(self):
        details = ms.extract_customer_details(
            "The order was placed on 2026-09-07."
        )

        self.assertEqual(details["date"], "2026-09-07")

    # 14. Extract multiple customer details
    def test_extract_multiple_details(self):
        details = ms.extract_customer_details(
            "My order is ORD12345, product KB-100, "
            "placed on 2026-09-07."
        )

        self.assertEqual(details["order_id"], "ORD12345")
        self.assertEqual(details["product_code"], "KB-100")
        self.assertEqual(details["date"], "2026-09-07")

    # 15. Context preservation
    def test_context_preservation(self):
        context = {
            "messages": [],
            "order_id": None,
            "product_code": None,
            "date": None
        }

        messages = [
            "My order is ORD12345.",
            "The product code is KB-100.",
            "The order was placed on 2026-09-07."
        ]

        for message in messages:
            context = ms.update_context(
                context,
                message
            )

        self.assertEqual(context["order_id"], "ORD12345")
        self.assertEqual(context["product_code"], "KB-100")
        self.assertEqual(context["date"], "2026-09-07")
        self.assertEqual(len(context["messages"]), 3)

    # 16. Context limited to latest 10 messages
    def test_context_message_limit(self):
        context = {
            "messages": [],
            "order_id": None,
            "product_code": None,
            "date": None
        }

        for number in range(1, 13):
            ms.update_context(
                context,
                "Test message " + str(number)
            )

        self.assertEqual(
            len(context["messages"]),
            ms.MAX_CONTEXT_MESSAGES
        )

        self.assertEqual(
            context["messages"][0],
            "Test message 3"
        )

        self.assertEqual(
            context["messages"][-1],
            "Test message 12"
        )

    # 17. Corrected order information
    def test_corrected_order_information(self):
        context = {
            "messages": [],
            "order_id": "ORD12345",
            "product_code": "KB-100",
            "date": "2026-09-07"
        }

        context = ms.update_corrected_information(
            context,
            "Actually, the correct order is ORD12346."
        )

        self.assertEqual(
            context["order_id"],
            "ORD12346"
        )

    # 18. Corrected product information
    def test_corrected_product_information(self):
        context = {
            "messages": [],
            "order_id": "ORD12345",
            "product_code": "KB-100",
            "date": "2026-09-07"
        }

        context = ms.update_corrected_information(
            context,
            "Actually, the correct product is KB-200."
        )

        self.assertEqual(
            context["product_code"],
            "KB-200"
        )

    # 19. Spelling correction
    def test_spelling_correction(self):
        corrected = ms.correct_spelling(
            "My keybord is not working."
        )

        self.assertEqual(
            corrected,
            "My keyboard is not working."
        )

    # 20. Multiple spelling corrections
    def test_multiple_spelling_corrections(self):
        corrected = ms.correct_spelling(
            "My keybord has a refnd and paymant problem."
        )

        self.assertIn("keyboard", corrected.lower())
        self.assertIn("refund", corrected.lower())
        self.assertIn("payment", corrected.lower())

    # 21. Technical support intent
    def test_technical_support_intent(self):
        result = ms.detect_intent(
            "My keyboard is not working."
        )

        self.assertEqual(
            result["intent"],
            "Technical support"
        )

        self.assertFalse(
            result["needs_clarification"]
        )

    # 22. Refund intent
    def test_refund_intent(self):
        result = ms.detect_intent(
            "I want a refund."
        )

        self.assertEqual(
            result["intent"],
            "Refund"
        )

        self.assertFalse(
            result["needs_clarification"]
        )

    # 23. Order status intent
    def test_order_status_intent(self):
        result = ms.detect_intent(
            "Where is my order?"
        )

        self.assertEqual(
            result["intent"],
            "Order status"
        )

        self.assertFalse(
            result["needs_clarification"]
        )

    # 24. Product information intent
    def test_product_information_intent(self):
        result = ms.detect_intent(
            "Tell me about the product features."
        )

        self.assertEqual(
            result["intent"],
            "Product information"
        )

        self.assertFalse(
            result["needs_clarification"]
        )

    # 25. Unknown intent
    def test_unknown_intent(self):
        result = ms.detect_intent(
            "I need help with something."
        )

        self.assertEqual(
            result["intent"],
            "Unknown"
        )

        self.assertTrue(
            result["needs_clarification"]
        )

    # 26. Low-confidence clarification
    def test_clarification_required(self):
        result = ms.check_clarification(
            "xyz abc"
        )

        self.assertTrue(
            result["needs_clarification"]
        )

    # 27. Clear request does not require clarification
    def test_no_clarification_for_clear_request(self):
        result = ms.check_clarification(
            "My keyboard is not working."
        )

        self.assertFalse(
            result["needs_clarification"]
        )

    # 28. Customer session creation
    def test_customer_session_creation(self):
        session = ms.CustomerSession(
            "CUSTOMER_001"
        )

        self.assertEqual(
            session.customer_id,
            "CUSTOMER_001"
        )

        self.assertEqual(
            session.messages,
            []
        )

        self.assertTrue(
            session.active
        )

    # 29. Add message to customer session
    def test_add_message_to_session(self):
        session = ms.CustomerSession(
            "CUSTOMER_001"
        )

        session.add_message(
            "My order is ORD12345."
        )

        self.assertEqual(
            len(session.messages),
            1
        )

        self.assertEqual(
            session.messages[0],
            "My order is ORD12345."
        )

        self.assertTrue(
            session.active
        )

    # 30. Session keeps latest 10 messages
    def test_session_message_limit(self):
        session = ms.CustomerSession(
            "CUSTOMER_001"
        )

        for number in range(1, 13):
            session.add_message(
                "Message " + str(number)
            )

        self.assertEqual(
            len(session.messages),
            10
        )

        self.assertEqual(
            session.messages[0],
            "Message 3"
        )

        self.assertEqual(
            session.messages[-1],
            "Message 12"
        )

    # 31. Session summary
    def test_session_summary(self):
        session = ms.CustomerSession(
            "CUSTOMER_001"
        )

        session.add_message("Hello")
        session.add_message("My order is ORD12345.")
        session.add_message("My keyboard is not working.")

        summary = session.create_summary()

        self.assertIn(
            "Customer discussed:",
            summary
        )

        self.assertIn(
            "ORD12345",
            summary
        )

    # 32. Empty session summary
    def test_empty_session_summary(self):
        session = ms.CustomerSession(
            "CUSTOMER_001"
        )

        summary = session.create_summary()

        self.assertEqual(
            summary,
            "No conversation history."
        )

    # 33. Session manager creates new session
    def test_session_manager_new_session(self):
        manager = ms.SessionManager()

        session = manager.get_session(
            "CUSTOMER_001"
        )

        self.assertEqual(
            session.customer_id,
            "CUSTOMER_001"
        )

        self.assertIn(
            "CUSTOMER_001",
            manager.sessions
        )

    # 34. Session manager returns existing session
    def test_existing_session_returned(self):
        manager = ms.SessionManager()

        session1 = manager.get_session(
            "CUSTOMER_001"
        )

        session1.add_message(
            "My order is ORD12345."
        )

        session2 = manager.get_session(
            "CUSTOMER_001"
        )

        self.assertIs(
            session1,
            session2
        )

        self.assertEqual(
            len(session2.messages),
            1
        )

    # 35. Session isolation
    def test_session_isolation(self):
        manager = ms.SessionManager()

        customer_a = manager.get_session(
            "CUSTOMER_A"
        )

        customer_b = manager.get_session(
            "CUSTOMER_B"
        )

        customer_a.add_message(
            "My order is ORD11111."
        )

        customer_b.add_message(
            "My order is ORD22222."
        )

        self.assertNotEqual(
            customer_a.messages,
            customer_b.messages
        )

        self.assertNotIn(
            "My order is ORD22222.",
            customer_a.messages
        )

        self.assertNotIn(
            "My order is ORD11111.",
            customer_b.messages
        )

    # 36. Session expiry and restoration
    def test_session_expiry_and_restoration(self):
        manager = ms.SessionManager()

        session = manager.get_session(
            "CUSTOMER_001"
        )

        session.add_message(
            "My order is ORD12345."
        )

        session.last_activity = (
            datetime.now()
            - timedelta(
                minutes=ms.SESSION_INACTIVITY_MINUTES + 1
            )
        )

        restored_session = manager.get_session(
            "CUSTOMER_001"
        )

        self.assertEqual(
            restored_session.customer_id,
            "CUSTOMER_001"
        )

        self.assertNotEqual(
            restored_session.summary,
            ""
        )

    # 37. Session restoration within 24 hours
    def test_session_restoration_within_24_hours(self):
        manager = ms.SessionManager()

        session = manager.get_session(
            "CUSTOMER_001"
        )

        session.add_message(
            "My order is ORD12345."
        )

        session.last_activity = (
            datetime.now()
            - timedelta(
                minutes=ms.SESSION_INACTIVITY_MINUTES + 1
            )
        )

        manager.get_session(
            "CUSTOMER_001"
        )

        manager.closed_sessions[
            "CUSTOMER_001"
        ]["closed_at"] = (
            datetime.now()
            - timedelta(hours=2)
        )

        restored_session = manager.get_session(
            "CUSTOMER_001"
        )

        self.assertNotEqual(
            restored_session.summary,
            ""
        )

        self.assertIn(
            "CUSTOMER_001",
            manager.sessions
        )
    # 38. New session after 24 hours
    def test_new_session_after_24_hours(self):
        manager = ms.SessionManager()

        session = manager.get_session(
            "CUSTOMER_001"
        )

        session.add_message(
            "My order is ORD12345."
        )

        session.last_activity = (
            datetime.now()
            - timedelta(
                minutes=ms.SESSION_INACTIVITY_MINUTES + 1
            )
        )

        manager.get_session(
            "CUSTOMER_001"
        )

        manager.sessions.pop(
            "CUSTOMER_001",
            None
        )

        manager.closed_sessions[
            "CUSTOMER_001"
        ]["closed_at"] = (
            datetime.now()
            - timedelta(hours=25)
        )

        new_session = manager.get_session(
            "CUSTOMER_001"
        )

        self.assertEqual(
            new_session.summary,
            ""
        )

        self.assertEqual(
            new_session.messages,
            []
        )

    # 39. Corrected information replaces old order
    def test_corrected_order_replaces_old_order(self):
        context = {
            "messages": [],
            "order_id": "ORD55555",
            "product_code": "KB-200",
            "date": "2026-09-07"
        }

        updated_context = ms.update_corrected_information(
            context,
            "Actually, the correct order is ORD55556."
        )

        self.assertEqual(
            updated_context["order_id"],
            "ORD55556"
        )

        self.assertNotEqual(
            updated_context["order_id"],
            "ORD55555"
        )

    # 40. Multiple requests can be identified
    def test_multiple_requests(self):
        message = (
            "My keyboard is not working "
            "and I also want a refund."
        )

        detected_intents = []

        for intent, patterns in ms.INTENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in message.lower():
                    detected_intents.append(intent)
                    break

        self.assertIn(
            "Technical support",
            detected_intents
        )

        self.assertIn(
            "Refund",
            detected_intents
        )
        
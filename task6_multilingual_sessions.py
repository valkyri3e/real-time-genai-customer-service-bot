import re
from datetime import datetime, timedelta

# -----------------------------
# CONFIGURATION
# -----------------------------

SUPPORTED_LANGUAGES = [
    "English",
    "Spanish",
    "French",
    "Hindi"
]

LANGUAGE_CONFIDENCE_THRESHOLD = 0.60
INTENT_CONFIDENCE_THRESHOLD = 0.60

MAX_CONTEXT_MESSAGES = 10

SESSION_INACTIVITY_MINUTES = 30
SESSION_RESTORE_HOURS = 24


# -----------------------------
# LANGUAGE DETECTION
# -----------------------------

LANGUAGE_PATTERNS = {
    "English": [
        "hello",
        "please",
        "help",
        "order",
        "keyboard",
        "problem",
        "working",
        "refund"
    ],

    "Spanish": [
        "hola",
        "gracias",
        "ayuda",
        "pedido",
        "problema",
        "teclado",
        "reembolso"
    ],

    "French": [
        "bonjour",
        "merci",
        "aide",
        "commande",
        "problème",
        "clavier",
        "remboursement"
    ],

    "Hindi": [
    "नमस्ते",
    "धन्यवाद",
    "मदद",
    "ऑर्डर",
    "समस्या",
    "कीबोर्ड",
    "रिफंड",

    # Transliterated Hindi
    "mera",
    "meri",
    "mujhe",
    "kaam nahi",
    "kar raha",
    "kar rahi",
    "nahi hai",
    "chahiye",
    "madad chahiye",
    "refund chahiye"
]
}


def detect_language(message):
    """Detect the most likely language and confidence."""

    text = message.lower()

    scores = {}

    for language, patterns in LANGUAGE_PATTERNS.items():

        score = 0

        for pattern in patterns:
            if pattern in text:
                score += 1

        scores[language] = score

    best_language = max(
        scores,
        key=scores.get
    )

    best_score = scores[best_language]

    total_matches = sum(scores.values())

    if total_matches == 0:
        confidence = 0.0
    else:
        confidence = best_score / total_matches

    if confidence < LANGUAGE_CONFIDENCE_THRESHOLD:
        return {
            "language": "Unknown",
            "confidence": round(confidence, 2)
        }

    return {
        "language": best_language,
        "confidence": round(confidence, 2)
    }


# -----------------------------
# LANGUAGE TEST
# -----------------------------

print("\n--- Language Detection Test ---")

test_messages = [
    "Hello, my keyboard is not working.",
    "Hola, mi teclado no funciona.",
    "Bonjour, mon clavier ne fonctionne pas.",
    "नमस्ते, मेरा कीबोर्ड काम नहीं कर रहा है।"
]

for message in test_messages:

    result = detect_language(message)

    print("\nMessage:", message)
    print("Language:", result["language"])
    print("Confidence:", result["confidence"])

    # -----------------------------
# MIXED-LANGUAGE AND LANGUAGE SWITCHING
# -----------------------------

def detect_languages(message):
    """Detect all languages present in a message."""

    text = message.lower()
    detected = []

    for language, patterns in LANGUAGE_PATTERNS.items():

        matches = 0

        for pattern in patterns:
            if pattern in text:
                matches += 1

        if matches > 0:
            detected.append(language)

    return detected


def update_conversation_language(
    message,
    current_language=None
):
    """Update the conversation language when the customer switches language."""

    detected_languages = detect_languages(message)

    if len(detected_languages) == 0:
        return {
            "language": current_language or "Unknown",
            "languages_detected": [],
            "mixed_language": False
        }

    if len(detected_languages) > 1:
        return {
            "language": detected_languages[0],
            "languages_detected": detected_languages,
            "mixed_language": True
        }

    new_language = detected_languages[0]

    return {
        "language": new_language,
        "languages_detected": detected_languages,
        "mixed_language": False
    }


# -----------------------------
# MIXED-LANGUAGE TEST
# -----------------------------

print("\n--- Mixed-Language Test ---")

mixed_message = (
    "Hello, mi teclado no funciona."
)

mixed_result = update_conversation_language(
    mixed_message
)

print("Detected languages:",
      mixed_result["languages_detected"])

print("Mixed language:",
      mixed_result["mixed_language"])


# -----------------------------
# LANGUAGE SWITCHING TEST
# -----------------------------

print("\n--- Language Switching Test ---")

current_language = "English"

message_1 = "Hello, my keyboard is not working."

result_1 = update_conversation_language(
    message_1,
    current_language
)

current_language = result_1["language"]

print("Message 1 language:",
      current_language)


message_2 = "Hola, mi teclado no funciona."

result_2 = update_conversation_language(
    message_2,
    current_language
)

current_language = result_2["language"]

print("Message 2 language:",
      current_language)


message_3 = "Bonjour, mon clavier ne fonctionne pas."

result_3 = update_conversation_language(
    message_3,
    current_language
)

current_language = result_3["language"]

print("Message 3 language:",
      current_language)

# -----------------------------
# EXTRACT AND PRESERVE CONTEXT
# -----------------------------

def extract_customer_details(message):
    """Extract important customer details from a message."""

    details = {}

    # Order ID examples: ORD12345, ORDER-12345
    order_match = re.search(
        r'\b(?:ORD|ORDER)[-_]?\d{3,}\b',
        message,
        re.IGNORECASE
    )

    if order_match:
        details["order_id"] = order_match.group(0)

    # Product code examples: KB-100, PROD-200
    product_match = re.search(
        r'\b(?:KB|PROD|PRD)[-_]?\d{2,}\b',
        message,
        re.IGNORECASE
    )

    if product_match:
        details["product_code"] = product_match.group(0)

    # Date examples: 2026-09-07
    date_match = re.search(
        r'\b\d{4}-\d{2}-\d{2}\b',
        message
    )

    if date_match:
        details["date"] = date_match.group(0)

    return details


def update_context(
    context,
    message
):
    """Update conversation context while keeping only the latest 10 messages."""

    context["messages"].append(message)

    if len(context["messages"]) > MAX_CONTEXT_MESSAGES:
        context["messages"] = context["messages"][
            -MAX_CONTEXT_MESSAGES:
        ]

    extracted = extract_customer_details(message)

    # New information replaces old information
    for key, value in extracted.items():
        context[key] = value

    return context


# -----------------------------
# CONTEXT TEST
# -----------------------------

print("\n--- Context Preservation Test ---")

conversation_context = {
    "messages": [],
    "order_id": None,
    "product_code": None,
    "date": None
}

messages = [
    "My name is Anjali.",
    "My order is ORD12345.",
    "The product code is KB-100.",
    "The order was placed on 2026-09-07."
]

for message in messages:
    conversation_context = update_context(
        conversation_context,
        message
    )

print("Order ID:",
      conversation_context["order_id"])

print("Product code:",
      conversation_context["product_code"])

print("Date:",
      conversation_context["date"])

print("Messages stored:",
      len(conversation_context["messages"]))

# -----------------------------
# CORRECTED INFORMATION
# -----------------------------

def update_corrected_information(
    context,
    message
):
    """Update stored information when the customer provides a correction."""

    text = message.lower()

    # Detect corrected order ID
    corrected_order = re.search(
        r'(?:correct|change|actually|new order|wrong order)[^\n]*?'
        r'\b(?:ORD|ORDER)[-_]?\d{3,}\b',
        message,
        re.IGNORECASE
    )

    if corrected_order:
        order_match = re.search(
            r'\b(?:ORD|ORDER)[-_]?\d{3,}\b',
            corrected_order.group(0),
            re.IGNORECASE
        )

        if order_match:
            context["order_id"] = order_match.group(0)

    # Detect corrected product code
    corrected_product = re.search(
        r'(?:correct|change|actually|new product|wrong product)[^\n]*?'
        r'\b(?:KB|PROD|PRD)[-_]?\d{2,}\b',
        message,
        re.IGNORECASE
    )

    if corrected_product:
        product_match = re.search(
            r'\b(?:KB|PROD|PRD)[-_]?\d{2,}\b',
            corrected_product.group(0),
            re.IGNORECASE
        )

        if product_match:
            context["product_code"] = product_match.group(0)

    return context


# -----------------------------
# SPELLING ERROR HANDLING
# -----------------------------

COMMON_CORRECTIONS = {
    "keybord": "keyboard",
    "keyboad": "keyboard",
    "keybaord": "keyboard",
    "refnd": "refund",
    "ordr": "order",
    "paymant": "payment"
}


def correct_spelling(message):
    """Correct common spelling errors without changing IDs or codes."""

    corrected_message = message

    for wrong, correct in COMMON_CORRECTIONS.items():

        corrected_message = re.sub(
            rf'\b{re.escape(wrong)}\b',
            correct,
            corrected_message,
            flags=re.IGNORECASE
        )

    return corrected_message


# -----------------------------
# INTENT DETECTION
# -----------------------------

INTENT_PATTERNS = {
    "Technical support": [
        "not working",
        "doesn't work",
        "problem",
        "error",
        "broken"
    ],

    "Refund": [
        "refund",
        "money back",
        "return my money"
    ],

    "Order status": [
        "where is my order",
        "order status",
        "track my order",
        "delivery"
    ],

    "Product information": [
        "product",
        "features",
        "specification",
        "specifications"
    ]
}


def detect_intent(message):
    """Detect customer intent and confidence."""

    text = message.lower()

    scores = {}

    for intent, patterns in INTENT_PATTERNS.items():

        score = 0

        for pattern in patterns:
            if pattern in text:
                score += 1

        scores[intent] = score

    best_intent = max(
        scores,
        key=scores.get
    )

    best_score = scores[best_intent]
    total_matches = sum(scores.values())

    if total_matches == 0:
        confidence = 0.0
    else:
        confidence = best_score / total_matches

    if confidence < INTENT_CONFIDENCE_THRESHOLD:
        return {
            "intent": "Unknown",
            "confidence": round(confidence, 2),
            "needs_clarification": True
        }

    return {
        "intent": best_intent,
        "confidence": round(confidence, 2),
        "needs_clarification": False
    }


# -----------------------------
# CLARIFICATION HANDLING
# -----------------------------

def check_clarification(message):
    """Check whether language or intent confidence is too low."""

    language_result = detect_language(message)
    intent_result = detect_intent(message)

    if language_result["confidence"] < LANGUAGE_CONFIDENCE_THRESHOLD:
        return {
            "needs_clarification": True,
            "reason": "Language confidence is too low."
        }

    if intent_result["confidence"] < INTENT_CONFIDENCE_THRESHOLD:
        return {
            "needs_clarification": True,
            "reason": "Intent confidence is too low."
        }

    return {
        "needs_clarification": False,
        "reason": None
    }


# -----------------------------
# CORRECTION TEST
# -----------------------------

print("\n--- Corrected Information Test ---")

correction_context = {
    "messages": [],
    "order_id": "ORD12345",
    "product_code": "KB-100",
    "date": "2026-09-07"
}

correction_message = (
    "Actually, the correct order is ORD12346."
)

correction_context = update_corrected_information(
    correction_context,
    correction_message
)

print("Updated Order ID:",
      correction_context["order_id"])


# -----------------------------
# SPELLING TEST
# -----------------------------

print("\n--- Spelling Correction Test ---")

misspelled_message = (
    "My keybord is not working."
)

corrected_message = correct_spelling(
    misspelled_message
)

print("Original:", misspelled_message)
print("Corrected:", corrected_message)


# -----------------------------
# INTENT TEST
# -----------------------------

print("\n--- Intent Detection Test ---")

intent_message = (
    "My keybord is not working."
)

intent_message = correct_spelling(
    intent_message
)

intent_result = detect_intent(
    intent_message
)

print("Intent:",
      intent_result["intent"])

print("Confidence:",
      intent_result["confidence"])

print("Needs clarification:",
      intent_result["needs_clarification"])


# -----------------------------
# LOW-CONFIDENCE TEST
# -----------------------------

print("\n--- Clarification Test ---")

ambiguous_message = (
    "I need help with something."
)

clarification = check_clarification(
    ambiguous_message
)

print("Needs clarification:",
      clarification["needs_clarification"])

print("Reason:",
      clarification["reason"])

# -----------------------------
# SESSION MANAGEMENT
# -----------------------------

class CustomerSession:

    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.messages = []
        self.summary = ""
        self.language = None
        self.last_activity = datetime.now()
        self.active = True

    def add_message(self, message):
        """Store message and keep only the latest 10 messages."""

        self.messages.append(message)

        if len(self.messages) > MAX_CONTEXT_MESSAGES:
            self.messages = self.messages[
                -MAX_CONTEXT_MESSAGES:
            ]

        self.last_activity = datetime.now()
        self.active = True

    def create_summary(self):
        """Create a simple conversation summary."""

        if not self.messages:
            self.summary = "No conversation history."

        else:
            self.summary = (
                "Customer discussed: "
                + " | ".join(self.messages[-3:])
            )

        return self.summary


class SessionManager:

    def __init__(self):
        self.sessions = {}
        self.closed_sessions = {}

    def get_session(self, customer_id):
        """Get an existing session or create a new one."""

        if customer_id in self.sessions:
            session = self.sessions[customer_id]

            inactive_minutes = (
                datetime.now() - session.last_activity
            ).total_seconds() / 60

            if inactive_minutes > SESSION_INACTIVITY_MINUTES:

                session.active = False

                session.create_summary()

                self.closed_sessions[customer_id] = {
                    "summary": session.summary,
                    "closed_at": datetime.now()
                }

                del self.sessions[customer_id]

        # Restore conversation if customer returns within 24 hours
        if customer_id in self.closed_sessions:

            closed_data = self.closed_sessions[customer_id]

            hours_since_closed = (
                datetime.now() - closed_data["closed_at"]
            ).total_seconds() / 3600

            if hours_since_closed <= SESSION_RESTORE_HOURS:

                new_session = CustomerSession(
                    customer_id
                )

                new_session.summary = (
                    closed_data["summary"]
                )

                self.sessions[customer_id] = new_session

                return new_session

            else:
                del self.closed_sessions[customer_id]

        # Create completely new session
        new_session = CustomerSession(
            customer_id
        )

        self.sessions[customer_id] = new_session

        return new_session


# -----------------------------
# SESSION TEST
# -----------------------------

print("\n--- Session Management Test ---")

manager = SessionManager()

customer_1 = manager.get_session("CUSTOMER_001")

customer_1.add_message(
    "Hello, my order is ORD12345."
)

customer_1.add_message(
    "The keyboard is not working."
)

print("Customer 1 messages:",
      len(customer_1.messages))

print("Customer 1 order context:",
      extract_customer_details(
          customer_1.messages[0]
      ).get("order_id"))


# -----------------------------
# SESSION ISOLATION TEST
# -----------------------------

customer_2 = manager.get_session("CUSTOMER_002")

customer_2.add_message(
    "I need help with my refund."
)

print("\n--- Session Isolation Test ---")

print("Customer 1 messages:",
      customer_1.messages)

print("Customer 2 messages:",
      customer_2.messages)


# -----------------------------
# 10-MESSAGE CONTEXT TEST
# -----------------------------

print("\n--- 10-Message Context Test ---")

for number in range(1, 13):

    customer_1.add_message(
        "Test message " + str(number)
    )

print("Messages stored:",
      len(customer_1.messages))

print("Stored messages:")

for message in customer_1.messages:
    print(message)


# -----------------------------
# SIMULATED SESSION EXPIRY
# -----------------------------

print("\n--- Session Expiry Test ---")

customer_1.last_activity = (
    datetime.now()
    - timedelta(
        minutes=SESSION_INACTIVITY_MINUTES + 1
    )
)

expired_session = manager.get_session(
    "CUSTOMER_001"
)

print(
    "Session restored:",
    expired_session.summary != ""
)


# -----------------------------
# SIMULATED 24-HOUR RESTORATION
# -----------------------------

print("\n--- 24-Hour Restoration Test ---")

customer_1.last_activity = (
    datetime.now()
    - timedelta(
        minutes=SESSION_INACTIVITY_MINUTES + 1
    )
)

manager.get_session("CUSTOMER_001")

manager.closed_sessions["CUSTOMER_001"]["closed_at"] = (
    datetime.now()
    - timedelta(hours=2)
)

restored_session = manager.get_session(
    "CUSTOMER_001"
)

print(
    "Conversation restored:",
    restored_session.summary != ""
)


# -----------------------------
# SIMULATED NEW SESSION AFTER 24 HOURS
# -----------------------------

print("\n--- New Session After 24 Hours Test ---")

restored_session.last_activity = (
    datetime.now()
    - timedelta(
        minutes=SESSION_INACTIVITY_MINUTES + 1
    )
)

manager.get_session("CUSTOMER_001")

manager.closed_sessions["CUSTOMER_001"]["closed_at"] = (
    datetime.now()
    - timedelta(hours=25)
)

new_session = manager.get_session(
    "CUSTOMER_001"
)

print(
    "New session created:",
    new_session.summary == ""
)

# -----------------------------
# FINAL TASK 6 EVALUATION
# -----------------------------

print("\n--- Multiple Requests Test ---")

multiple_request = (
    "My keyboard is not working and I also want a refund."
)

multiple_intents = []

for intent, patterns in INTENT_PATTERNS.items():
    for pattern in patterns:
        if pattern in multiple_request.lower():
            multiple_intents.append(intent)
            break

print("Detected requests:", multiple_intents)


print("\n--- Ambiguous Follow-Up Test ---")

ambiguous_followup = "What about that?"

clarification_result = check_clarification(
    ambiguous_followup
)

print(
    "Needs clarification:",
    clarification_result["needs_clarification"]
)

print(
    "Reason:",
    clarification_result["reason"]
)


print("\n--- Transliterated Input Test ---")

transliterated_message = (
    "Mera keyboard kaam nahi kar raha"
)

transliterated_language = detect_language(
    transliterated_message
)

print(
    "Detected language:",
    transliterated_language["language"]
)

print(
    "Confidence:",
    transliterated_language["confidence"]
)

if transliterated_language["language"] == "Unknown":
    print("Clarification required: Yes")


print("\n--- Language Switching Conversation Test ---")

switching_messages = [
    "Hello, my order is ORD55555.",
    "Hola, mi teclado no funciona.",
    "Bonjour, je veux un remboursement."
]

current_language = None

for message in switching_messages:

    result = update_conversation_language(
        message,
        current_language
    )

    current_language = result["language"]

    print(
        "Message:",
        message
    )

    print(
        "Language:",
        current_language
    )


print("\n--- Corrected Order Test ---")

correction_context = {
    "messages": [],
    "order_id": "ORD55555",
    "product_code": "KB-200",
    "date": "2026-09-07"
}

correction = (
    "Actually, the correct order is ORD55556."
)

correction_context = update_corrected_information(
    correction_context,
    correction
)

print(
    "Corrected order ID:",
    correction_context["order_id"]
)


print("\n--- Final Session Isolation Test ---")

session_a = manager.get_session(
    "CUSTOMER_A"
)

session_b = manager.get_session(
    "CUSTOMER_B"
)

session_a.add_message(
    "My order is ORD11111."
)

session_b.add_message(
    "My order is ORD22222."
)

print(
    "Customer A messages:",
    session_a.messages
)

print(
    "Customer B messages:",
    session_b.messages
)

print(
    "Sessions isolated:",
    session_a.messages != session_b.messages
)
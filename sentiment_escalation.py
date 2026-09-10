import re
from datetime import datetime


# -----------------------------
# CONFIGURATION
# -----------------------------

BUSINESS_START = 9
BUSINESS_END = 18

NEGATIVE_ESCALATION_MINUTES = 15


# -----------------------------
# SENTIMENT KEYWORDS
# -----------------------------

POSITIVE_WORDS = [
    "thank",
    "thanks",
    "great",
    "good",
    "happy",
    "excellent"
]

NEGATIVE_WORDS = [
    "bad",
    "terrible",
    "disappointed",
    "angry",
    "upset",
    "not working",
    "problem",
    "wrong"
]

URGENT_WORDS = [
    "urgent",
    "immediately",
    "emergency",
    "asap",
    "right now"
]

FRUSTRATED_WORDS = [
    "frustrated",
    "ridiculous",
    "unacceptable",
    "again",
    "still",
    "fed up"
]

SARCASM_WORDS = [
    "great job",
    "wonderful",
    "amazing",
    "thanks a lot"
]


# -----------------------------
# HIGH-RISK ISSUES
# -----------------------------

HIGH_RISK_PATTERNS = {
  "Account compromise": [
    "account hacked",
    "account compromised",
    "someone accessed my account",
    "account was accessed",
    "someone else accessed my account",
    "someone else accessed",
    "unauthorised access",
    "unauthorized access"
],

    "Duplicate payment": [
        "charged twice",
        "paid twice",
        "duplicate payment",
        "duplicate charge"
    ],

    "Legal threat": [
        "legal action",
        "sue",
        "lawyer",
        "court",
        "legal complaint"
    ]
}


# -----------------------------
# BASIC LANGUAGE DETECTION
# -----------------------------

def detect_language(message):
    """Detect common languages using simple keyword patterns."""

    text = message.lower()

    if any(
        word in text
        for word in [
            "hola",
            "gracias",
            "problema"
        ]
    ):
        return "Spanish"

    if any(
        word in text
        for word in [
            "bonjour",
            "merci",
            "problème"
        ]
    ):
        return "French"

    if any(
        word in text
        for word in [
            "hindi",
            "नमस्ते"
        ]
    ):
        return "Hindi"

    return "English"


print("Sentiment escalation module loaded.")

# -----------------------------
# SENTIMENT ANALYSIS
# -----------------------------

def analyse_sentiment(message, conversation_history=None):
    """Analyse sentiment, urgency, frustration and sarcasm."""

    text = message.lower()

    if conversation_history is None:
        conversation_history = []

    combined_text = " ".join(
        conversation_history
    ).lower() + " " + text

    positive_score = sum(
        1 for word in POSITIVE_WORDS
        if word in text
    )

    negative_score = sum(
        1 for word in NEGATIVE_WORDS
        if word in text
    )

    frustrated_score = sum(
        1 for word in FRUSTRATED_WORDS
        if word in text
    )

    urgent_score = sum(
        1 for word in URGENT_WORDS
        if word in text
    )

    sarcastic_score = sum(
        1 for phrase in SARCASM_WORDS
        if phrase in text
    )

    # Determine main sentiment
    if sarcastic_score > 0:
        sentiment = "Sarcastic"

    elif frustrated_score > 0:
        sentiment = "Frustrated"

    elif negative_score > positive_score:
        sentiment = "Negative"

    elif positive_score > negative_score:
        sentiment = "Positive"

    else:
        sentiment = "Neutral"

    # Urgent flag
    urgency = urgent_score > 0

    # Repeated negative messages
    negative_history_count = 0

    for previous_message in conversation_history:

        previous_lower = previous_message.lower()

        if any(
            word in previous_lower
            for word in NEGATIVE_WORDS
        ):
            negative_history_count += 1

    repeated_negative = (
        negative_history_count >= 2
    )

    # Confidence score
    total_signals = (
        positive_score
        + negative_score
        + frustrated_score
        + urgent_score
        + sarcastic_score
    )

    if total_signals == 0:
        confidence = 0.50
    else:
        confidence = min(
            0.95,
            0.60 + (total_signals * 0.05)
        )

    return {
        "language": detect_language(message),
        "sentiment": sentiment,
        "urgent": urgency,
        "frustrated": frustrated_score > 0,
        "sarcastic": sarcastic_score > 0,
        "repeated_negative": repeated_negative,
        "confidence": round(confidence, 2)
    }


# -----------------------------
# SENTIMENT TEST
# -----------------------------

print("\n--- Sentiment Analysis Test ---")

test_message = (
    "This is ridiculous! "
    "My keyboard is still not working. "
    "I need this fixed immediately."
)

result = analyse_sentiment(
    test_message
)

print("Language:", result["language"])
print("Sentiment:", result["sentiment"])
print("Urgent:", result["urgent"])
print("Frustrated:", result["frustrated"])
print("Sarcastic:", result["sarcastic"])
print("Confidence:", result["confidence"])

# -----------------------------
# HIGH-RISK ISSUE DETECTION
# -----------------------------

def detect_high_risk_issue(message):
    """Detect high-risk customer issues."""

    text = message.lower()

    detected_risks = []

    for risk, patterns in HIGH_RISK_PATTERNS.items():

        for pattern in patterns:

            if pattern in text:
                detected_risks.append(risk)
                break

    return detected_risks


# -----------------------------
# HIGH-RISK TEST
# -----------------------------

print("\n--- High-Risk Issue Test ---")

risk_message = (
    "I was charged twice for the same order."
)

risks = detect_high_risk_issue(
    risk_message
)

print("Detected risks:", risks)

# -----------------------------
# ESCALATION LOGIC
# -----------------------------

def create_escalation(
    reason,
    condition,
    conversation
):
    """Create a record for an escalation."""

    return {
        "reason": reason,
        "activated_condition": condition,
        "conversation_summary": conversation
    }


def check_escalation(
    sentiment_result,
    high_risk_issues,
    unresolved_minutes,
    conversation
):
    """Check whether the conversation requires escalation."""

    escalations = []

    # High-risk issue
    for risk in high_risk_issues:

        escalations.append(
            create_escalation(
                risk,
                "High-risk issue detected",
                conversation
            )
        )

    # Repeated negative messages
    if sentiment_result["repeated_negative"]:

        escalations.append(
            create_escalation(
                "Repeated negative messages",
                "Negative sentiment repeated in conversation history",
                conversation
            )
        )

    # Negative conversation unresolved for more than 15 minutes
    if (
        sentiment_result["sentiment"]
        in ["Negative", "Frustrated", "Sarcastic"]
        and unresolved_minutes > NEGATIVE_ESCALATION_MINUTES
    ):

        escalations.append(
            create_escalation(
                "Negative conversation unresolved",
                "Negative conversation exceeded 15 minutes",
                conversation
            )
        )

    return escalations


# -----------------------------
# ESCALATION TEST
# -----------------------------

print("\n--- Escalation Test ---")

conversation_history = [
    "My keyboard is not working.",
    "This problem is still not fixed.",
    "I am frustrated and this is unacceptable."
]

current_message = (
    "I have been waiting for 20 minutes. "
    "This is still not resolved."
)

sentiment_result = analyse_sentiment(
    current_message,
    conversation_history
)

high_risk_issues = detect_high_risk_issue(
    current_message
)

escalations = check_escalation(
    sentiment_result,
    high_risk_issues,
    20,
    "Customer reports an unresolved keyboard issue."
)

for escalation in escalations:

    print("\nReason:", escalation["reason"])
    print(
        "Condition:",
        escalation["activated_condition"]
    )
    print(
        "Summary:",
        escalation["conversation_summary"]
    )
    # -----------------------------
# AFTER-HOURS ROUTING
# -----------------------------

def route_complaint(
    message,
    current_hour=None
):
    """Route complaints based on urgency and business hours."""

    sentiment_result = analyse_sentiment(
        message
    )

    if current_hour is None:
        current_hour = datetime.now().hour

    business_hours = (
        BUSINESS_START <= current_hour < BUSINESS_END
    )

    if business_hours:
        return "Normal support queue"

    if sentiment_result["urgent"]:
        return "On-call queue"

    return "Next working day"


# -----------------------------
# AFTER-HOURS TESTS
# -----------------------------

print("\n--- After-Hours Urgent Test ---")

urgent_message = (
    "This is urgent. "
    "Someone accessed my account and I need help immediately."
)

urgent_route = route_complaint(
    urgent_message,
    current_hour=22
)

print("Routing result:", urgent_route)


print("\n--- After-Hours Normal Test ---")

normal_message = (
    "My keyboard is not working."
)

normal_route = route_complaint(
    normal_message,
    current_hour=22
)

print("Routing result:", normal_route)

# -----------------------------
# FINAL EVALUATION TESTS
# -----------------------------

print("\n--- Sarcasm Test ---")

sarcasm_message = (
    "Great job, my keyboard is still not working."
)

sarcasm_result = analyse_sentiment(
    sarcasm_message
)

print("Sentiment:", sarcasm_result["sentiment"])
print("Sarcastic:", sarcasm_result["sarcastic"])
print("Confidence:", sarcasm_result["confidence"])


print("\n--- Calm High-Risk Test ---")

calm_risk_message = (
    "I noticed that my account was accessed by someone else."
)

calm_risk_result = analyse_sentiment(
    calm_risk_message
)

calm_risks = detect_high_risk_issue(
    calm_risk_message
)

calm_escalations = check_escalation(
    calm_risk_result,
    calm_risks,
    5,
    "Customer calmly reports possible account compromise."
)

print("Sentiment:", calm_risk_result["sentiment"])
print("High-risk issues:", calm_risks)
print("Escalations:", len(calm_escalations))


print("\n--- Simulated Time Test ---")

morning_message = (
    "My keyboard is not working."
)

morning_route = route_complaint(
    morning_message,
    current_hour=10
)

night_route = route_complaint(
    "This is urgent. Please help immediately.",
    current_hour=22
)

print("10:00 routing:", morning_route)
print("22:00 routing:", night_route)
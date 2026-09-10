import os
import shutil
import hashlib

import re
from datetime import datetime

RETRY_DELAYS = [15, 30, 60]

def show_retry_schedule():
    print("\n--- Retry Schedule ---")
    for attempt, minutes in enumerate(RETRY_DELAYS, 1):
        print(f"Attempt {attempt}: retry after {minutes} minutes")


def check_maintenance_window():
    current_hour = datetime.now().hour

    # Maintenance window: 2 PM to 4 PM
    if 14 <= current_hour < 16:
        print("Maintenance window: OPEN")
        print("Updates are allowed.")
    else:
        print("Maintenance window: CLOSED")
        print("Updates are not allowed.")

    # Maintenance window: 2 PM to 4 PM
    if 14 <= current_hour < 16:
        print("Maintenance window: OPEN")
        print("Updates are allowed.")
    else:
        print("Maintenance window: CLOSED")
        print("Updates are not allowed.")

    print("\n--- Retry Schedule ---")
    for attempt, minutes in enumerate(RETRY_DELAYS, 1):
        print(f"Attempt {attempt}: retry after {minutes} minutes")


def mask_sensitive_data(text):
    text = re.sub(r'\S+@\S+\.\S+', '[EMAIL MASKED]', text)
    text = re.sub(r'\b\d{10}\b', '[PHONE MASKED]', text)
    text = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[CARD MASKED]', text)
    return text

from datetime import datetime

# Folders
INPUT = "input_documents"
PROCESSED = "processed"
QUARANTINE = "quarantine"
VERSIONS = "versions"

for folder in [INPUT, PROCESSED, QUARANTINE, VERSIONS]:
    os.makedirs(folder, exist_ok=True)


def get_hash(filepath):
    """Create a unique hash for a document."""
    with open(filepath, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()


def scan_documents():
    
    """Find new or modified documents."""
    files = os.listdir(INPUT)

    if not files:
        print("No documents found.")
        return

    for filename in files:
        filepath = os.path.join(INPUT, filename)

        if not os.path.isfile(filepath):
            continue

        print("Checking document: [DOCUMENT NAME HIDDEN]")

        # Prompt-injection protection
        with open(filepath, "r", errors="ignore") as file:
            content = file.read().lower()

        suspicious_words = [
            "ignore previous instructions",
            "ignore all instructions",
            "system prompt",
            "jailbreak"
        ]

        if any(word in content for word in suspicious_words):
            print(f"  REJECTED: Suspicious instructions found in {filename}")
            shutil.move(filepath, os.path.join(QUARANTINE, filename))
            continue



        # Check duplicate
        file_hash = get_hash(filepath)
        duplicate = False

        for old_file in os.listdir(PROCESSED):
            old_path = os.path.join(PROCESSED, old_file)

            if os.path.isfile(old_path) and get_hash(old_path) == file_hash:
                duplicate = True
                break

        if duplicate:
            print(f"  DUPLICATE: {filename}")
            continue

        # Basic validation
        if os.path.getsize(filepath) == 0:
            print(f"  INVALID: {filename}")
            shutil.move(filepath, os.path.join(QUARANTINE, filename))
            continue

        # Process document
        shutil.copy(filepath, os.path.join(PROCESSED, filename))

        # Create version
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_name = f"{timestamp}_{filename}"
        shutil.copy(filepath, os.path.join(VERSIONS, version_name))

        print("  PROCESSED: [SENSITIVE DATA MASKED]")
        print(f"  VERSION CREATED: {version_name}")


def rollback():
    """Restore the latest version."""
    versions = os.listdir(VERSIONS)

    if not versions:
        print("No versions available.")
        return

    latest = sorted(versions)[-1]
    source = os.path.join(VERSIONS, latest)

    filename = latest.split("_", 2)[-1]
    destination = os.path.join(PROCESSED, filename)

    shutil.copy(source, destination)

    print(f"Rollback completed: {filename}")


def quality_check():
    """Basic knowledge-base quality check."""
    files = os.listdir(PROCESSED)

    if files:
        print("Quality check: PASSED")
        print(f"Documents in knowledge base: {len(files)}")
    else:
        print("Quality check: FAILED")


def show_status():
    processed = len(os.listdir(PROCESSED))
    quarantined = len(os.listdir(QUARANTINE))
    versions = len(os.listdir(VERSIONS))

    print("\n--- Knowledge Base Monitoring ---")
    print("Documents processed:", processed)
    print("Documents quarantined:", quarantined)
    print("Versions created:", versions)

    if processed > 0:
        print("Pipeline status: HEALTHY")
    else:
        print("Pipeline status: NO DOCUMENTS")

# Simple access control
ROLE = input("Enter your role (admin/operator/viewer): ").lower()

if ROLE not in ["admin", "operator", "viewer"]:
    print("Access denied.")
    exit()

print(f"Access granted: {ROLE}")


# Main menu
while True:
    print("\n===== CHATBOT KNOWLEDGE BASE =====")
    print("1. Scan and process documents")
    print("2. Quality check")
    print("3. Rollback")
    print("4. Show status")
    print("5. Show retry schedule")
    print("6. Check maintenance window")
    print("7. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        scan_documents()

    elif choice == "2":
        quality_check()

    elif choice == "3":
        rollback()

    elif choice == "4":
        show_status()

    elif choice == "5":
     show_retry_schedule()

    elif choice == "6":
       check_maintenance_window()

    elif choice == "7":
     print("Pipeline stopped.")
     break

else:
    print("Invalid choice.")

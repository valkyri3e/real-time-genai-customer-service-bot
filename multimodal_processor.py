import os
import time
import threading
from queue import Queue
from pathlib import Path
import re
import pytesseract
from PIL import Image, ImageFilter
import fitz

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

UNSAFE_EXTENSIONS = {
    ".exe",
    ".bat",
    ".cmd",
    ".sh",
    ".js"
}

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".pdf"
}


def validate_file(file_path):
    path = Path(file_path)

    if not path.exists():
        return False, "File does not exist."

    if path.suffix.lower() in UNSAFE_EXTENSIONS:
        return False, "Unsafe file type rejected."

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False, "Unsupported file type."

    return True, "File is valid."


def check_image_quality(file_path):
    """Check whether an image is too small or too blurry."""

    image = Image.open(file_path).convert("L")
    width, height = image.size

    if width < 300 or height < 300:
        return False

    edges = image.filter(ImageFilter.FIND_EDGES)
    variance = edges.getextrema()[1]

    if variance < 100:
        return False

    return True


def extract_text_from_image(file_path):
    """Extract text from an image using OCR."""

    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)

    return text.strip()


def extract_text_from_pdf(file_path):
    """Extract text from text-based and scanned PDFs."""

    document = fitz.open(file_path)
    extracted_text = []

    for page in document:
        text = page.get_text().strip()

        if text:
            extracted_text.append(text)
        else:
            pix = page.get_pixmap()

            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            ocr_text = pytesseract.image_to_string(image)
            extracted_text.append(ocr_text)

    document.close()

    return "\n".join(extracted_text).strip()


def extract_text(file_path):
    """Choose the correct extraction method based on file type."""

    extension = Path(file_path).suffix.lower()

    if extension in {".jpg", ".jpeg", ".png", ".webp"}:
        return extract_text_from_image(file_path)

    elif extension == ".pdf":
        return extract_text_from_pdf(file_path)

    return ""


def detect_prompt_injection(text):
    """Detect suspicious instructions hidden in extracted text."""

    suspicious_patterns = [
        r"ignore previous instructions",
        r"ignore all instructions",
        r"system prompt",
        r"reveal your instructions",
        r"disregard previous instructions"
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def extract_invoice_details(text):
    """Extract important fields without inventing values."""

    details = {
        "order_id": None,
        "date": None,
        "amount": None,
        "product": None,
        "error_code": None
    }

    order_match = re.search(
        r"Order ID\s*:\s*([A-Za-z0-9-]+)",
        text,
        re.IGNORECASE
    )

    date_match = re.search(
        r"Order Date\s*:\s*(.+)",
        text,
        re.IGNORECASE
    )

    amount_match = re.search(
        r"Total Amount\s*:\s*(.+)",
        text,
        re.IGNORECASE
    )

    product_match = re.search(
        r"Product\s*:\s*(.+)",
        text,
        re.IGNORECASE
    )

    error_match = re.search(
        r"Error Code\s*:\s*([A-Za-z0-9-]+)",
        text,
        re.IGNORECASE
    )

    if order_match:
        details["order_id"] = order_match.group(1).strip()

    if date_match:
        details["date"] = date_match.group(1).strip()

    if amount_match:
        details["amount"] = amount_match.group(1).strip()

    if product_match:
        details["product"] = product_match.group(1).strip()

    if error_match:
        details["error_code"] = error_match.group(1).strip()

    return details


def mask_sensitive_info(text):
    """Mask personal and payment information before logging."""

    text = re.sub(
        r"(Customer Name\s*:\s*).+",
        r"\1[REDACTED]",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"(Price\s*:\s*).+",
        r"\1[REDACTED]",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"(Total Amount\s*:\s*).+",
        r"\1[REDACTED]",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"(Payment Status\s*:\s*).+",
        r"\1[REDACTED]",
        text,
        flags=re.IGNORECASE
    )

    return text


def process_customer_request(message, file_path=None):
    """Process a customer message and uploaded file."""

    print("\n--- Customer Request ---")
    print("Message:", message)

    if not file_path:
        print("No file uploaded.")
        return

    valid, result = validate_file(file_path)

    if not valid:
        print("File rejected:", result)
        return

    print("File accepted:", file_path)

    if Path(file_path).suffix.lower() in {
        ".jpg", ".jpeg", ".png", ".webp"
    }:

        if not check_image_quality(file_path):
            print(
                "File rejected: Image quality is too low. "
                "Please upload a clearer image."
            )
            return

    extracted_text = extract_text(file_path)

    if detect_prompt_injection(extracted_text):
        print(
            "File rejected: Suspicious instructions detected "
            "in extracted text."
        )
        return

    invoice_details = extract_invoice_details(extracted_text)

    message_order_match = re.search(
        r"order\s+([A-Za-z0-9-]+)",
        message,
        re.IGNORECASE
    )

    if message_order_match:

        message_order_id = message_order_match.group(1)

        if invoice_details["order_id"] == message_order_id:
            print("Order ID check: MATCH")

        else:
            print("Order ID check: CONFLICT")
            print(
                "Please confirm your order ID or upload "
                "the correct invoice."
            )

    else:
        print("Order ID check: Not provided in message")

    message_error_match = re.search(
        r"\bERR-\d+\b",
        message,
        re.IGNORECASE
    )

    if message_error_match:

        message_error_code = message_error_match.group(0)

        if invoice_details["error_code"] == message_error_code:
            print("Error Code check: MATCH")

        else:
            print("Error Code check: CONFLICT")

    else:
        print("Error Code check: Not provided in message")

    print("\n--- Extracted Invoice Details ---")
    print("Order ID:", invoice_details["order_id"])
    print("Date:", invoice_details["date"])
    print("Amount: [REDACTED]")
    print("Product:", invoice_details["product"])
    print("Error Code:", invoice_details["error_code"])

    print("\n--- Extracted Text ---")

    if extracted_text:
        masked_text = mask_sensitive_info(extracted_text)
        print(masked_text)

    else:
        print("No readable text could be extracted.")

    return extracted_text


def delete_after_retention(file_path, retention_seconds=60):
    """Delete an uploaded file after the retention period."""

    time.sleep(retention_seconds)

    if file_path and Path(file_path).exists():
        os.remove(file_path)
        print("Uploaded file deleted after retention period.")


processing_queue = Queue()


def background_worker():
    """Process requests placed in the background queue."""

    while True:

        request = processing_queue.get()

        if request is None:
            break

        message, file_path = request

        print("\nBackground processing started.")

        process_customer_request(message, file_path)

        processing_queue.task_done()


worker_thread = threading.Thread(
    target=background_worker,
    daemon=True
)

worker_thread.start()


def handle_customer_request(message, file_path=None):
    """Handle normal and long-running customer requests."""

    start_time = time.time()

    if file_path:
        threading.Thread(
            target=delete_after_retention,
            args=(file_path, 60),
            daemon=True
        ).start()

    processing_thread = threading.Thread(
        target=process_customer_request,
        args=(message, file_path)
    )

    processing_thread.start()

    processing_thread.join(timeout=30)

    if processing_thread.is_alive():

        print("\nProcessing exceeded 30 seconds.")
        print("Request moved to background queue.")
        print(
            "Customer notified: Your request is still being processed."
        )

        processing_queue.put(
            (message, file_path)
        )


if __name__ == "__main__":

    customer_message = (
        "My order 99999 has an error ERR-204."
        "I have attached the invoice."
    )

    file_path = "sample_invoice.png"

    handle_customer_request(
        customer_message,
        file_path
    )
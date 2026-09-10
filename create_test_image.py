from PIL import Image, ImageDraw, ImageFont

# Create a white image
image = Image.new("RGB", (1000, 700), "white")
draw = ImageDraw.Draw(image)

# Text for OCR testing
text = """SAMPLE INVOICE

Invoice Number: INV-1001
Order ID: 12345
Customer Name: Test Customer
Order Date: 07 September 2026

Product: Wireless Keyboard
Quantity: 1
Price: Rs. 1500
Total Amount: Rs. 1500

Payment Status: Paid
Error Code: ERR-204
"""

# Use a default font
font = ImageFont.load_default(size=25)

# Write the text onto the image
draw.multiline_text((50, 50), text, fill="black", font=font, spacing=15)

# Save the image in the project folder
image.save("sample_invoice.png")

print("sample_invoice.png created successfully!")
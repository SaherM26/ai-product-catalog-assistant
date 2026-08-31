from pathlib import Path

from app.extraction import extract_products
from app.validation import validate_products


file_path = Path(
    "sample-data/Synthetic_Supplier_Price_List_51_Products.xlsx"
)

with file_path.open("rb") as file:
    file_bytes = file.read()


# Step 1: Extract products with Gemini
extracted = extract_products(
    file_bytes=file_bytes,
    filename=file_path.name,
)

# Step 2: Validate and normalize products
validated = validate_products(
    extracted.products
)


print(f"Total products: {len(validated)}")
print()

review_count = 0

for index, product in enumerate(validated, start=1):

    if product["needs_review"]:
        review_count += 1

        print(f"--- Review Required: Product {index} ---")
        print(f"Product: {product['product_name']}")
        print(f"Brand: {product['brand']}")
        print(f"UOM: {product['uom']}")
        print(f"MOQ: {product['moq']}")
        print(f"Price: {product['price']}")
        print(f"HSN: {product['hsn']}")
        print(f"Reason: {product['review_reason']}")
        print()


print(f"Products requiring review: {review_count}")
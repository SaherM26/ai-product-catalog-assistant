from pathlib import Path

from app.extraction import extract_products


file_path = Path(
    "sample-data/Synthetic_Supplier_Price_List_51_Products.xlsx"
)

with file_path.open("rb") as file:
    file_bytes = file.read()


result = extract_products(
    file_bytes=file_bytes,
    filename=file_path.name,
)


print(f"Products extracted: {len(result.products)}")
print()

for index, product in enumerate(result.products[:5], start=1):
    print(f"--- Product {index} ---")
    print(f"Product Name: {product.product_name}")
    print(f"Brand: {product.brand}")
    print(f"UOM: {product.uom}")
    print(f"MOQ: {product.moq}")
    print(f"Price: {product.price}")
    print(f"HSN: {product.hsn}")
    print()
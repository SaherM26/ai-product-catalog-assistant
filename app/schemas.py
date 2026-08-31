from typing import Optional

from pydantic import BaseModel, Field


class Product(BaseModel):
    product_name: str = Field(
        description="Product name from the source document"
    )

    brand: Optional[str] = Field(
        default=None,
        description="Brand if present in the source"
    )

    uom: Optional[str] = Field(
        default=None,
        description="Unit of measurement"
    )

    moq: Optional[float] = Field(
        default=None,
        description="Minimum order quantity if present"
    )

    price: Optional[float] = Field(
        default=None,
        description="Product price if present"
    )

    hsn: Optional[str] = Field(
        default=None,
        description="HSN code if present in the source"
    )


class ProductExtraction(BaseModel):
    products: list[Product]
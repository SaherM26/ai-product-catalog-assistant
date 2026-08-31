import re
from difflib import SequenceMatcher
from .schemas import Product

# Canonical UOM mapping
CANONICAL_UOM = {
    "pcs": "Piece",
    "piece": "Piece",
    "pieces": "Piece",
    "nos": "Piece",
}

def normalize_uom(value: str | None) -> str | None:
    """
    Normalize common unit-of-measure variations.
    """
    if not value:
        return None

    cleaned = value.strip().lower()

    return CANONICAL_UOM.get(cleaned, value.strip())

def normalize_price(value):
    """
    Convert formatted price values into numeric values.

    Examples:
        "₹ 1,480.00" -> 1480.0
        "1,245.00"   -> 1245.0
        187          -> 187.0
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    cleaned = str(value)

    # Remove currency symbols, commas, and whitespace.
    cleaned = re.sub(
        r"[₹$€£,\s]",
        "",
        cleaned,
    )

    try:
        return float(cleaned)
    except ValueError:
        return None

def normalize_product(product: Product) -> Product:
    """
    Apply deterministic normalization to an extracted product.
    """
    return Product(
        product_name=(
            product.product_name.strip()
            if product.product_name
            else ""
        ),
        brand=(
            product.brand.strip()
            if product.brand
            else None
        ),
        uom=normalize_uom(product.uom),
        moq=product.moq,
        price=normalize_price(product.price),
        hsn=(
            product.hsn.strip()
            if product.hsn
            else None
        ),
    )

def validate_product(product: Product) -> dict:
    """
    Validate one product and identify issues that require
    human review.
    """
    product = normalize_product(product)
    review_reasons = []
    # Required product identity
    if not product.product_name:
        review_reasons.append(
            "Product name missing"
        )

    # MOQ
    if product.moq is None:
        review_reasons.append(
            "MOQ missing"
        )
    elif product.moq < 0:
        review_reasons.append(
            "MOQ cannot be negative"
        )

    # Price
    if product.price is None:
        review_reasons.append(
            "Price missing or invalid"
        )
    elif product.price < 0:
        review_reasons.append(
            "Price cannot be negative"
        )

    # HSN
    if product.hsn is None:
        review_reasons.append(
            "HSN missing"
        )

    return {
        **product.model_dump(),
        "needs_review": bool(review_reasons),
        "review_reason": (
            "; ".join(review_reasons)
            if review_reasons
            else None
        ),
    }

def combine_reason(
    existing: str | None,
    new_reason: str,
) -> str:
    """
    Append a review reason without duplicating it.
    """
    if not existing:
        return new_reason

    existing_parts = [
        part.strip()
        for part in existing.split(";")
        if part.strip()
    ]

    if new_reason not in existing_parts:
        existing_parts.append(new_reason)

    return "; ".join(existing_parts)

def normalize_name_for_comparison(
    name: str,
) -> str:
    """
    Normalize harmless formatting differences while preserving
    meaningful product specifications.
    Examples:
        '16 sqmm' -> '16sqmm'
        '4-6 A'   -> '4-6a'
    """
    value = name.lower().strip()

    # Normalize whitespace.
    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    # Remove spaces around separators.
    value = re.sub(
        r"\s*-\s*",
        "-",
        value,
    )

    # Normalize 'sq mm', 'sqmm', etc.
    value = re.sub(
        r"\s*sq\s*mm\b",
        "sqmm",
        value,
    )

    # Normalize spacing around x.
    value = re.sub(
        r"\s*x\s*",
        "x",
        value,
    )

    # Remove remaining spaces for comparison.
    value = value.replace(" ", "")

    return value

def extract_numeric_tokens(
    name: str,
) -> set[str]:
    """
    Extract numeric/specification tokens from a product name.
    """

    return set(
        re.findall(
            r"\d+(?:\.\d+)?",
            name,
        )
    )


def detect_near_duplicates(
    products: list[dict],
) -> None:
    """
    Detect suspicious duplicate or near-duplicate product names
    without incorrectly flagging legitimately different products.

    The detector:
    1. Flags exact normalized name matches with different brands.
    2. Flags only very small formatting variations when their
       numeric/specification tokens are identical.
    """

    for i in range(len(products)):

        for j in range(i + 1, len(products)):

            first = products[i]
            second = products[j]

            first_name = normalize_name_for_comparison(
                first["product_name"]
            )

            second_name = normalize_name_for_comparison(
                second["product_name"]
            )           
            # Case 1: Exact normalized product-name match
            if first_name == second_name:

                # Different brands make this a potentially
                # important duplicate that requires review.
                if (
                    first.get("brand")
                    and second.get("brand")
                    and first["brand"].strip().lower()
                    != second["brand"].strip().lower()
                ):
                    reason = (
                        "Potential duplicate product name "
                        "with different brand"
                    )

                    first["needs_review"] = True
                    second["needs_review"] = True

                    first["review_reason"] = combine_reason(
                        first.get("review_reason"),
                        reason,
                    )

                    second["review_reason"] = combine_reason(
                        second.get("review_reason"),
                        reason,
                    )

                continue
            # Case 2: Very small formatting differences
            similarity = SequenceMatcher(
                None,
                first_name,
                second_name,
            ).ratio()

            if similarity < 0.97:
                continue

            first_numbers = extract_numeric_tokens(
                first_name
            )

            second_numbers = extract_numeric_tokens(
                second_name
            )

            # Meaningful numeric specifications must match.
            if first_numbers != second_numbers:
                continue

            reason = (
                "Potential near-duplicate product name"
            )

            first["needs_review"] = True
            second["needs_review"] = True

            first["review_reason"] = combine_reason(
                first.get("review_reason"),
                reason,
            )

            second["review_reason"] = combine_reason(
                second.get("review_reason"),
                reason,
            )


def validate_products(
    products: list[Product],
) -> list[dict]:
    """
    Normalize, validate, and check products for
    potential near-duplicates.
    """

    validated = [
        validate_product(product)
        for product in products
    ]

    detect_near_duplicates(
        validated
    )

    return validated
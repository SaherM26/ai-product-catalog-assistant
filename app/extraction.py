import io
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pypdf import PdfReader

from .schemas import ProductExtraction


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Please add it to your .env file."
    )

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.6-flash"


SYSTEM_INSTRUCTIONS = """
You are an AI product catalog extraction assistant.

Your job is to extract product information from supplier PDF or Excel data.

Extract these fields:
- product_name
- brand
- uom
- moq
- price
- hsn

Rules:
1. Only use information supported by the source.
2. Never invent missing information.
3. If a value is missing, return null.
4. If a value is ambiguous or unreadable, return null.
5. Normalize UOM variants such as:
   PCS, pcs, Nos, Piece -> Piece
6. Convert formatted prices such as:
   ₹ 1,480.00 -> 1480.00
7. Do not guess HSN codes.
8. Do not guess MOQ.
9. Preserve the meaning of product names.
10. Return one product object for each product record.
"""


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""

    reader = PdfReader(io.BytesIO(file_bytes))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n\n".join(pages)


def extract_excel_text(file_bytes: bytes) -> str:
    """Convert an Excel file into CSV-style text."""

    dataframe = pd.read_excel(
        io.BytesIO(file_bytes),
        dtype=str
    )

    dataframe = dataframe.fillna("")

    return dataframe.to_csv(index=False)


def read_source(
    file_bytes: bytes,
    filename: str
) -> str:
    """Read supported file types and return text."""

    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        text = extract_pdf_text(file_bytes)

    elif extension in {".xlsx", ".xls"}:
        text = extract_excel_text(file_bytes)

    else:
        raise ValueError(
            "Unsupported file type. "
            "Please upload a PDF or Excel file."
        )

    if not text.strip():
        raise ValueError(
            "No readable content was found in the uploaded file."
        )

    return text


def extract_products(
    file_bytes: bytes,
    filename: str
) -> ProductExtraction:
    """Extract structured products using Gemini."""

    source_text = read_source(
        file_bytes,
        filename
    )

    prompt = f"""
Extract supplier product information from the following source.

Only use information that appears in the source.

SOURCE:
-------------------------
{source_text}
-------------------------

Return the product records using the required schema.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            response_mime_type="application/json",
            response_schema=ProductExtraction,
        ),
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    try:
        return ProductExtraction.model_validate_json(
            response.text
        )
    except Exception as exc:
        raise ValueError(
            "Gemini returned invalid structured data."
        ) from exc
from pathlib import Path
import io
import time

import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from google.genai import errors

from .extraction import extract_products
from .validation import validate_products
from .logging_config import logger

app = FastAPI(
    title="AI Product Catalog & Price List Assistant",
    version="0.1.0",
)

# CORS
# Allows the React frontend on localhost:5173
# to communicate with the FastAPI backend on port 8000.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }

# Root endpoint
@app.get("/")
def root():
    return {
        "name": "AI Product Catalog & Price List Assistant",
        "status": "running",
    }

# Process supplier file
@app.post("/api/process")
async def process_file(
    file: UploadFile = File(...)
):
    start_time = time.perf_counter()
    allowed_extensions = {
        ".pdf",
        ".xlsx",
        ".xls",
    }

    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    logger.info(
        "Processing started | file=%s | type=%s",
        filename,
        extension,
    )
    if extension not in allowed_extensions:
        logger.warning(
            "Unsupported file type | file=%s | type=%s",
            filename,
            extension,
        )
        return {
            "success": False,
            "error": (
                "Unsupported file type. "
                "Please upload a PDF or Excel file."
            ),
        }
    try:
        file_bytes = await file.read()
        if not file_bytes:

            logger.warning(
                "Empty file received | file=%s",
                filename,
            )
            return {
                "success": False,
                "error": "The uploaded file is empty.",
            }
        logger.info(
            "File loaded | file=%s | bytes=%d",
            filename,
            len(file_bytes),
        )

        # AI extraction
        extracted = extract_products(
            file_bytes=file_bytes,
            filename=filename,
        )

        logger.info(
            "AI extraction completed | file=%s | products=%d",
            filename,
            len(extracted.products),
        )

        # Deterministic validation
        validated = validate_products(
            extracted.products
        )

        review_count = sum(
            1
            for product in validated
            if product["needs_review"]
        )

        valid_count = (
            len(validated) - review_count
        )

        duration = (
            time.perf_counter() - start_time
        )

        logger.info(
            (
                "Processing completed | "
                "file=%s | products=%d | "
                "valid=%d | review=%d | "
                "duration=%.2fs"
            ),
            filename,
            len(validated),
            valid_count,
            review_count,
            duration,
        )

        return {
            "success": True,
            "filename": filename,
            "total_products": len(validated),
            "valid_products": valid_count,
            "needs_review": review_count,
            "processing_seconds": round(
                duration,
                2,
            ),
            "products": validated,
        }

    except ValueError as exc:
        logger.warning(
            "Validation/input failure | file=%s | error=%s",
            filename,
            str(exc),
        )

        return {
            "success": False,
            "error": str(exc),
        }
    
    except errors.APIError as exc:
        if exc.code == 429:

            logger.warning(
                (
                    "Gemini quota/rate-limit failure | "
                    "file=%s | code=%s | message=%s"
                ),
                filename,
                exc.code,
                exc.message,
            )
            return {
                "success": False,
                "error": (
                    "The AI service is temporarily unavailable "
                    "because the Gemini request limit has been "
                    "reached. Please try again later."
                ),
            }
        logger.error(
            (
                "Gemini API failure | "
                "file=%s | code=%s | message=%s"
            ),
            filename,
            exc.code,
            exc.message,
        )
        return {
            "success": False,
            "error": (
                "The AI service could not process the file "
                "right now. Please try again later."
            ),
        }
    except Exception:
        logger.exception(
            "Unexpected processing failure | file=%s",
            filename,
        )

        return {
            "success": False,
            "error": (
                "An unexpected error occurred while "
                "processing the file."
            ),
        }
# Export validated products to Excel
@app.post("/api/export")
async def export_products(payload: dict):
    try:
        products = payload.get("products", [])

        if not products:
            return {
                "success": False,
                "error": "No products available to export."
            }

        export_columns = [
            "product_name",
            "brand",
            "uom",
            "moq",
            "price",
            "hsn",
            "needs_review",
            "review_reason",
        ]

        rows = []

        for product in products:
            rows.append({
                column: product.get(column)
                for column in export_columns
            })

        df = pd.DataFrame(rows)

        output = io.BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:
            df.to_excel(
                writer,
                index=False,
                sheet_name="Validated Products",
            )

        output.seek(0)

        return StreamingResponse(
            output,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition":
                    'attachment; filename="validated_products.xlsx"'
            },
        )

    except Exception as exc:
        logger.exception(
            "Excel export failed | error=%s",
            str(exc),
        )

        return {
            "success": False,
            "error": "Could not generate the Excel file."
        }
from fastapi import APIRouter, UploadFile, File, Form, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import EmailStr
import logging

from app.core.security import get_api_key, validate_file_size, validate_file_type
from app.core.config import settings
from app.services.data_parser import parse_sales_file
from app.services.ai_service import generate_ai_summary
from app.services.email_service import send_insight_email
from app.models.schemas import AnalyzeResponse, ErrorResponse

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file or input"},
        401: {"model": ErrorResponse, "description": "Missing API key"},
        403: {"model": ErrorResponse, "description": "Invalid API key"},
        413: {"model": ErrorResponse, "description": "File too large"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        502: {"model": ErrorResponse, "description": "Upstream service error"},
    },
    summary="Analyze Sales File & Send Email",
    description="""
Upload a CSV or XLSX sales file and provide a recipient email address.

The API will:
1. Parse and validate the uploaded file
2. Extract key statistics and metrics
3. Generate a professional executive summary using AI
4. Send the formatted report to the recipient email

**Authentication**: Include your `X-API-Key` header.  
**Rate Limit**: 10 requests per minute per IP.  
**Max File Size**: 10 MB
    """,
    tags=["Analysis"],
)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def analyze_sales(
    request: Request,
    file: UploadFile = File(..., description="CSV or XLSX sales data file"),
    recipient_email: str = Form(..., description="Email address to receive the AI-generated report"),
    api_key: str = Depends(get_api_key),
):
    # Validate email manually (pydantic EmailStr doesn't work directly as Form)
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, recipient_email):
        raise HTTPException(status_code=400, detail="Invalid email address format.")

    # Validate file
    validate_file_type(file.filename, file.content_type or "")
    
    content = await file.read()
    validate_file_size(len(content))

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    logger.info(f"Processing file: {file.filename} ({len(content)} bytes) for {recipient_email}")

    # Parse data
    data_summary = parse_sales_file(content, file.filename)

    # Generate AI summary
    ai_summary = await generate_ai_summary(data_summary)

    # Send email
    await send_insight_email(recipient_email, ai_summary, file.filename)

    # Return first 300 chars of summary as preview
    preview = ai_summary[:300] + "..." if len(ai_summary) > 300 else ai_summary

    return AnalyzeResponse(
        success=True,
        message=f"Sales insight report successfully generated and sent to {recipient_email}.",
        filename=file.filename,
        recipient=recipient_email,
        summary_preview=preview,
        data_stats={
            "rows": data_summary["total_rows"],
            "columns": data_summary["columns"],
        },
    )


@router.get(
    "/status",
    summary="Service Status",
    description="Check if the API and its dependencies are configured correctly.",
    tags=["Health"],
)
async def service_status():
    """Returns configuration status (no sensitive values exposed)."""
    return {
        "api": "operational",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_configured": bool(settings.GEMINI_API_KEY or settings.GROQ_API_KEY),
        "email_provider": settings.EMAIL_PROVIDER,
        "email_configured": bool(settings.SMTP_USER or settings.SENDGRID_API_KEY),
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
    }

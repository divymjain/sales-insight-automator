from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings
import secrets

api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)


async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key from request header."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Include X-API-Key header.",
        )
    if not secrets.compare_digest(api_key, settings.INTERNAL_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )
    return api_key


def validate_file_size(file_size: int) -> None:
    """Validate uploaded file size."""
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB.",
        )


def validate_file_type(filename: str, content_type: str) -> None:
    """Validate that uploaded file is CSV or XLSX."""
    allowed_extensions = {".csv", ".xlsx", ".xls"}
    allowed_content_types = {
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream",
    }
    
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: CSV, XLSX. Got: {ext}",
        )

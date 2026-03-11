import pandas as pd
import io
from typing import Dict, Any
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


def parse_sales_file(content: bytes, filename: str) -> Dict[str, Any]:
    """Parse CSV or XLSX file and extract sales statistics."""
    try:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        if ext == "csv":
            df = pd.read_csv(io.BytesIO(content))
        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")

        if df.empty:
            raise HTTPException(status_code=400, detail="File is empty.")

        logger.info(f"Parsed file: {filename}, rows: {len(df)}, cols: {list(df.columns)}")

        return build_summary(df, filename)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File parse error: {e}")
        raise HTTPException(status_code=422, detail=f"Could not parse file: {str(e)}")


def build_summary(df: pd.DataFrame, filename: str) -> Dict[str, Any]:
    """Build structured summary from DataFrame."""
    summary = {
        "filename": filename,
        "total_rows": len(df),
        "columns": list(df.columns),
        "preview": df.head(5).to_dict(orient="records"),
        "stats": {},
    }

    # Numeric columns analysis
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    for col in numeric_cols:
        summary["stats"][col] = {
            "total": float(df[col].sum()),
            "mean": float(df[col].mean()),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
        }

    # Categorical breakdowns
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    summary["categorical_breakdowns"] = {}
    for col in categorical_cols[:5]:  # Limit to first 5 categorical cols
        value_counts = df[col].value_counts().head(10).to_dict()
        summary["categorical_breakdowns"][col] = value_counts

    # Try to detect revenue column
    revenue_cols = [c for c in df.columns if "revenue" in c.lower() or "sales" in c.lower() or "amount" in c.lower()]
    if revenue_cols:
        rev_col = revenue_cols[0]
        summary["revenue_highlight"] = {
            "column": rev_col,
            "total": float(df[rev_col].sum()),
            "average": float(df[rev_col].mean()),
        }

    # Date range detection
    date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]
    if date_cols:
        try:
            dates = pd.to_datetime(df[date_cols[0]], errors="coerce").dropna()
            if not dates.empty:
                summary["date_range"] = {
                    "start": str(dates.min().date()),
                    "end": str(dates.max().date()),
                    "column": date_cols[0],
                }
        except Exception:
            pass

    return summary

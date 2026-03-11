import json
import logging
import httpx
from typing import Dict, Any
from fastapi import HTTPException
from app.core.config import settings

logger = logging.getLogger(__name__)


def build_prompt(data_summary: Dict[str, Any]) -> str:
    summary_json = json.dumps(data_summary, indent=2, default=str)
    return f"""You are a senior business analyst at Rabbitt AI preparing an executive briefing.

Analyze the following sales data summary and write a professional, concise executive report.

DATA SUMMARY:
{summary_json}

Write a report with these sections:
1. **Executive Overview** - 2-3 sentence high-level summary of performance
2. **Key Metrics** - Bullet points of the most important numbers (revenue, units, trends)
3. **Regional / Category Performance** - Highlights from breakdowns if available
4. **Notable Observations** - Any anomalies, standout performers, or concerns
5. **Recommended Actions** - 2-3 actionable next steps for leadership

Keep the tone professional, data-driven, and concise. Use specific numbers from the data.
Format using Markdown. Total length: 300-500 words."""


async def generate_summary_gemini(prompt: str) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(status_code=502, detail=f"AI service error (Gemini): {str(e)}")


async def generate_summary_groq(prompt: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
            "temperature": 0.4,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        raise HTTPException(status_code=502, detail=f"AI service error (Groq): {str(e)}")


async def generate_ai_summary(data_summary: Dict[str, Any]) -> str:
    prompt = build_prompt(data_summary)
    provider = settings.LLM_PROVIDER.lower()
    logger.info(f"Generating AI summary with provider: {provider}")

    if provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured.")
        return await generate_summary_gemini(prompt)
    elif provider == "groq":
        if not settings.GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured.")
        return await generate_summary_groq(prompt)
    else:
        raise HTTPException(status_code=500, detail=f"Unknown LLM provider: {provider}")
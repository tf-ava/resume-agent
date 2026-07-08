import os
from dotenv import load_dotenv

from fastapi import APIRouter, UploadFile, File, Form

from src.resume_agent.schemas import ParsedResumePdf, ResumeProfile, MatchAnalysis, AnalyzeResumeResponse
from src.resume_agent.pdf_parser.parsed_by_pymupdf4llm import parse_pdf_to_markdown
from src.resume_agent.pdf_parser.clean import clean_markdown
from src.resume_agent.llm import (
    extract_resume_profile,
    analyze_resume_job_match,
)
from src.resume_agent.cache import (
    build_analysis_cache_key,
    get_cached_analysis,
    set_cached_analysis,
)

load_dotenv()

REDIS_URL = os.getenv(
    "REDIS_URL"
)

MODEL = os.getenv(
    "MODEL"
)


router = APIRouter(
    prefix="/api",
    tags=["resume_analyze"]
)


@router.post(
    "/analyze",
    response_model=AnalyzeResumeResponse,
)
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    #读取pdf
    pdf_bytes = await file.read()

    if not REDIS_URL:
        # PDF -> Markdown
        parsed_resume = await parse_pdf_to_markdown(
            pdf_bytes=pdf_bytes,
            content_type=file.content_type
        )
        cleaned_parsed_resume = clean_markdown(parsed_resume)


        # Markdown -> ResumeProfile
        resume_profile = await extract_resume_profile(
            model=MODEL,
            prp=cleaned_parsed_resume,
        )


        # ResumeProfile + JD -> MatchAnalysis
        match_analysis = await analyze_resume_job_match(
            model=MODEL,
            rp=resume_profile,
            jd=job_description,
        )
        # 组装
        response = AnalyzeResumeResponse(
            resume_profile=resume_profile,
            match_analysis=match_analysis
        )
        return response
    else:

        #生成缓存key
        cache_key = build_analysis_cache_key(
            pdf_bytes=pdf_bytes,
            job_description=job_description,
        )

        cached_response = await get_cached_analysis(cache_key)

        if cached_response is not None:
            return cached_response
        
        # PDF -> Markdown
        parsed_resume = await parse_pdf_to_markdown(
            pdf_bytes=pdf_bytes,
            content_type=file.content_type
        )
        cleaned_parsed_resume = clean_markdown(parsed_resume)


        # Markdown -> ResumeProfile
        resume_profile = await extract_resume_profile(
            model=MODEL,
            prp=cleaned_parsed_resume,
        )


        # ResumeProfile + JD -> MatchAnalysis
        match_analysis = await analyze_resume_job_match(
            model=MODEL,
            rp=resume_profile,
            jd=job_description,
        )


        # 组装
        response = AnalyzeResumeResponse(
            resume_profile=resume_profile,
            match_analysis=match_analysis
        )

        #进入缓存
        await set_cached_analysis(
            cache_key=cache_key,
            response=response,
        )

        return response
import os
from dotenv import load_dotenv


import json
from litellm import acompletion
from pydantic import ValidationError
from fastapi import HTTPException, status

from src.resume_agent.schemas import ParsedResumePdf, ResumeProfile, MatchAnalysis
from src.resume_agent.prompt import EXTRACT_RESUME_INFO, ANALYZE_RESUME_JOB_MATCH

load_dotenv()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

BASE_URL = os.getenv(
    "BASE_URL"
)

async def extract_resume_profile(
    model: str,
    prp: ParsedResumePdf,
) -> ResumeProfile:
    messages = []
    messages.append({"role":"system", "content":EXTRACT_RESUME_INFO})
    messages.append({"role":"user", "content":prp.markdown_text})
    tools = []
    tools.append(
        {
            "type":"function",
            "function":{
                "name":"extract_resume_profile",
                "description":"Extract structured resume profile from resume markdown.Must be used when giving output",
                "parameters":ResumeProfile.model_json_schema()
            }
        }
    )
    return await _get_structured_response(model=model,
                    messages=messages,
                    tools=tools,
                    is_first_step=True)

async def analyze_resume_job_match(
    model: str,
    rp: ResumeProfile,
    jd: str,
) -> MatchAnalysis:
    messages = []
    messages.append({"role":"system", "content":ANALYZE_RESUME_JOB_MATCH})
    messages.append(
        {
            "role": "user",
            "content": (
                "以下是结构化简历信息：\n"
                f"{rp.model_dump_json(ensure_ascii=False)}\n\n"
                "以下是岗位描述：\n"
                f"{jd}"
            ),
        }
    )
    tools = []
    tools.append(
        {
            "type":"function",
            "function":{
                "name":"analyze_resume_job_match",
                "description":"Analyse the match rate between a job description and a resume.Must be used when giving output",
                "parameters":MatchAnalysis.model_json_schema()
            }
        }
    )
    return await _get_structured_response(model=model,
                    messages=messages,
                    tools=tools,
                    is_first_step=False)



async def _get_structured_response(model:str,
                    messages:list[dict],
                    tools:list[dict],
                    is_first_step:bool) -> ResumeProfile | MatchAnalysis:
    for i in range(0, 2):
        try:
            response = await acompletion(
                model=model,
                messages=messages,
                tools=tools,
                base_url=BASE_URL,
                api_key=OPENROUTER_API_KEY
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "code": "LLM_REQUEST_FAILED",
                    "message": "大模型调用失败，请稍后重试。",
                    "debug": str(e),
                },
            ) from e
        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"你必须调用工具返回结构化结果，"
                        "不要直接输出自然语言。"
                    ),
                }
            )
            continue
        raw_args = tool_calls[0].function.arguments
        try:
            data = json.loads(raw_args)
        except json.JSONDecodeError as e:
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": tool_calls,
                }
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_calls[0].id,
                    "content": (
                        "工具参数不是合法 JSON。\n"
                        f"错误信息：{str(e)}\n"
                        "请重新调用工具，并返回合法 JSON。"
                    ),
                }
            )
            continue
        try:
            if is_first_step:
                result = ResumeProfile.model_validate(data)
            else:
                result = MatchAnalysis.model_validate(data)
            return result
        except ValidationError as e:
            messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": tool_calls
                    }
            )
            messages.append(
                    {
                    "role":"tool",
                    "tool_call_id":tool_calls[0].id,
                    "content":f"""
                            工具参数没有通过 Pydantic 校验。
                            校验错误如下：
                            ```json
                            {json.dumps(e.errors(),ensure_ascii=False)}
                            请重新调用工具，并严格符合 schema。"""
                    }
            )
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail={
            "code": "LLM_STRUCTURED_OUTPUT_FAILED",
            "message": "模型未能返回符合要求的结构化结果，请稍后重试。",
        }
    )
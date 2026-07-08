from pydantic import BaseModel, Field

class ParsedResumePdf(BaseModel):
    markdown_text: str = Field(default=None, description="由pymupdf4llm从pdf中解析出来的Markdown文本")

from pydantic import BaseModel, Field


class ResumeProfile(BaseModel):
    name: str | None = Field(default=None, description="姓名")
    phone: str | None = Field(default=None, description="电话")
    email: str | None = Field(default=None, description="邮箱")
    address: str | None = Field(default=None, description="地址")

    job_intention: str | None = Field(default=None, description="求职意向")
    expected_salary: str | None = Field(default=None, description="期望薪资")

    years_of_experience: str | None = Field(default=None, description="工作年限")
    education_background: str | None = Field(default=None, description="学历背景")
    project_experience: list[str] = Field(default_factory=list, description="项目经历")
    skills: list[str] = Field(default_factory=list, description="技能列表")


class MatchAnalysis(BaseModel):
    skill_match_score: int = Field(
        ge=0,
        le=100,
        description="技能匹配率，0-100"
    )

    experience_relevance_score: int = Field(
        ge=0,
        le=100,
        description="工作经验相关性评分，0-100"
    )

    overall_relevance_score: int = Field(
        ge=0,
        le=100,
        description="总相关性评分，0-100"
    )

    summary: str = Field(description="匹配分析总结")


class AnalyzeResumeResponse(BaseModel):
    resume_profile: ResumeProfile | None = Field(default=None, description="简历结构化信息")
    match_analysis: MatchAnalysis | None = Field(default=None, description="匹配分析结果")
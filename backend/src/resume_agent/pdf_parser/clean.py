import re

from src.resume_agent.schemas import ParsedResumePdf


def clean_markdown(psp: ParsedResumePdf) -> ParsedResumePdf:
    """
    Clean markdown extracted by pymupdf4llm.
    """

    md = psp.markdown_text

    # 统一换行
    md = md.replace("\r\n", "\n")


    # 删除连续空行
    md = re.sub(
        r"\n{3,}",
        "\n\n",
        md
    )


    # 删除行尾空格
    md = "\n".join(
        line.rstrip()
        for line in md.splitlines()
    )


    # 删除孤立 bullet
    md = re.sub(
        r"^\s*[-•]\s*$",
        "",
        md,
        flags=re.MULTILINE
    )


    return ParsedResumePdf(
        markdown_text=md.strip()
    )
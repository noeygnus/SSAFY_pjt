import ast
import json
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


load_dotenv()


def run_llm(prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5-nano")

    if not api_key:
        return "[오류 발생] OPENAI_API_KEY가 설정되지 않았습니다."

    llm = init_chat_model(
        model,
        model_provider="openai",
        api_key=api_key,
    )

    result = llm.invoke(
        [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    return result.content

def filter_inappropriate(comments):
    if not comments:
        return []

    numbered_comments = "\n".join(
        f"{index}. {comment}" for index, comment in enumerate(comments)
    )

    prompt = f"""
다음 댓글 목록에서 부적절한 댓글(욕설, 혐오, 비방, 선정성, 과도한 비난 등)의 번호만 반환해줘.
응답은 반드시 이 형식만 사용해줘: [0, 2, 5] 또는 []
다른 설명이나 마크다운 없이 배열만 반환해줘.

댓글 목록:
{numbered_comments}
"""

    response = run_llm(prompt).strip()

    if response.startswith("[오류 발생]"):
        return comments

    try:
        remove_indexes = json.loads(response)
    except json.JSONDecodeError:
        return comments

    remove_indexes = sorted(
        set(
            int(index)
            for index in remove_indexes
            if isinstance(index, int) and 0 <= index < len(comments)
        ),
        reverse=True,
    )

    filtered = comments[:]

    for index in remove_indexes:
        filtered.pop(index)

    return filtered


def augment_comments(cleaned_comments):
    if not cleaned_comments:
        return []

    prompt = f"""
아래 댓글 리스트의 각 문장을 의미는 유지하면서 다른 표현으로 바꿔줘.

조건:
- 입력 댓글 개수와 출력 댓글 개수를 같게 유지해줘.
- 출력은 반드시 Python 리스트 형태로만 해줘.
- 설명, 마크다운, 코드블록은 쓰지 마.

댓글 리스트:
{cleaned_comments}
"""

    response = run_llm(prompt).strip()

    if response.startswith("[오류 발생]"):
        return []

    try:
        augmented = ast.literal_eval(response)
    except (ValueError, SyntaxError):
        return []

    if not isinstance(augmented, list):
        return []

    return augmented


def summarize_comments(comments):
    if not comments:
        return ""

    prompt = f"""
아래 댓글 목록을 보고 전체 분위기와 주요 내용을 3문장 이내로 요약해줘.

댓글 목록:
{comments}
"""

    response = run_llm(prompt).strip()

    if response.startswith("[오류 발생]"):
        return ""

    return response
from django.conf import settings
from openai import OpenAI


ANALYSIS_SYSTEM_PROMPT = """
당신은 금융 커뮤니티 사용자의 게시글과 댓글을 바탕으로 투자 성향을 분석하는 한국어 어시스턴트입니다.
입력으로 제공된 활동 내용만 근거로 삼고, 실제 투자 조언이나 매수/매도 지시는 하지 마세요.

출력은 아래 형식을 지켜 한국어로 작성하세요.

1. 투자 성향 요약: 한 문장
2. 주요 관심 자산: 2~4개 항목
3. 위험 선호도: 보수적 / 중립적 / 적극적 중 하나와 근거
4. 커뮤니티 활동 특징: 2~3개 항목
5. 참고하면 좋은 점: 교육 목적의 일반적인 제안 2개

분석 근거가 부족하면 억지로 결론을 내리지 말고, 부족한 이유와 추가로 필요한 활동 예시를 알려주세요.
"""

MIN_ANALYSIS_CHARS = 80


def _build_llm_client():
    mode = (getattr(settings, "MODE", "OPENAI") or "OPENAI").strip().upper()

    if mode == "UPSTAGE":
        api_key = (getattr(settings, "UPSTAGE_API_KEY", "") or "").strip()
        if not api_key:
            return None, None, "UPSTAGE_API_KEY가 설정되어 있지 않습니다."
        client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1/solar")
        return client, getattr(settings, "UPSTAGE_MODEL", "solar-mini"), None

    api_key = (getattr(settings, "OPENAI_API_KEY", "") or "").strip()
    if not api_key:
        return None, None, "OPENAI_API_KEY가 설정되어 있지 않습니다."
    client = OpenAI(api_key=api_key)
    return client, getattr(settings, "OPENAI_MODEL", "gpt-5-nano"), None


def build_activity_text(posts, comments):
    sections = []
    for post in posts:
        sections.append(f"[게시글] 제목: {post.title}\n내용: {post.content}")
    for comment in comments:
        sections.append(f"[댓글] 게시글: {comment.post.title}\n내용: {comment.content}")
    return "\n\n".join(sections).strip()


def analyze_investment_profile(posts, comments):
    activity_text = build_activity_text(posts, comments)
    if len(activity_text) < MIN_ANALYSIS_CHARS:
        return {
            "ok": False,
            "message": "분석에 필요한 게시글이나 댓글 내용이 부족합니다. 관심 자산에 대한 의견을 조금 더 작성한 뒤 다시 시도해 주세요.",
        }

    client, model, error = _build_llm_client()
    if error:
        return {"ok": False, "message": error}

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": activity_text[:6000]},
            ],
        )
        content = (response.choices[0].message.content or "").strip()
        if not content:
            return {"ok": False, "message": "분석 결과가 비어 있습니다. 잠시 후 다시 시도해 주세요."}
        return {"ok": True, "message": content}
    except Exception as exc:
        return {
            "ok": False,
            "message": f"투자 성향 분석 중 오류가 발생했습니다. ({type(exc).__name__})",
        }

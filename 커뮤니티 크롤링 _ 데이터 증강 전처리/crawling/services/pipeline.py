from crawling.models import CrawlingResult
from .toss_crawler import fetch_comments
from .llm import filter_inappropriate, augment_comments, summarize_comments
from .preprocess import clean_comments


def run_crawling_pipeline(company_name):
    # 1. 크롤링
    crawling_data = fetch_comments(company_name, limit=20)

    matched_company_name = crawling_data.get("matched_company_name", "")
    stock_code = crawling_data.get("stock_code", "")
    raw_comments = crawling_data.get("raw_comments", [])

    if not raw_comments:
        result = CrawlingResult.objects.create(
            input_company_name=company_name,
            matched_company_name=matched_company_name,
            stock_code=stock_code,
            raw_comments=[],
            cleaned_comments=[],
            augmented_comments=[],
            iqr_info={},
            summary="댓글 데이터를 수집하지 못했습니다.",
        )
        return result

    # 2. LLM 기반 부적절 댓글 제거
    appropriate_comments = filter_inappropriate(raw_comments)

    # 3. 일반 전처리
    cleaned_comments, iqr_info = clean_comments(appropriate_comments)

    # 4. LLM 데이터 증강
    augmented_comments = augment_comments(cleaned_comments)

    # 5. 요약 생성
    summary = summarize_comments(cleaned_comments)

    # 6. DB 저장
    result = CrawlingResult.objects.create(
        input_company_name=company_name,
        matched_company_name=matched_company_name,
        stock_code=stock_code,
        raw_comments=raw_comments,
        cleaned_comments=cleaned_comments,
        augmented_comments=augmented_comments,
        iqr_info=iqr_info,
        summary=summary,
    )

    return result
from django.db import models


class CrawlingResult(models.Model):
    input_company_name = models.CharField(
        max_length=100,
        verbose_name="입력 회사명",
    )

    matched_company_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="실제 매칭 종목명",
    )

    stock_code = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="종목 코드",
    )

    raw_comments = models.JSONField(
        default=list,
        verbose_name="원본 댓글 목록",
    )

    cleaned_comments = models.JSONField(
        default=list,
        verbose_name="정제 댓글 목록",
    )

    augmented_comments = models.JSONField(
        default=list,
        verbose_name="증강 댓글 목록",
    )

    iqr_info = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="IQR 임계값 정보",
    )

    summary = models.TextField(
        blank=True,
        verbose_name="댓글 요약",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성 일시",
    )

    removed_count = models.IntegerField(default=0)
    inappropriate_removed_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.input_company_name} - {self.created_at:%Y-%m-%d %H:%M}"
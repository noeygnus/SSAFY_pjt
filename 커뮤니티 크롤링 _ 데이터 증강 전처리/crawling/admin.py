from django.contrib import admin
from .models import CrawlingResult


@admin.register(CrawlingResult)
class CrawlingResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "input_company_name",
        "matched_company_name",
        "stock_code",
        "created_at",
    )
    search_fields = (
        "input_company_name",
        "matched_company_name",
        "stock_code",
    )
    readonly_fields = ("created_at",)
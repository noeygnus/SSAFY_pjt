from django.shortcuts import render

from .forms import CompanySearchForm
from .services.pipeline import run_crawling_pipeline


def index(request):
    form = CompanySearchForm()

    return render(
        request,
        "crawling/index.html",
        {
            "form": form,
        },
    )


def result(request):
    if request.method != "POST":
        form = CompanySearchForm()
        return render(
            request,
            "crawling/index.html",
            {
                "form": form,
            },
        )

    form = CompanySearchForm(request.POST)

    if not form.is_valid():
        return render(
            request,
            "crawling/index.html",
            {
                "form": form,
            },
        )

    company_name = form.cleaned_data["company_name"]

    try:
        crawling_result = run_crawling_pipeline(company_name)

        return render(
            request,
            "crawling/result.html",
            {
                "result": crawling_result,
            },
        )

    except Exception as error:
        return render(
            request,
            "crawling/index.html",
            {
                "form": form,
                "error_message": f"처리 중 오류가 발생했습니다: {error}",
            },
        )
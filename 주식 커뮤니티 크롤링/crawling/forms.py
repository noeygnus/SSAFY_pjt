from django import forms


class CompanySearchForm(forms.Form):
    company_name = forms.CharField(
        label="회사명",
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "예: 삼성전자",
                "class": "company-input",
            }
        ),
    )

    def clean_company_name(self):
        company_name = self.cleaned_data["company_name"].strip()

        if not company_name:
            raise forms.ValidationError("회사명을 입력해주세요.")

        return company_name
import re
import pandas as pd


def clean_comments(comments):
    if not comments:
        return [], {}

    df = pd.DataFrame(comments, columns=["comment"])

    # 결측치/공백 제거
    df = df.dropna(subset=["comment"])
    df["comment"] = df["comment"].astype(str).str.strip()
    df = df[df["comment"] != ""]

    # 특수문자 제거: 한글, 영어, 숫자, 공백만 유지
    df["clean"] = df["comment"].apply(
        lambda text: re.sub(r"[^가-힣a-zA-Z0-9\s]", "", text)
    )
    df["clean"] = df["clean"].str.replace(r"\s+", " ", regex=True).str.strip()

    # 의미 없는 패턴 제거
    cond_numeric = df["clean"].str.match(r"^\d+$")
    cond_repeat = df["clean"].str.match(r"^[ㅋㅎ]+$")
    cond_english = df["clean"].str.match(r"^[A-Za-z\s]+$")
    cond_none = df["clean"].str.lower() == "none"

    df = df[~(cond_numeric | cond_repeat | cond_english | cond_none)]

    # 길이 기반 IQR 이상치 제거
    df["length"] = df["clean"].str.len()

    iqr_info = {}

    if len(df) >= 5:
        q1 = df["length"].quantile(0.25)
        q3 = df["length"].quantile(0.75)
        iqr = q3 - q1
        lower = max(5, q1 - 1.5 * iqr)
        upper = q3 + 1.5 * iqr

        iqr_info = {
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "lower": lower,
            "upper": upper,
        }

        df = df[(df["length"] >= lower) & (df["length"] <= upper)]
    else:
        df = df[df["length"] >= 3]
        iqr_info = {
            "message": "데이터 수가 적어 IQR 대신 3자 이상 기준 적용",
        }

    cleaned_comments = df["clean"].tolist()

    return cleaned_comments, iqr_info
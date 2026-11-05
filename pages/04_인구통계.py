
from pathlib import Path
import pandas as pd
import streamlit as st

# 현재 파일 위치
BASE_DIR = Path(__file__).resolve().parent

# CSV 파일을 찾을 위치
possible_paths = [
    BASE_DIR / "population_utf8.csv",
    BASE_DIR.parent / "population_utf8.csv",
    BASE_DIR / "population.csv",
    BASE_DIR.parent / "population.csv",
    Path.cwd() / "population_utf8.csv",
    Path.cwd() / "population.csv"
]

# 실제 파일 찾기
CSV_PATH = next(
    (path for path in possible_paths if path.is_file()),
    None
)

@st.cache_data
def load_data():

    if CSV_PATH is None:
        st.error("CSV 파일을 찾을 수 없습니다.")
        st.write("확인한 폴더:", str(BASE_DIR))
        st.write("현재 작업 폴더:", str(Path.cwd()))
        st.write("확인한 경로:")

        for path in possible_paths:
            st.write(str(path))

        st.stop()

    try:
        return pd.read_csv(
            CSV_PATH,
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:
        return pd.read_csv(
            CSV_PATH,
            encoding="cp949"
        )

df = load_data()

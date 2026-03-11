import streamlit as st
from kiwipiepy import Kiwi
import requests

# 1. 페이지 설정
st.set_page_config(page_title="Jerboa Infinite Engine", page_icon="🐦")

@st.cache_resource
def load_all():
    kiwi = Kiwi()
    # 한국어 명사 리스트 (더 안정적인 주소로 변경했어)
    url = "https://raw.githubusercontent.com/monologg/korean-wordlist/master/nouns.txt"
    try:
        res = requests.get(url)
        # 공백 제거하고 리스트화
        full_dict = [w.strip() for w in res.text.split('\n') if len(w.strip()) > 1]
        full_dict = list(set(full_dict)) # 중복 제거
        full_dict.sort()
    except:
        # 실패 시 니치한 기본 사전 (이물의 취향 반영)
        full_dict = sorted(["심연", "권태", "알바트로스", "오브제", "몽유병", "유령", "해부대", "재봉틀"])
    return kiwi, full_dict

kiwi, NOUN_DICT = load_all()

st.title("🐦 저보아 무한 울리포 엔진")

# --- 진단 모드 (이거 보면 왜 안 변하는지 알 수 있어!) ---
with st.expander("🔍 엔진 상태 확인 (진단용)"):
    st.write(f"현재 사전 단어 수: **{len(NOUN_DICT):,}개**")
    st.write("사전 앞부분 예시:", NOUN_DICT[:10])
    test_word = st.text_input("사전에 이 단어가 있는지 확인:", value="예술")
    if test_word in NOUN_DICT:
        st.success(f"'{test_word}'가 사전에 있습니다!")
    else:
        st.error(f"'{test_word}'가 사전에 없습니다. 그래서 안 바뀌는 거야!")
# --------------------------------------------------

def s_plus_n_engine(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    last_end = 0
    for token in tokens:
        result.append(text[last_end:token.start])
        # 명사(NNG, NNP)를 찾아서 치환
        if token.tag in ['NNG', 'NNP']:
            if token.form in NOUN_DICT:
                idx = NOUN_DICT.index(token.form)
                result.append(NOUN_DICT[(idx + n) % len(NOUN_DICT)])

import streamlit as st
from kiwipiepy import Kiwi
import os

st.set_page_config(page_title="Jerboa Master Engine", page_icon="🐦")

@st.cache_resource
def load_jerboa_dict():
    kiwi = Kiwi()
    # 깃허브에 직접 올린 nouns.txt만 믿고 갑니다.
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            # 404 같은 쓰레기 텍스트가 섞이지 않게 필터링 로직 추가
            lines = f.readlines()
            words = [l.strip() for l in lines if len(l.strip()) > 1 and "404" not in l]
    else:
        # 파일이 없을 때를 대비한 최소한의 예술적 안전망
        words = ["심연", "권태", "알바트로스", "오브제", "인생", "예술"]
    
    words.sort()
    return kiwi, words

kiwi, NOUN_DICT = load_jerboa_dict()

st.title("🐦 저보아: 국가 공인(?) 무한 엔진")
st.write(f"현재 엔진에 장전된 단어: **{len(NOUN_DICT)}개**")

# 진단 모드 (사전 내용 직접 확인)
with st.expander("🔍 현재 사전 단어 목록 보기"):
    st.write(", ".join(NOUN_DICT))

# (치환 로직 부분)
def oulipo_process(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    last_end = 0
    for token in tokens:
        result.append(text[last_end:token.start])
        if token.tag in ['NNG', 'NNP'] and token.form in NOUN_DICT:
            idx = NOUN_DICT.index(token.form)
            result.append(NOUN_DICT[(idx + n) % len(NOUN_DICT)])
        else:
            result.append(token.form)
        last_end = token.end
    result.append(text[last_end:])
    return "".join(result)

shift_n = st.sidebar.slider("치환 간격 (S+n)", 1, 20, 7)
user_input = st.text_area("문장을 입력하세요:", height=150)

if st.button("변환 실행"):
    if user_input:
        output = oulipo_process(user_input, shift_n)
        st.success(output)

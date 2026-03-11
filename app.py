import streamlit as st
from kiwipiepy import Kiwi
import os

st.set_page_config(page_title="Jerboa Infinite Engine", page_icon="🐦")

@st.cache_resource
def load_perfect_dict():
    kiwi = Kiwi()
    # 깃허브에 올린 우리의 5만 단어장을 읽어와
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if len(line.strip()) > 1]
    else:
        # 혹시 파일이 없을 때를 대비한 비상용
        words = ["심연", "권태", "알바트로스", "오브제", "해부대", "재봉틀"]
    
    words.sort()
    return kiwi, words

kiwi, NOUN_DICT = load_perfect_dict()

st.title("🐦 저보아: 무한 울리포 엔진")
st.write(f"현재 엔진에 장전된 단어: **{len(NOUN_DICT):,}개**")

def s_plus_n_final(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    last_end = 0
    for token in tokens:
        result.append(text[last_end:token.start])
        if token.tag in ['NNG', 'NNP'] and token.form in NOUN_DICT:
            idx = NOUN_DICT.index(token.form)
            # n만큼 뒤의 단어로 치환 (리스트 크기를 넘어가면 다시 처음으로)
            result.append(NOUN_DICT[(idx + n) % len(NOUN_DICT)])
        else:
            result.append(token.form)
        last_end = token.end
    result.append(text[last_end:])
    return "".join(result)

shift_n = st.sidebar.slider("치환 간격 (S + n)", 1, 1000, 7)
user_input = st.text_area("해체할 문장을 입력하세요:", height=150)

if st.button("무한 변환 실행"):
    if user_input:
        output = s_plus_n_final(user_input, shift_n)
        st.markdown("### ✨ 변환 결과")
        st.success(output)
    else:
        st.warning("문장을 입력해 줘, 이물.")

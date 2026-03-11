import streamlit as st
from kiwipiepy import Kiwi
import random
import os
import re

# --- 1. 페이지 설정 & 스타일 (기존 스타일 계승) ---
st.set_page_config(page_title="Jerboa Circle", layout="wide")

st.markdown("""
<style>
    :root { color-scheme: light !important; }
    [data-testid="stAppViewContainer"], .stApp { background-color: #FFFFFF !important; }
    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    }
    h1 {
        font-family: 'Trattatello', 'Apple Chancery', cursive !important;
        font-size: 3.8rem !important; color: #000; text-align: center;
    }
    * { font-family: 'Eulyoo1945-Regular', serif !important; color: #000; }
    
    /* 해부대 입력창 */
    textarea {
        background-color: #111 !important; color: #FFF !important;
        border: 2px solid #000 !important; font-size: 1.1rem !important;
    }
    
    /* 활자 해부기 타일 스타일 */
    .dissector-node {
        display: inline-block; padding: 5px 10px; margin: 4px;
        border: 1px solid #000; font-weight: bold; cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

@st.cache_data
def load_oulipo_dict():
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return ["거울", "파편", "심연", "공백", "기억", "망각", "미학"]
NOUN_DICT = load_oulipo_dict()

# --- 2. 메인 타이틀 ---
st.title("Jerboa Circle: Surrealist Workshop")

# --- 3. 탭 구성 ---
tab1, tab2 = st.tabs(["🏺 Oulipo Engine (S+N)", "🔪 The Dissector (활자 해부)"])

# ---------------------------------------------------------
# TAB 1: 기존 Oulipo Engine (S+N)
# ---------------------------------------------------------
with tab1:
    st.markdown("### [울리포 엔진 가동]")
    user_input_1 = st.text_area("해부대 (S+N)", placeholder="문장을 입력하세요.", height=150, key="input1")
    
    c1, c2 = st.columns(2)
    shift_val = c1.slider("S+N 거리", 1, 100, 7)
    prob_val = c2.slider("변환 확률 (%)", 0, 100, 100)

    # (기존 transform_with_logic 함수 로직 생략 - 기존 코드 그대로 사용 가능)
    if st.button("✨ 문장 재단하기", key="btn1"):
        # 기존 변환 로직 및 시각화 코드 실행
        st.write("변환된 결과가 여기에 표시됩니다 (기존 로직 적용)")

# ---------------------------------------------------------
# TAB 2: 신규 활자 해부기 (Dissector)
# ---------------------------------------------------------
with tab2:
    st.markdown("### [활자 해부기: 조사의 성역화]")
    
    if 'fragments' not in st.session_state: st.session_state.fragments = []
    if 'locked_indices' not in st.session_state: st.session_state.locked_indices = set()

    user_input_2 = st.text_area("해부대 (재배치)", placeholder="조사를 클릭해 고정하고 나머지를 섞으세요.", height=150, key="input2")

    col_a, col_b = st.columns(2)
    if col_a.button("🧪 활자 추출"):
        # 공백을 포함한 모든 글자를 파편화
        st.session_state.fragments = list(user_input_2)
        st.session_state.locked_indices = set()

    if col_b.button("🔀 파편 재배치 (고정 제외)"):
        if st.session_state.fragments:
            indices = list(range(len(st.session_state.fragments)))
            non_locked_indices = [i for i in indices if i not in st.session_state.locked_indices]
            
            # 고정되지 않은 글자들만 추출해서 셔플
            non_locked_chars = [st.session_state.fragments[i] for i in non_locked_indices]
            random.shuffle(non_locked_chars)
            
            # 다시 제자리에 끼워넣기
            new_fragments = list(st.session_state.fragments)
            for i, char in zip(non_locked_indices, non_locked_chars):
                new_fragments[i] = char
            st.session_state.fragments = new_fragments

    st.divider()

    # 인터랙티브 해부대
    if st.session_state.fragments:
        st.write("클릭하여 고정(검은색) / 해제(흰색):")
        
        # Streamlit에서 개별 클릭을 받기 위해 버튼들을 나열 (반응형 위해 flex 처리 권장)
        # 여기서는 간단히 나열하지만, 실제로는 CSS와 엮어 타일처럼 보이게 함
        cols = st.columns(min(len(st.session_state.fragments), 20)) 
        
        for i, char in enumerate(st.session_state.fragments):
            char_display = char if char != " " else "⎵"
            is_locked = i in st.session_state.locked_indices
            
            # 버튼 스타일을 이용해 '고정' 상태 표시
            button_type = "primary" if is_locked else "secondary"
            if st.button(char_display, key=f"fragment_{i}", type=button_type):
                if is_locked: st.session_state.locked_indices.remove(i)
                else: st.session_state.locked_indices.add(i)
                st.rerun()

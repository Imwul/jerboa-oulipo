import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Jerboa Oulipo Engine", page_icon="🐦")
API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"

@st.cache_resource
def load_fail_safe_resources():
    kiwi = Kiwi()
    
    # 1. 절대 실패 없는 니치 사전 (인터넷 안 돼도 작동)
    # 우리 서클의 정체성을 담은 단어들이야.
    base_dict = [
        "심연", "권태", "알바트로스", "오브제", "몽유병", "유령", "해부대", "재봉틀", 
        "우산", "마네킹", "자동기술", "무의식", "초현실", "파편", "공백", "소멸", 
        "기억", "퍼즐", "레디메이드", "몽타주", "단절", "우연", "구조", "필연", 
        "미궁", "거울", "나르시스", "에로스", "밤", "향기", "음울", "태양", 
        "검은색", "몰락", "환각", "침묵", "안개", "안주", "예술", "인생",
        "보들레르", "초현실주의", "누보로망", "페렉", "키냐르", "조각", "설치"
    ]
    
    # 2. 더 강력한 외부 사전 연결 시도
    # 이번엔 404가 나면 아예 무시하도록 로직을 짰어.
    try:
        url = "https://raw.githubusercontent.com/monologg/korean-wordlist/master/nouns.txt"
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and "404" not in res.text[:100]:
            ext_words = [w.strip() for w in res.text.split('\n') if len(w.strip()) > 1]
            base_dict = list(set(base_dict + ext_words))
    except:
        pass # 실패하면 그냥 우리 니치 사전만 써!
        
    base_dict.sort()
    return kiwi, base_dict

kiwi, NOUN_DICT = load_fail_safe_resources()

st.title("🐦 저보아: 무한 울리포 엔진")
st.write(f"현재 엔진에 장전된 단어: **{len(NOUN_DICT):,}개**")

# --- 진단 모드 ---
with st.expander("🔍 엔진 상태 실시간 점검"):
    st.write("사전 시작 부분:", NOUN_DICT[:15])
    test_w = st.text_input("단어 존재 확인:", "사랑")
    if test_w in NOUN_DICT:
        st.success(f"'{test_w}'가 사전에 로드되었습니다!")
    else:
        st.error(f"'{test_w}'가 아직 사전에 없습니다.")

# --- 치환 로직 ---
def s_plus_n_ultimate(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    last_end = 0
    for token in tokens:
        result.append(text[last_end:token.start])
        if token.tag in ['NNG', 'NNP']:
            if token.form in NOUN_DICT:
                idx = NOUN_DICT.index(token.form)
                # n만큼 이동 (순환 구조)
                result.append(NOUN_DICT[(idx + n) % len(NOUN_DICT)])
            else:
                result.append(token.form)
        else:
            result.append(token.form)
        last_end = token.end
    result.append(text[last_end:])
    return "".join(result)

shift_n = st.sidebar.slider("치환 간격 (S + n)", 1, 100, 7)
user_input = st.text_area("해체할 문장을 입력하세요:", height=150)

if st.button("무한 엔진 가동"):
    if user_input:
        output = s_plus_n_ultimate(user_input, shift_n)
        st.markdown("### ✨ 변환 결과")
        st.success(output)
    else:
        st.warning("문장을 넣어줘, 이물!")

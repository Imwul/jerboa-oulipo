import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="Jerboa Infinite Engine", page_icon="🐦")

# 1. 국립국어원 API 키 (이물이 발급받은 키)
API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"

@st.cache_resource
def load_vast_ocean():
    kiwi = Kiwi()
    # 비상용 니치 사전
    base_words = ["심연", "권태", "알바트로스", "오브제", "몽유병", "유령", "해부대", "재봉틀", "초현실", "예술", "인생", "사랑"]
    
    # 다중 외부 주소 시도
    mirrors = [
        "https://raw.githubusercontent.com/naver/korean-wordlist/master/nouns.txt",
        "https://raw.githubusercontent.com/monologg/korean-wordlist/master/nouns.txt"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    final_set = set(base_words)
    success_msg = "⚠️ 외부 연결 실패, 로컬 모드 가동"

    for url in mirrors:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                words = [w.strip() for w in r.text.split('\n') if len(w.strip()) > 1]
                if words and "404" not in words[0]:
                    final_set.update(words)
                    success_msg = f"✅ 외부 연결 성공! ({len(words):,}개 로드)"
                    break
        except:
            continue
            
    return kiwi, sorted(list(final_set)), success_msg

# 여기서 괄호가 잘 닫혔는지 꼭 확인해!
kiwi, NOUN_DICT, status = load_vast_ocean()

st.title("🐦 저보아: 무한 울리포 엔진")
st.sidebar.info(status) # <-- 바로 이 부분이야, 이물!
st.write(f"현재 엔진에 장전된 단어: **{len(NOUN_DICT):,}개**")

def oulipo_logic(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    last_end = 0
    for token in tokens:
        result.append(text[last_end:token.start])
        if token.tag in ['NNG', 'NNP']:
            if token.form in NOUN_DICT:
                idx = NOUN_DICT.index(token.form)
                result.append(NOUN_DICT[(idx + n) % len(NOUN_DICT)])
            else:
                result.append(token.form)
        else:
            result.append(token.form)
        last_end = token.end
    result.append(text[last_end:])
    return "".join(result)

shift_n = st.sidebar.slider("치환 간격 (n)", 1, 1000, 7)
user_input = st.text_area("해체할 문장을 입력하세요:", height=150)

if st.button("무한 변환 실행"):
    if user_input:
        output = oulipo_logic(user_input, shift_n)
        st.success(output)

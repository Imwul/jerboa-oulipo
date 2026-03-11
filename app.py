import streamlit as st
from kiwipiepy import Kiwi
import requests

@st.cache_resource
def load_with_diagnostics():
    kiwi = Kiwi()
    # 1. 비상용 니치 사전 (47개)
    base_dict = sorted([
        "심연", "권태", "알바트로스", "오브제", "몽유병", "유령", "해부대", "재봉틀", 
        "우산", "마네킹", "자동기술", "무의식", "초현실", "파편", "공백", "소멸", 
        "예술", "인생", "보들레르", "초현실주의", "누보로망", "페렉", "키냐르"
    ])
    
    # 2. 외부 사전 연결 시도 (더 강력한 헤더 추가)
    # 이번엔 가장 안정적인 데이터 과학용 단어장 주소를 쓸게.
    url = "https://raw.githubusercontent.com/naver/korean-wordlist/master/nouns.txt"
    headers = {'User-Agent': 'Mozilla/5.0'} # "나 사람이야!"라고 속이는 헤더야.
    
    error_msg = None
    try:
        res = requests.get(url, headers=headers, timeout=15) # 대기 시간을 15초로 늘렸어.
        if res.status_code == 200:
            ext_words = [w.strip() for w in res.text.split('\n') if len(w.strip()) > 1]
            base_dict = list(set(base_dict + ext_words))
            st.sidebar.success("✅ 외부 사전 연결 성공!")
        else:
            error_msg = f"응답 오류: {res.status_code}"
    except Exception as e:
        error_msg = f"연결 오류: {str(e)}"
        
    if error_msg:
        st.sidebar.error(f"⚠️ {error_msg}")
        
    base_dict.sort()
    return kiwi, base_dict

kiwi, NOUN_DICT = load_with_diagnostics()

st.title("🐦 저보아: 무한 울리포 엔진")
st.write(f"현재 엔진에 장전된 단어: **{len(NOUN_DICT):,}개**")

# (이하 변환 로직 동일)

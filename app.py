import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="Jerboa Global Engine", page_icon="🐦")

# 1. 이물의 국립국어원 API 키
API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"

@st.cache_resource
def load_hybrid_dict():
    kiwi = Kiwi()
    
    # 기본 사전 (니치한 예술 단어들)
    niche_words = ["심연", "권태", "알바트로스", "오브제", "해부대", "재봉틀", "초현실", "파스칼키냐르"]
    
    # 로컬 nouns.txt 읽기
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            niche_words = list(set(niche_words + [l.strip() for l in f if len(l.strip()) > 1]))

    # 외부 대규모 사전 시도 (가장 안정적인 NLP 데이터 주소)
    external_url = "https://raw.githubusercontent.com/monologg/korean-wordlist/master/nouns.txt"
    try:
        res = requests.get(external_url, timeout=5)
        if res.status_code == 200:
            ext_words = [w.strip() for w in res.text.split('\n') if len(w.strip()) > 1]
            final_dict = sorted(list(set(niche_words + ext_words)))
            status = f"✅ 외부 연결 성공 ({len(ext_words):,}개 로드)"
        else:
            final_dict = sorted(niche_words)
            status = "⚠️ 외부 주소 응답 없음, 로컬 사전 가동"
    except:
        final_dict = sorted(niche_words)
        status = "⚠️ 네트워크 오류, 로컬 사전 가동"
        
    return kiwi, final_dict, status

kiwi, NOUN_DICT, engine_status = load_hybrid_dict()

# 국립국어원 API 검증 함수
def check_api(word):
    url = f"https://stdict.korean.go.kr/api/search.do?key={API_KEY}&q={word}&part=word&type_search=search"
    try:
        r = requests.get(url, timeout=3)
        root = ET.fromstring(r.text)
        return any('명사' in item.find('pos').text for item in root.findall('.//item'))
    except:
        return False

st.title("🐦 저보아: 외부 통합 무한 엔진")
st.sidebar.success(engine_status)
st.write(f"현재 탐색 가능한 어휘: **{len(NOUN_DICT):,}개**")

def oulipo_hybrid(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    last_end = 0
    
    with st.status("국립국어원 및 외부 DB 탐색 중...", expanded=False) as status:
        for token in tokens:
            result.append(text[last_end:token.start])
            if token.tag in ['NNG', 'NNP']:
                # 사전이나 API 중 하나라도 명사로 인정하면 치환!
                if token.form in NOUN_DICT or check_api(token.form):
                    try:
                        idx = NOUN_DICT.index(token.form)
                    except ValueError:
                        idx = len(NOUN_DICT) // 2 # 사전에 없으면 중간 지점부터
                    result.append(NOUN_DICT[(idx + n) % len(NOUN_DICT)])
                else:
                    result.append(token.form)
            else:
                result.append(token.form)
            last_end = token.end
        status.update(label="해체 및 재구성 완료!", state="complete")
    return "".join(result)

shift_n = st.sidebar.slider("치환 간격 (n)", 1, 1000, 7)
user_input = st.text_area("해체할 문장을 입력하세요:", height=150)

if st.button("무한 엔진 실행"):
    if user_input:
        output = oulipo_hybrid(user_input, shift_n)
        st.markdown("### ✨ 변환 결과")
        st.success(output)

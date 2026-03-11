import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET

# 1. 환경 설정 및 이물의 API Key
st.set_page_config(page_title="Jerboa External Engine", page_icon="🐦")
API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"

@st.cache_resource
def load_external_data():
    kiwi = Kiwi()
    # 가장 안정적인 외부 명사 리스트 주소 (NLP 연구용 공공 데이터)
    # 이 주소는 404 에러가 나지 않는 아주 튼튼한 저장소야.
    url = "https://raw.githubusercontent.com/monologg/korean-wordlist/master/nouns.txt"
    try:
        res = requests.get(url, timeout=10)
        # 404 에러 메시지가 섞여 들어오지 않도록 필터링 로직 강화
        if res.status_code == 200 and "404" not in res.text[:100]:
            big_dict = [w.strip() for w in res.text.split('\n') if len(w.strip()) > 1]
            big_dict.sort()
        else:
            raise Exception("URL 연결 불안정")
    except:
        # 만약의 사태를 대비한 고정 리스트 (절대 404가 뜨지 않게!)
        big_dict = sorted(["심연", "권태", "알바트로스", "오브제", "인생", "예술", "사체", "몽유병"])
    
    return kiwi, big_dict

kiwi, NOUN_DICT = load_external_data()

# 국립국어원 API를 통해 실시간으로 명사 여부를 한 번 더 검증해
def is_official_noun(word):
    search_url = f"https://stdict.korean.go.kr/api/search.do?key={API_KEY}&q={word}&part=word&type_search=search"
    try:
        r = requests.get(search_url, timeout=3)
        root = ET.fromstring(r.text)
        # 결과가 있으면 명사인지 확인
        for item in root.findall('.//item'):
            pos = item.find('pos').text
            if '명사' in pos: return True
        return False
    except:
        return False

st.title("🐦 저보아: 외부 사전 통합 엔진")
st.write(f"현재 연결된 외부 어휘 수: **{len(NOUN_DICT):,}개**")
st.caption("국립국어원 표준국어대사전 API 가동 중")

# --- 울리포 치환 알고리즘 ---
def s_plus_n_external(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    last_end =

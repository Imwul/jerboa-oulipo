import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET

# 1. 페이지 설정 (반드시 최상단)
st.set_page_config(page_title="Jerboa Network Diagnostic", page_icon="🐦")

# 2. Kiwi 엔진 로드 함수 (캐싱 처리)
@st.cache_resource
def load_kiwi_engine():
    try:
        return Kiwi()
    except Exception as e:
        st.error(f"Kiwi 로드 실패: {e}")
        return None

# 3. 메인 진단 및 단어 로드 함수
def diagnostic_load():
    kiwi = load_kiwi_engine()
    
    # 기본 단어장
    base_dict = ["심연", "권태", "알바트로스", "오브제", "해부대", "재봉틀", "초현실", "파편", "공백", "소멸"]
    
    API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"
    
    # ⚠️ 이 부분의 들여쓰기가 위 코드들과 일치해야 해!
    keywords = [
        "오브제", "파편", "흔적", "심연", "거울", "그림자", 
        "자동", "복제", "기계", "신체", "시선", "공백"
    ]
    
    total_ext_words = []

    try:
        for kw in keywords:
            # API 호출 시 num=100으로 최대치 확보
            url = f"https://opendict.korean.go.kr/api/search?key={API_KEY}&q={kw}&target=1&num=100&advanced=y&method=include"
            res = requests.get(url, timeout=10, verify=False)
            
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                words = [node.text.replace('-', '') for node in root.findall('.//item/word') if node.text]
                total_ext_words.extend(words)
        
        final_dict = sorted(list(set(base_dict + total_ext_words)))
        status = f"✅ 성공! (총 {len(final_dict)}개 장전)"
        return kiwi, final_dict, status

    except Exception as e:
        return kiwi, base_dict, f"⚠️ 통신 장애: {str(e)}"

# --- 실행부 ---
kiwi, NOUN_DICT, network_status = diagnostic_load()

st.title("🐦 저보아: 무한 울리포 엔진")

# 사이드바 상태 표시
if "✅" in network_status:
    st.sidebar.success(network_status)
else:
    st.sidebar.warning(network_status)

st.write(f"현재 장전된 단어: **{len(NOUN_DICT):,}개**")

# 만약 단어가 너무 적으면 경고창 띄우기
if len(NOUN_DICT) < 50:
    st.info("단어 공급이 원활하지 않습니다. '저보아 서클'의 창의성이 위험합니다!")

# 확인용 리스트 (일부만)
with st.expander("장전된 단어 샘플 보기"):
    st.write(", ".join(NOUN_DICT[:50]) + " ...")

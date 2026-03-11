import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Jerboa Network Diagnostic", page_icon="🐦")

# 1. 국립국어원 API 키
API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"

@st.cache_resource
def diagnostic_load():
    kiwi = Kiwi()
    # 비상용 정예 단어 (이 리스트가 12개라면 더 늘려야 해!)
    base_dict = ["심연", "권태", "알바트로스", "오브제", "해부대", "재봉틀", "초현실", "파편", "공백", "소멸"]
    
    # "나 브라우저야!"라고 철저히 위장하는 헤더
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 깃허브 명사 리스트 주소 (가장 안정적인 주소로 변경)
    url = "https://raw.githubusercontent.com/naver/korean-wordlist/master/nouns.txt"
    
    try:
        # verify=False는 SSL 인증서 오류를 무시하는 옵션이야 (위험하지만 진단용으론 최고지)
        res = requests.get(url, headers=headers, timeout=10, verify=True)
        if res.status_code == 200:
            ext_words = [w.strip() for w in res.text.split('\n') if len(w.strip()) > 1]
            return kiwi, sorted(list(set(base_dict + ext_words))), "✅ 외부 네트워크 연결 성공!"
        else:
            return kiwi, base_dict, f"❌ 응답 오류 (코드: {res.status_code})"
    except Exception as e:
        return kiwi, base_dict, f"⚠️ 통신 실패: {str(e)}"

kiwi, NOUN_DICT, network_status = diagnostic_load()

# --- 사이드바에 네트워크 진단 결과 노출 ---
st.sidebar.title("🔍 네트워크 상태")
if "✅" in network_status:
    st.sidebar.success(network_status)
else:
    st.sidebar.error(network_status)
    st.sidebar.warning("팁: 로컬 사전으로 자동 전환되었습니다.")

st.title("🐦 저보아: 무한 울리포 엔진")
st.write(f"현재 장전된 단어: **{len(NOUN_DICT):,}개**")

# (이후 변환 로직은 이전과 동일)

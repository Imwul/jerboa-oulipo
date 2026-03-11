import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET

# 1. 페이지 설정은 무조건 최상단!
st.set_page_config(page_title="Jerboa Network Diagnostic", page_icon="🐦")

@st.cache_resource
def get_kiwi():
    try:
        return Kiwi()
    except Exception as e:
        st.error(f"Kiwi 엔진 시동 실패: {e}")
        return None

def diagnostic_load():
    kiwi = get_kiwi()
    base_dict = ["심연", "권태", "알바트로스", "오브제", "해부대", "재봉틀", "초현실", "파편", "공백", "소멸"]
    
    # 국립국어원 API 테스트용 주소 (실제 API 가이드에 맞게 수정 필요)
    API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"
    url = f"https://opendict.korean.go.kr/api/search?key={API_KEY}&q=현대&target=1"

    try:
        # verify=False로 인증서 문제 원천 봉쇄 (임시)
        res = requests.get(url, timeout=5, verify=False) 
        
        if res.status_code == 200:
            # XML 구조가 맞는지 확인하며 파싱
            try:
                root = ET.fromstring(res.content)
                items = root.findall('.//item')
                ext_words = [item.find('word').text.replace('-', '') for item in items if item.find('word') is not None]
                return kiwi, sorted(list(set(base_dict + ext_words))), "✅ API 연결 성공!"
            except Exception as parse_err:
                return kiwi, base_dict, f"⚠️ 데이터 해석 실패(비정상 응답): {parse_err}"
        else:
            return kiwi, base_dict, f"❌ 서버 응답 에러 (코드: {res.status_code})"
            
    except Exception as e:
        return kiwi, base_dict, f"🌐 네트워크 연결 불가: {str(e)}"

# 실행 및 화면 표시
kiwi, NOUN_DICT, network_status = diagnostic_load()

st.title("🐦 저보아: 무한 울리포 엔진")

if "✅" not in network_status:
    st.warning(f"진단 결과: {network_status}")
    st.info("기본 단어장으로 전환합니다.")

st.write(f"현재 장전된 단어: **{len(NOUN_DICT)}개**")
st.code(NOUN_DICT[:10]) # 단어들 일부 노출해서 작동 확인

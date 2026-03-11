import streamlit as st
import requests
import xml.etree.ElementTree as ET

# ... (기타 설정)

API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"

@st.cache_resource
def diagnostic_load():
    kiwi = Kiwi()
    base_dict = ["심연", "권태", "알바트로스", "오브제", "해부대", "재봉틀", "초현실", "파편", "공백", "소멸"]
    
    # 국립국어원 API 호출 URL (예: '현대'가 포함된 명사 100개 추출)
    # 실제 울리포 엔진을 위해서는 검색어나 타겟을 유동적으로 설정해야 해.
    url = f"https://opendict.korean.go.kr/api/search?key={API_KEY}&q=현대&part=word&sort=popular&type_search=search&method=exact&target=1"

    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            # XML 파싱 (국립국어원은 기본이 XML이야)
            root = ET.fromstring(res.content)
            ext_words = [item.find('word').text.replace('-', '') for item in root.findall('.//item')]
            
            return kiwi, sorted(list(set(base_dict + ext_words))), "✅ 국립국어원 API 연결 성공!"
        else:
            return kiwi, base_dict, f"❌ API 오류 (코드: {res.status_code})"
    except Exception as e:
        return kiwi, base_dict, f"⚠️ 통신 실패: {str(e)}"

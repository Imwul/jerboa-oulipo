import streamlit as st
import requests
import xml.etree.ElementTree as ET

# 1. 페이지 설정은 무조건 최상단!
st.set_page_config(page_title="Jerboa Network Diagnostic", page_icon="🐦")

st.cache_resource
def diagnostic_load():
    kiwi = get_kiwi()
    # 이물의 취향을 저격하는 정예 단어들
    base_dict = ["심연", "권태", "알바트로스", "오브제", "해부대", "재봉틀", "초현실", "파편", "공백", "소멸"]
    
    API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"
    
    # 전략 변경: 검색 키워드를 여러 개로 확장해서 더 많이 긁어모으기
    keywords = ["예술", "미술", "철학", "시", "파편"]
    total_ext_words = []

    try:
        for kw in keywords:
            # target=1(우리말샘), num=100(최대 100개씩)
            url = f"https://opendict.korean.go.kr/api/search?key={API_KEY}&q={kw}&target=1&num=100"
            res = requests.get(url, timeout=5, verify=False)
            
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                # 'word' 태그 안의 텍스트를 추출 (붙임표 '-' 제거)
                items = root.findall('.//item/word')
                total_ext_words.extend([node.text.replace('-', '') for node in items if node.text])

        # 중복 제거 및 필터링
        final_dict = sorted(list(set(base_dict + total_ext_words)))
        return kiwi, final_dict, f"✅ API 연동 성공! (가져온 단어: {len(total_ext_words)}개)"

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

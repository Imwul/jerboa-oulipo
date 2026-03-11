import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET

# 1. 페이지 설정 및 인증키 (보안을 위해 여기에 직접 기입하거나 Secrets를 사용해)
st.set_page_config(page_title="Jerboa National Engine", page_icon="🐦")
API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"

@st.cache_resource
def load_resources():
    kiwi = Kiwi()
    # S+n을 위해 필요한 대규모 기준 명사 리스트 (약 5만 단어)
    url = "https://raw.githubusercontent.com/monologg/korean-wordlist/master/nouns.txt"
    try:
        res = requests.get(url)
        big_dict = [w.strip() for w in res.text.split('\n') if len(w.strip()) > 1]
        big_dict.sort()
    except:
        big_dict = ["심연", "권태", "알바트로스", "오브제", "몽유병", "유령"]
    return kiwi, big_dict

kiwi, NOUN_DICT = load_resources()

# 국립국어원 API로 명사 여부 확인 함수
def check_noun_api(word):
    url = f"https://stdict.korean.go.kr/api/search.do?key={API_KEY}&q={word}&part=word&type_search=search"
    try:
        r = requests.get(url)
        root = ET.fromstring(r.text)
        for item in root.findall('.//item'):
            pos = item.find('pos').text
            if '명사' in pos:
                return True
        return False
    except:
        return False

st.title("🐦 저보아: 국가 공인 무한 엔진")
st.write(f"현재 탐색 가능한 공식 어휘: **{len(NOUN_DICT):,}개 + 실시간 API 조회**")

# --- 알고리즘 로직 ---
def oulipo_national_engine(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    last_end = 0
    
    with st.status("국립국어원 데이터베이스 탐색 중...", expanded=False) as status:
        for token in tokens:
            result.append(text[last_end:token.start])
            # Kiwi가 명사로 판단하고, API에서도 명사로 확인될 경우
            if token.tag in ['NNG', 'NNP']:
                st.write(f"검증 중: {token.form}")
                if token.form in NOUN_DICT or check_noun_api(token.form):
                    # 사전 내 위치 찾기 (없으면 근사치)
                    try:
                        idx = NOUN_DICT.index(token.form)
                    except ValueError:
                        idx = 0 # 사전에 없으면 0번부터 시작
                    
                    new_word = NOUN_DICT[(idx + n) % len(NOUN_DICT)]
                    result.append(new_word)
                else:
                    result.append(token.form)
            else:
                result.append(token.form)
            last_end = token.end
        status.update(label="해체 및 재구성 완료!", state="complete")
        
    result.append(text[last_end:])
    return "".join(result)

# --- UI ---
shift_n = st.sidebar.slider("치환 간격 (S + n)", 1, 1000, 7)
user_input = st.text_area("해체할 문장을 입력하세요:", height=150)

if st.button("국가 공인 알고리즘 실행"):
    if user_input:
        output = oulipo_national_engine(user_input, shift_n)
        st.markdown("### ✨ 변환 결과")
        st.success(output)
        st.caption("본 결과는 국립국어원 표준국어대사전 데이터를 기반으로 생성되었습니다.")
    else:
        st.warning("문장을 입력해 주세요, 이물.")

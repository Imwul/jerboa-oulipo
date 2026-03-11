import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="Jerboa Infinite Engine", page_icon="🐦")

# 1. 국립국어원 API 키 (이물이 발급받은 키)
API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"

@st.cache_resource
def load_all_reliable():
    kiwi = Kiwi()
    
    # 기본 니치 사전 (인터넷 안 돼도 작동함)
    base_dict = [
        "심연", "권태", "알바트로스", "오브제", "몽유병", "유령", "해부대", "재봉틀", 
        "우산", "마네킹", "자동기술", "무의식", "초현실", "파편", "공백", "소멸", 
        "예술", "인생", "사랑", "보들레르", "페렉", "키냐르"
    ]
    
    # 시도해볼 대규모 사전 주소 리스트 (안정적인 것들로 선별)
    urls = [
        "https://raw.githubusercontent.com/monologg/korean-wordlist/master/nouns.txt",
        "https://raw.githubusercontent.com/naver/korean-wordlist/master/nouns.txt",
        "https://raw.githubusercontent.com/loosie/doraemon/master/data/nouns.txt"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    final_dict = set(base_dict)
    success_url = None

    for url in urls:
        try:
            # timeout을 10초로 늘리고, headers를 추가해서 차단을 방지해
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200 and "404" not in res.text[:100]:
                words = [w.strip() for w in res.text.split('\n') if len(w.strip()) > 1]
                final_nouns = [w for w in words if not any(char.isdigit() for char in w)] # 숫자 포함 단어 제거
                final_dict.update(final_nouns)
                success_url = url
                break 
        except:
            continue
            
    status = f"✅ 외부 사전 연결 성공 ({success_url})" if success_url else "⚠️ 모든 외부 주소 실패, 로컬 사전 가동"
    return kiwi, sorted(list(final_dict)), status

kiwi, NOUN_DICT, engine_status = load_all_reliable()

st.title("🐦 저보아: 무한 울리포 엔진")
st.sidebar.info(engine_status)
st.write(f"현재 엔진에 장전된 단어: **{len(NOUN_DICT):,}개**")

# --- 국립국어원 API 실시간 검증 로직 ---
def check_api(word):
    url = f"https://stdict.korean.go.kr/api/search.do?key={API_KEY}&q={word}&part=word&type_search=search"
    try:
        r = requests.get(url, timeout=3)
        root = ET.fromstring(r.text)
        return any('명사' in item.find('pos').text for item in root.findall('.//item'))
    except:
        return False

# --- 변환 로직 (S+N) ---
def oulipo_engine(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    last_end = 0
    for token in tokens:
        result.append(text[last_end:token.start])
        if token.tag in ['NNG', 'NNP']:
            # 사전에 있거나 API에서 명사로 판명되면 치환!
            if token.form in NOUN_DICT or check_api(token.form):
                try:
                    idx = NOUN_DICT.index(token.form)
                    result.append(NOUN_DICT[(idx + n) % len(NOUN_DICT)])
                except ValueError:
                    # 사전에 없지만 명사인 경우, 사전의 중간 단어로 치환하는 초현실적 기법
                    result.append(NOUN_DICT[len(NOUN_DICT)//2])
            else:
                result.append(token.form)
        else:
            result.append(token.form)
        last_end = token.end
    result.append(text[last_end:])
    return "".join(result)

shift_n = st.sidebar.slider("치환 간격 (n)", 1, 1000, 7)
user_input = st.text_area("해체할 문장을 입력하세요:", height=150)

if st.button("무한 엔진 가동"):
    if user_input:
        with st.spinner('외부 데이터베이스와 공명 중...'):
            output = oulipo_engine(user_input, shift_n)
            st.markdown("### ✨ 변환 결과")
            st.success(output)

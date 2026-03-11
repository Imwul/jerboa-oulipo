import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="Jerboa Infinite Engine", page_icon="🐦")

# 1. 국립국어원 API 키
API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"

@st.cache_resource
def load_vast_ocean():
    kiwi = Kiwi()
    
    # [수혈 1] 직접 심어넣은 정예 단어장 (최소한의 자존심)
    # 이물이 좋아하는 니치한 단어들을 대거 추가했어.
    jerboa_niche = [
        "심연", "권태", "알바트로스", "오브제", "몽유병", "유령", "해부대", "재봉틀", "우산", "마네킹", 
        "자동기술", "무의식", "초현실", "파편", "공백", "소멸", "기억", "퍼즐", "레디메이드", "몽타주", 
        "단절", "우연", "구조", "필연", "미궁", "거울", "나르시스", "에로스", "보들레르", "페렉", 
        "키냐르", "누보로망", "사체", "환각", "침묵", "안개", "예술", "인생", "사랑", "해부", 
        "메스", "처방", "청진기", "세포", "증식", "마취", "신경", "혈관", "기생", "상흔", 
        "결핍", "잉여", "순환", "비명", "검은색", "우울", "광기", "심장", "폐허", "그림자"
    ]
    
    # [수혈 2] 외부 거대 사전 시도 (가장 튼튼한 주소들)
    mirrors = [
        "https://raw.githubusercontent.com/monologg/korean-wordlist/master/nouns.txt",
        "https://raw.githubusercontent.com/naver/korean-wordlist/master/nouns.txt"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    final_set = set(jerboa_niche)
    
    # 만약 기존에 성공해서 저장된 nouns.txt가 있다면 그것도 합쳐
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            final_set.update([l.strip() for l in f if len(l.strip()) > 1])

    success_msg = "⚠️ 외부 연결 실패, 저보아 정예 사전 모드"
    
    for url in mirrors:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200 and "404" not in r.text[:100]:
                ext_words = [w.strip() for w in r.text.split('\n') if len(w.strip()) > 1]
                final_set.update(ext_words)
                success_msg = f"✅ 대양 연결 성공! ({len(final_set):,}개 장전됨)"
                break
        except:
            continue
            
    return kiwi, sorted(list(final_set)), success_msg

kiwi, NOUN_DICT, status = load_vast_ocean()

st.title("🐦 저보아: 무한 울리포 엔진")
st.sidebar.info(status)
st.write(f"현재 엔진에 장전된 단어: **{len(NOUN_DICT):,}개**")

# --- 진단 섹션 ---
with st.expander("🔍 엔진 내부 들여다보기"):
    st.write("로드된 단어 예시:", NOUN_DICT[:20])
    if "사랑" in NOUN_DICT:
        st.write("✅ '사랑' 단어 감지됨")

# --- 변환 로직 ---
def oulipo_logic(text, n):
    tokens = kiwi.tokenize(text)
    result = []
    last_end = 0
    for token in tokens:
        result.append(text[last_end:token.start])
        if token.tag in ['NNG', 'NNP']:
            if token.form in NOUN_DICT:
                idx = NOUN_DICT.index(token.form)
                result.append(NOUN_DICT[(idx + n) % len(NOUN_DICT)])
            else:
                result.append(token.form)
        else:
            result.append(token.form)
        last_end = token.end
    result.append(text[last_end:])
    return "".join(result)

shift_n = st.sidebar.slider("치환 간격 (S + n)", 1, 1000, 7)
user_input = st.text_area("해체할 문장을 입력하세요:", height=150, placeholder="사랑은 인생의 오브제다.")

if st.button("무한 변환 실행"):
    if user_input:
        output = oulipo_logic(user_input, shift_n)
        st.markdown("### ✨ 변환 결과")
        st.success(output)
    else:
        st.warning("문장을 넣어줘, 이물.")

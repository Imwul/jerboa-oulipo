import streamlit as st
from kiwipiepy import Kiwi
import requests
import xml.etree.ElementTree as ET
import random
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Jerboa Network Diagnostic", page_icon="🐦")

@st.cache_resource
def load_kiwi_engine():
    return Kiwi()

def fetch_words(kw, API_KEY):
    url = f"https://opendict.korean.go.kr/api/search?key={API_KEY}&q={kw}&target=1&num=100&advanced=y&method=include"
    try:
        res = requests.get(url, timeout=5, verify=False)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            # 기호(^, -)를 미리 제거해서 정화함
            return [node.text.replace('-', '').replace('^', ' ') for node in root.findall('.//item/word') if node.text]
    except: return []
    return []

@st.cache_resource
def diagnostic_load():
    kiwi = load_kiwi_engine()
    base_dict = ["심연", "권태", "알바트로스", "오브제", "해부대", "재봉틀", "초현실", "파편", "공백", "소멸"]
    API_KEY = "E14AAE57D9E8F2214E247F3D5953E31B"
    keywords = ["오브제", "파편", "흔적", "심연", "거울", "그림자", "자동", "복제", "기계", "신체", "시선", "공백"]
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda kw: fetch_words(kw, API_KEY), keywords))
    
    total_ext_words = [word for words in results for word in words]
    final_dict = sorted(list(set(base_dict + total_ext_words)))
    return kiwi, final_dict, f"✅ 엔진 준비 완료 ({len(final_dict)}개 파편)"

kiwi, NOUN_DICT, network_status = diagnostic_load()

st.title("🐦 저보아: 무한 울리포 엔진")

# --- 변환 엔진 (ValueError 수정됨) ---
def transform_engine(text, dictionary):
    if not text.strip(): return "입력된 문장이 없어."
    
    tokens = kiwi.tokenize(text)
    result = []
    
    for t in tokens:
        if t.tag.startswith('N'): # 명사라면
            new_word = random.choice(dictionary)
            # 💡 중요: (단어, 품사) 형태의 튜플로 전달해야 ValueError가 안 나!
            result.append((new_word, 'NNG'))
        else:
            # 기존 토큰의 형태와 품사를 그대로 유지
            result.append((t.form, t.tag))
            
    return kiwi.join(result) # 이제 여기서 에러가 나지 않아!

# UI 부분
user_input = st.text_area("텍스트를 투입해봐.", placeholder="예: 나는 오늘 거울 속에서 파편을 발견했다.")

if st.button("✨ 엔진 가동"):
    if user_input:
        transformed = transform_engine(user_input, NOUN_DICT)
        st.subheader("🖼️ 변환된 결과")
        st.success(transformed)
    else:
        st.warning("문장을 먼저 입력해줘.")

# 시각화 (생략 가능하지만 이물의 취향대로 유지)
st.divider()
visual_samples = random.sample(NOUN_DICT, min(40, len(NOUN_DICT)))
cols = st.columns(5)
for i, word in enumerate(visual_samples):
    with cols[i % 5]:
        color = random.choice(["#3a3f4a", "#2c3e50", "#31433f", "#4a3c5a"])
        st.markdown(f'<div style="background-color:{color}; color:white; padding:5px; border-radius:10px; text-align:center; margin-bottom:5px; font-size:0.8rem;">{word}</div>', unsafe_allow_html=True)

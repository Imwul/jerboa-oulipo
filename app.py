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
def transform_engine(text, dictionary, shift=7):
    if not text.strip(): return "입력된 문장이 없어."
    
    # 1. 사전 정제: 띄어쓰기가 있는 단어는 리듬을 깨므로 필터링 (선택 사항)
    # 1:1 대응을 원한다면 띄어쓰기 없는 단어만 남기는 게 좋아.
    clean_dict = [w for w in dictionary if ' ' not in w]
    
    tokens = kiwi.tokenize(text)
    result = []
    
    for t in tokens:
        if t.tag.startswith('N'): # 명사일 때
            try:
                # 2. S+N 알고리즘: 현재 단어가 사전의 몇 번째인지 찾고 shift만큼 이동
                # 만약 사전에 없는 단어라면 랜덤하게 하되, seed를 써서 고정함
                if t.form in clean_dict:
                    current_idx = clean_dict.index(t.form)
                    new_idx = (current_idx + shift) % len(clean_dict)
                    new_word = clean_dict[new_idx]
                else:
                    # 사전에 없는 단어는 일관성을 위해 해시값을 시드로 사용
                    random.seed(hash(t.form))
                    new_word = random.choice(clean_dict)
                
                result.append((new_word, 'NNG'))
            except:
                result.append((t.form, t.tag))
        else:
            result.append((t.form, t.tag))
            
    return kiwi.join(result)
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

# --- (이전 로직 동일) ---

# 🚀 3. 변환 버튼 및 결과 출력
if st.button("✨ 무한 울리포 엔진 가동"):
    if user_input:
        with st.spinner("단어 파편들을 재조립하는 중..."):
            transformed_text = transform_engine(user_input, NOUN_DICT)
            st.subheader("🖼️ 변환된 결과")
            st.success(transformed_text)
            st.info(f"💡 이 문장에는 {len(NOUN_DICT)}개의 파편 중 일부가 침투했어.")
    else:
        # ⚠️ 여기서 에러가 났었지? 따옴표와 괄호를 확실히 닫아줬어.
        st.warning("먼저 문장을 입력해야 엔진을 돌릴 수 있어!")

# --- 🎨 4. 시각화: 파편의 벽 (Gallery of Fragments) ---
st.divider()
st.subheader("🏺 746개의 파편들: 설치 미술 모드")
st.write("우리 엔진이 삼킨 단어들을 무작위로 전시한 공간이야. 클릭할 때마다 배치가 달라지지.")

# 746개 중 50개만 랜덤하게 뽑아서 시각화 (너무 많으면 페이지가 무거워지니까)
visual_samples = random.sample(NOUN_DICT, min(50, len(NOUN_DICT)))

# CSS를 활용해 약간 '니치'한 감성의 태그 클라우드 만들기
st.markdown("""
    <style>
    .fragment-tag {
        display: inline-block;
        padding: 5px 12px;
        margin: 4px;
        background-color: #f0f2f6;
        border-radius: 20px;
        font-size: 0.9rem;
        color: #31333F;
        border: 1px solid #d1d5db;
        transition: all 0.3s ease;
    }
    .fragment-tag:hover {
        background-color: #ff4b4b;
        color: white;
        transform: scale(1.1) rotate(2deg);
    }
    </style>
    """, unsafe_allow_html=True)

# HTML 태그 생성
fragment_html = "".join([f'<span class="fragment-tag">{word}</span>' for word in visual_samples])
st.markdown(fragment_html, unsafe_allow_html=True)

if st.button("♻️ 파편 재배치"):
    st.rerun()

# ==========================================
# TAB 6: The Babel Glitch (바벨의 균열 - 오독의 시학)
# ==========================================
with tab6:
    st.markdown("""
    <style>
        @font-face { font-family: 'GmarketSans'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff'); }
        @font-face { font-family: 'KyoboHandwriting'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_20-04@1.0/KyoboHandwriting2019.woff') format('woff'); }
        @font-face { font-family: 'DungGeunMo'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.2/DungGeunMo.woff') format('woff'); }
    </style>
    """, unsafe_allow_html=True)
 
    st.markdown("""
    <div class="instruction-box">
        <b>[바벨의 균열 지침: 타이포그래피 콜라주]</b><br>
        - <b>구문 파괴:</b> 완벽한 문장을 넣어 기괴한 번역 오류를 발생시키세요.<br>
        - <b>활자 해체:</b> 폰트 믹스, 진동, 비틀림 슬라이더를 조절하면 <b>결과물이 실시간으로</b> 일그러집니다.
    </div>
    """, unsafe_allow_html=True)
    
    babel_input = st.text_area("해부할 완벽한 문장", placeholder="나는 오늘 아침에 일어나 거울을 보며 깊은 절망을 느꼈다.", height=150, key="babel_input")
    
    SURREAL_NOUNS = ["침묵", "기하학", "고깃덩어리", "균열", "환상지", "잔해", "태엽", "미궁", "백색소음", "이물질", "심연", "파편", "얼룩", "구토"]
    WEIRD_ADVERBS = ["기계적으로", "불쾌하게", "영원히", "느닷없이", "집요하게", "증발하듯", "조각조각", "발작적으로"]
    WEIRD_PARTICLES = ["에게로써", "마저도", "조차", "의 곁에서", "를 향한", "치고는", "너머로"]
    WEIRD_ENDINGS = ["었도다", "리라", "느냐", "거늘", "ㄹ지언정", "나이다", "겠지", "련만"]
    GLITCH_MARKS = ["... ", " [데이터 누락] ", " / ", " (침묵) ", " ░▒▓ ", " // "]
    
    # 4가지 확실히 다른 스타일의 한글 폰트 믹스
    MIX_FONTS = ["'Eulyoo1945-Regular', serif", "'GmarketSans', sans-serif", "'KyoboHandwriting', cursive", "'DungGeunMo', monospace"]

    if 'babel_raw_output' not in st.session_state:
        st.session_state.babel_raw_output = ""

    if st.button("🗼 바벨탑 무너뜨리기", key="babel_btn"):
        if babel_input:
            tokens = kiwi.tokenize(babel_input)
            glitch_result = []
            
            for t in tokens:
                if t.tag.startswith('N') and random.random() > 0.8:
                    glitch_result.append((random.choice(SURREAL_NOUNS), t.tag))
                elif t.tag.startswith('M') and random.random() > 0.5:
                    glitch_result.append((random.choice(WEIRD_ADVERBS), t.tag))
                elif t.tag.startswith('J'): 
                    if random.random() > 0.4: glitch_result.append((random.choice(WEIRD_PARTICLES), t.tag))
                    else: glitch_result.append((t.form, t.tag))
                elif t.tag.startswith('E'):
                    if random.random() > 0.5: glitch_result.append((random.choice(WEIRD_ENDINGS), t.tag))
                    else: glitch_result.append((t.form, t.tag))
                else:
                    glitch_result.append((t.form, t.tag))
                
                if random.random() > 0.9: glitch_result.append(glitch_result[-1])
            
            ruined_text = kiwi.join(glitch_result)
            
            words = ruined_text.split()
            final_text = ""
            for w in words:
                final_text += w + " "
                if random.random() > 0.85: final_text += random.choice(GLITCH_MARKS)
            
            st.session_state.babel_raw_output = final_text

    # 결과물이 있을 때만 렌더링
    if st.session_state.babel_raw_output:
        st.divider()
        st.subheader("👁️ 시각적 변형 제어")
        bc1, bc2 = st.columns(2)
        babel_bumpy = bc1.slider("글자 진동 (높을수록 들쭉날쭉)", 0.0, 1.0, 0.3, key="babel_bumpy")
        babel_tilt = bc2.slider("글자 비틀림 (각도)", 0, 45, 15, key="babel_tilt")

        styled_html = "<div style='padding: 30px; border: 3px solid #000; background: #fff; color: #000 !important; line-height: 2.5; word-wrap: break-word; white-space: pre-wrap;'>"
        
        # !important를 추가해서 전역 CSS를 강제로 뚫어버림
        for char in st.session_state.babel_raw_output:
            if char == ' ': 
                styled_html += '&nbsp;'
            else:
                fs = 1.4 + random.uniform(-babel_bumpy, babel_bumpy)
                rot = random.uniform(-babel_tilt, babel_tilt)
                font_choice = random.choice(MIX_FONTS) if random.random() > 0.65 else MIX_FONTS[0]
                
                styled_html += f'<span style="font-family:{font_choice} !important; font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold;">{char}</span>'
        
        styled_html += "</div>"
        
        st.subheader("👁️ 오독의 캔버스")
        st.markdown(styled_html, unsafe_allow_html=True)

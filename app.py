import streamlit as st
import streamlit.components.v1 as components
from kiwipiepy import Kiwi
import random
import os
import re
import json

# --- 1. 페이지 설정 & 🎨 반응형 디자인 (CSS) ---
st.set_page_config(page_title="Jerboa Circle", layout="wide")

st.markdown("""
<style>
    :root { color-scheme: light !important; }
    [data-testid="stAppViewContainer"], .stApp { background-color: #FFFFFF !important; }

    /* 폰트 4종 로드 */
    @font-face { font-family: 'Eulyoo1945'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff'); }
    @font-face { font-family: 'GmarketSans'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff'); }
    @font-face { font-family: 'KyoboHandwriting'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_20-04@1.0/KyoboHandwriting2019.woff') format('woff'); }
    @font-face { font-family: 'DungGeunMo'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.2/DungGeunMo.woff') format('woff'); }

    /* 기본 텍스트 설정 */
    html, body, [data-testid="stHeader"], .stMarkdown, p, span, div { 
        font-family: 'Eulyoo1945', serif; 
        color: #000000;
    }

    h1 {
        font-family: 'Trattatello', 'Apple Chancery', cursive !important;
        font-size: 3.8rem !important; color: #000000 !important;
        text-align: center; margin-bottom: 1.5rem !important; padding-top: 1rem !important;
    }

    /* 해부대(입력창) 하얀 글씨 강제 고정 */
    .stTextArea textarea, .stTextInput input {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        font-family: 'Eulyoo1945', serif !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        caret-color: #FFFFFF !important;
        font-size: 1.1rem !important;
    }
    
    .instruction-box {
        background-color: #F9F9F9; padding: 18px; border-left: 5px solid #000000;
        margin-bottom: 25px; line-height: 1.7; font-size: 0.95rem; color: #000000 !important;
    }

    /* 하단 사전 파편 애니메이션 CSS */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(1.5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    .fragment-tag {
        display: inline-block; padding: 8px 16px; margin: 10px; border-radius: 2px;
        border: 1px solid #000000; animation: float 5s ease-in-out infinite;
        font-weight: bold; cursor: default; color: #000000 !important;
    }

    /* 버튼 텍스트 색상 픽스 */
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button { 
        background-color: #000000 !important; color: #FFFFFF !important; 
        border-radius: 0px !important; width: 100% !important;
        height: 3.5rem; font-size: 1.2rem !important;
    }
    div.stButton > button p, div[data-testid="stFormSubmitButton"] > button p { color: #FFFFFF !important; }

    /* 📱 모바일 반응형 폰트 조절 로직 */
    @media (max-width: 768px) {
        html { font-size: 13px !important; }
        h1 { font-size: 2.5rem !important; }
        .stTextArea textarea, .stTextInput input { font-size: 1rem !important; }
        .instruction-box { font-size: 0.9rem !important; padding: 12px; }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

@st.cache_data
def load_oulipo_dict():
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return ["거울", "파편", "심연", "공백", "기억", "망각", "미학", "구토", "이방인", "페스트", "시시포스", "환영", "균열", "기하학"]

NOUN_DICT = load_oulipo_dict()
WASHED_COLORS = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]

st.title("Jerboa Circle: Surrealist Workshop")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏺 Oulipo (S+N)", "🔪 Dissector (마그넷)", "🔥 Automaton (자동기술)", "⬛ Erasure (소거)", "📜 Cadavre Exquis", "🗼 Babel Glitch"
])

# ==========================================
# TAB 1: Oulipo Engine (지침서 완벽 복구)
# ==========================================
with tab1:
    st.markdown("""
    <div class="instruction-box">
        <b>[울리포 엔진 가동 지침]</b><br>
        - <b>해부대:</b> 문장을 입력하세요. <b>줄 바꿈</b>과 <b>단어 사이의 여백</b>은 엄격히 보존됩니다.<br>
        - <b>S+N 거리:</b> 명사를 사전에서 찾아 N단계 뒤의 단어로 치환합니다.<br>
        - <b>성역 보호:</b> <b>&lt;단어&gt;</b> 와 같이 꺽쇠로 감싼 부분은 변하지 않는 '성역'이 됩니다.<br>
        - <b>변환 확률:</b> 문장 속 모든 명사를 바꿀지, 일부만 무작위로 치환할지 결정합니다.
    </div>
    """, unsafe_allow_html=True)
    user_input = st.text_area("해부대", placeholder="나는 <심연을> 보았다.", height=150, key="engine_input")
    c1, c2 = st.columns(2); shift_val = c1.slider("S+N 거리", 1, 100, 7); prob_val = c2.slider("변환 확률 (%)", 0, 100, 100)
    c3, c4 = st.columns(2); bumpy_val = c3.slider("진동", 0.0, 0.6, 0.15); tilt_val = c4.slider("비틀림", 0, 30, 10)

    def transform_with_logic(line, shift, prob):
        parts = re.split(r'(<.*?>)', line)
        d_len = len(NOUN_DICT)
        line_result = []
        for part in parts:
            if part.startswith('<') and part.endswith('>'): line_result.append(part[1:-1])
            elif part == '': continue
            else:
                leading_ws = re.match(r'^\s*', part).group() if re.match(r'^\s*', part) else ""
                trailing_ws = re.search(r'\s*$', part).group() if re.search(r'\s*$', part) else ""
                content = part.strip()
                if not content:
                    line_result.append(part)
                    continue
                tokens = kiwi.tokenize(content)
                sub_res = []
                for t in tokens:
                    if t.tag.startswith('N') and (hash(t.form) % 100) < prob:
                        if t.form in NOUN_DICT:
                            idx = (NOUN_DICT.index(t.form) + shift) % d_len
                            new_w = NOUN_DICT[idx]
                        else:
                            random.seed(hash(t.form))
                            new_w = NOUN_DICT[random.randint(0, d_len-1)]
                        sub_res.append((new_w, 'NNG'))
                    else: sub_res.append((t.form, t.tag))
                line_result.append(leading_ws + kiwi.join(sub_res) + trailing_ws)
        return "".join(line_result)

    if st.button("✨ 문장 재단하기", key="engine_btn"):
        if user_input:
            lines = user_input.split('\n')
            html_res = '<div style="line-height: 2.3; word-wrap: break-word; padding: 25px; border: 3px solid #000000; background-color: #FFFFFF; white-space: pre-wrap;">'
            for line in lines:
                if not line.strip():
                    html_res += '\n'
                    continue
                transformed_line = transform_with_logic(line, shift_val, prob_val)
                for char in transformed_line:
                    if char == ' ': html_res += '&nbsp;'
                    else:
                        fs = 1.4 + random.uniform(-bumpy_val, bumpy_val)
                        rot = random.uniform(-tilt_val, tilt_val)
                        html_res += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold; color:#000;">{char}</span>'
                html_res += '\n'
            html_res += '</div>'
            st.markdown(html_res, unsafe_allow_html=True)

# ==========================================
# TAB 2: The Dissector (📱 모바일 터치 완벽 대응)
# ==========================================
with tab2:
    st.markdown("""
    <div class="instruction-box">
        <b>[마그넷 & 나이프 해부 지침]</b><br>
        - <b>🧲 마그넷:</b> 자유롭게 드래그하여 배치합니다. 뿌리가 같은 파편은 고유의 색상을 공유합니다.<br>
        - <b>🔪 칼 툴:</b> 켜진 상태로 마그넷의 특정 글자를 클릭하면, 그 위치에서 텍스트가 잘려나갑니다.<br>
        - <b>🧴 풀 툴:</b> 켜진 상태로 두 마그넷을 클릭하면 붙습니다. 서로 다른 색상도 모자이크처럼 유지됩니다.<br>
        - <b>✨ 영감 (셔플):</b> 파편들을 임의의 행(3~5개)으로 재배치하여 우연의 시를 만듭니다.
    </div>
    """, unsafe_allow_html=True)

    user_input_2 = st.text_area("해부대 (마그넷 생성용)", placeholder="캔버스에 뿌릴 시를 입력하세요.", height=150, key="magnet_input")

    if st.button("🧲 캔버스에 마그넷 생성", key="create_magnet"):
        if user_input_2:
            words = [w for w in re.split(r'\s+', user_input_2) if w]
            words_json = json.dumps(words)
            colors_json = json.dumps(WASHED_COLORS)

            custom_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                body {{ font-family: 'Eulyoo1945', serif; margin: 0; padding: 0; overflow: hidden; user-select: none; }}
                #toolbar {{ background: #000; padding: 10px; display: flex; gap: 10px; align-items: center; justify-content: center; flex-wrap: wrap; }}
                .tool-btn {{ background: #fff; color: #000; border: 2px solid #fff; padding: 8px 16px; font-size: 0.95rem; font-weight: bold; cursor: pointer; transition: all 0.2s; touch-action: manipulation; }}
                .tool-btn.active-knife {{ background: #ff4d4d; color: #fff; border-color: #ff4d4d; }}
                .tool-btn.active-glue {{ background: #4d79ff; color: #fff; border-color: #4d79ff; }}
                #canvas-area {{ width: 100%; height: 600px; background: #fafafa; position: relative; border: 3px solid #000; border-top: none; cursor: default; overflow: hidden; touch-action: none; }}
                .magnet {{ position: absolute; border: 2px solid #000; padding: 0; display: flex; font-size: 1.4rem; font-weight: bold; cursor: grab; white-space: nowrap; box-shadow: 4px 4px 0px #000; background: transparent; touch-action: none; }}
                .magnet:active {{ cursor: grabbing; z-index: 1000 !important; transform: scale(1.05); }}
                .char {{ display: inline-block; padding: 6px 3px; color: #000; transition: color 0.2s; pointer-events: auto; }}
                .char:first-child {{ padding-left: 8px; }} .char:last-child {{ padding-right: 8px; }}
                body.knife-mode #canvas-area, body.knife-mode .magnet {{ cursor: crosshair; }}
                body.knife-mode .char:hover {{ color: #ff4d4d; font-weight: 900; transform: translateY(-2px); }}
                body.glue-mode #canvas-area, body.glue-mode .magnet {{ cursor: cell; }}
                body.glue-mode .char {{ pointer-events: none; }}
                .glue-selected {{ box-shadow: 0 0 15px 5px #4d79ff !important; border-color: #4d79ff; transform: scale(1.05); }}
                
                @media (max-width: 768px) {{
                    #canvas-area {{ height: 450px; }}
                    .magnet {{ font-size: 1.1rem; padding: 0; }}
                    .char {{ padding: 4px 2px; }}
                }}
            </style>
            </head>
            <body>
                <div id="toolbar">
                    <button id="knifeToggle" class="tool-btn">🔪 칼 (Off)</button>
                    <button id="glueToggle" class="tool-btn">🧴 풀 (Off)</button>
                    <button id="shuffleBtn" class="tool-btn" style="background:#ffe3b3; border-color:#ffe3b3;">✨ 셔플</button>
                </div>
                <div id="canvas-area"></div>
                <script>
                    const initialWords = {words_json}; const colorPalette = {colors_json}; const canvas = document.getElementById('canvas-area');
                    let knifeMode = false; let glueMode = false; let glueTarget = null; let zIndex = 10;
                    const knifeBtn = document.getElementById('knifeToggle'); const glueBtn = document.getElementById('glueToggle'); const shuffleBtn = document.getElementById('shuffleBtn');

                    knifeBtn.addEventListener('click', () => {{ knifeMode = !knifeMode; if(knifeMode) {{ glueMode = false; clearGlueTarget(); updateBtns(); }} updateBtns(); }});
                    glueBtn.addEventListener('click', () => {{ glueMode = !glueMode; if(glueMode) {{ knifeMode = false; updateBtns(); }} else clearGlueTarget(); updateBtns(); }});

                    function updateBtns() {{
                        document.body.classList.toggle('knife-mode', knifeMode); document.body.classList.toggle('glue-mode', glueMode);
                        knifeBtn.classList.toggle('active-knife', knifeMode); glueBtn.classList.toggle('active-glue', glueMode);
                        knifeBtn.innerText = knifeMode ? '🔪 칼 (On)' : '🔪 칼 (Off)'; glueBtn.innerText = glueMode ? '🧴 풀 (On)' : '🧴 풀 (Off)';
                    }}
                    function clearGlueTarget() {{ if (glueTarget) glueTarget.classList.remove('glue-selected'); glueTarget = null; }}
                    function getCharData(el) {{ return Array.from(el.children).map(span => ({{ char: span.innerText, bg: span.style.backgroundColor }})); }}

                    function createMagnet(charDataArr, sx, sy) {{
                        if (!charDataArr || charDataArr.length === 0) return;
                        const div = document.createElement('div'); div.className = 'magnet'; div.style.left = sx + 'px'; div.style.top = sy + 'px'; div.style.zIndex = ++zIndex;
                        
                        charDataArr.forEach((item, idx) => {{
                            const span = document.createElement('span'); span.className = 'char'; span.innerText = item.char; span.style.backgroundColor = item.bg; span.dataset.index = idx;
                            // 포인터 이벤트: 모바일 터치와 PC 마우스를 모두 커버
                            span.addEventListener('pointerdown', (e) => {{
                                if (!knifeMode) return; e.stopPropagation(); 
                                const clickedIdx = parseInt(e.target.dataset.index); if (clickedIdx === 0) return;
                                const curData = getCharData(div); const p1 = curData.slice(0, clickedIdx); const p2 = curData.slice(clickedIdx);
                                const pX = parseFloat(div.style.left); const pY = parseFloat(div.style.top);
                                div.remove(); createMagnet(p1, pX, pY); createMagnet(p2, pX + e.target.offsetLeft + 5, pY + 15);
                            }});
                            div.appendChild(span);
                        }});

                        div.addEventListener('pointerdown', (e) => {{
                            if (knifeMode) return;
                            if (glueMode) {{
                                e.stopPropagation();
                                if (!glueTarget) {{ glueTarget = div; div.classList.add('glue-selected'); }} 
                                else if (glueTarget !== div) {{
                                    const d1 = getCharData(glueTarget); const d2 = getCharData(div);
                                    const t1X = parseFloat(glueTarget.style.left); const t2X = parseFloat(div.style.left);
                                    const comb = t1X <= t2X ? d1.concat(d2) : d2.concat(d1);
                                    const nX = Math.min(t1X, t2X); const nY = parseFloat(glueTarget.style.top);
                                    glueTarget.remove(); div.remove(); glueTarget = null; createMagnet(comb, nX, nY);
                                }} else clearGlueTarget();
                                return;
                            }}
                            // 드래그 로직 (터치/마우스)
                            e.preventDefault(); div.style.zIndex = ++zIndex; 
                            let pos3 = e.clientX, pos4 = e.clientY;
                            const move = (ev) => {{
                                ev.preventDefault(); 
                                let p1 = pos3 - ev.clientX; let p2 = pos4 - ev.clientY; 
                                pos3 = ev.clientX; pos4 = ev.clientY;
                                div.style.top = (div.offsetTop - p2) + "px"; div.style.left = (div.offsetLeft - p1) + "px";
                            }};
                            const up = () => {{ document.removeEventListener('pointermove', move); document.removeEventListener('pointerup', up); }};
                            document.addEventListener('pointermove', move, {{passive: false}});
                            document.addEventListener('pointerup', up);
                        }});
                        canvas.appendChild(div);
                    }}

                    shuffleBtn.addEventListener('click', () => {{
                        let mags = Array.from(document.querySelectorAll('.magnet')); let dList = mags.map(m => getCharData(m));
                        for (let i = dList.length - 1; i > 0; i--) {{ const j = Math.floor(Math.random() * (i + 1)); [dList[i], dList[j]] = [dList[j], dList[i]]; }}
                        canvas.innerHTML = ''; clearGlueTarget();
                        let cy = 50, cx = 20, cnt = 0, trg = Math.floor(Math.random() * 3) + 3;
                        dList.forEach((cD) => {{
                            createMagnet(cD, cx, cy); cx += (cD.length * 28) + 20; cnt++;
                            if (cnt >= trg || cx > canvas.offsetWidth - 100) {{ cy += 75; cx = 20 + Math.random() * 40; cnt = 0; trg = Math.floor(Math.random() * 3) + 3; }}
                        }});
                    }});

                    initialWords.forEach((word, i) => {{
                        const x = 20 + (i % 4) * 80 + Math.random() * 20; const y = 20 + Math.floor(i / 4) * 60 + Math.random() * 20;
                        const c = colorPalette[Math.floor(Math.random() * colorPalette.length)];
                        const cArr = Array.from(word).map(ch => ({{ char: ch, bg: c }}));
                        createMagnet(cArr, x, y);
                    }});
                </script>
            </body>
            </html>
            """
            components.html(custom_html, height=700)

# ==========================================
# TAB 3: The Automaton (오버레이 및 불타는 로직 / 모바일 폰트 최적화)
# ==========================================
with tab3:
    st.markdown("""
    <div class="instruction-box">
        <b>[자동 기술 지침: 파편의 증발]</b><br>
        - <b>무의식의 흐름:</b> 텍스트를 입력하세요. 5초간 멈추면 <b>최근 당신이 쏟아낸 3~5개의 어절</b>만 붉게 타오르며 사라집니다.<br>
        - <b>이성의 차단:</b> 백스페이스(수정)를 누르려면 3~5번을 연타해야 겨우 한 글자가 지워집니다.
    </div>
    """, unsafe_allow_html=True)

    automaton_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body { font-family: 'Eulyoo1945', serif; margin: 0; padding: 0; background: #fafafa; user-select: none; }
        #progress-container { width: 100%; height: 8px; background: #ddd; }
        #progress-bar { width: 100%; height: 100%; background: #000; transition: width 0.1s linear, background 1s ease; }
        .danger #progress-bar { background: #ff4d4d; }
        #editor-wrapper { position: relative; width: 100%; height: 500px; border: 3px solid #000; box-shadow: 4px 4px 0px #000; background: transparent; box-sizing: border-box; overflow: hidden; }
        textarea, #overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; padding: 20px; box-sizing: border-box; margin: 0; font-family: 'Eulyoo1945', serif; font-size: 1.5rem; line-height: 1.8; border: none; outline: none; background: transparent; white-space: pre-wrap; word-wrap: break-word; overflow-y: auto; }
        textarea { color: #000; resize: none; z-index: 2; cursor: text; }
        #overlay { color: transparent; z-index: 1; pointer-events: none; }
        .burning-text { display: inline-block; animation: burnTextOnly 1.5s forwards ease-in; }
        @keyframes burnTextOnly {
            0% { color: #ff4d4d; text-shadow: 0 0 0px #ff0000; opacity: 1; transform: translateY(0px); }
            40% { color: #ff3333; text-shadow: 0 -3px 8px #ff9900; opacity: 0.8; transform: translateY(-2px); }
            100% { color: transparent; text-shadow: 0 -15px 25px #ff0000; opacity: 0; transform: translateY(-8px); }
        }
        #bs-warning { position: absolute; top: 20px; right: 20px; color: #ff4d4d; font-weight: bold; opacity: 0; transition: opacity 0.2s; pointer-events: none; z-index: 100; }
        
        @media (max-width: 768px) {
            #editor-wrapper { height: 350px; }
            textarea, #overlay { font-size: 1.1rem; padding: 15px; }
        }
    </style>
    </head>
    <body>
        <div id="progress-container"><div id="progress-bar"></div></div>
        <div id="editor-wrapper">
            <div id="overlay"></div>
            <textarea id="auto-text" placeholder="의식의 검열을 멈추고 쏟아내세요. 5초 뒤 최근 쓴 단어들이 불탑니다..."></textarea>
            <div id="bs-warning">이성이 저항합니다! 연타하세요!</div>
        </div>
        <script>
            const textarea = document.getElementById('auto-text'); const overlay = document.getElementById('overlay');
            const progressBar = document.getElementById('progress-bar'); const bsWarning = document.getElementById('bs-warning');
            const TIME_LIMIT = 5000; let timerInterval; let timeRemaining = TIME_LIMIT; let isBurning = false;
            let bsCount = 0; let bsRequired = Math.floor(Math.random() * 3) + 3;

            function startTimer() {
                clearInterval(timerInterval); timeRemaining = TIME_LIMIT; isBurning = false;
                document.getElementById('progress-container').classList.remove('danger'); progressBar.style.width = '100%';
                timerInterval = setInterval(() => {
                    if(textarea.value.trim() === '') return; 
                    timeRemaining -= 100; progressBar.style.width = ((timeRemaining / TIME_LIMIT) * 100) + '%';
                    if (timeRemaining <= 2000) document.getElementById('progress-container').classList.add('danger');
                    if (timeRemaining <= 0) { clearInterval(timerInterval); triggerPartialBurn(); }
                }, 100);
            }

            function triggerPartialBurn() {
                if(isBurning) return; isBurning = true;
                const val = textarea.value; const numToDelete = Math.floor(Math.random() * 3) + 3; 
                let wordCount = 0; let splitIndex = 0; let inWord = false;
                for(let i = val.length - 1; i >= 0; i--) {
                    if (/\\s/.test(val[i])) { inWord = false; } else { if (!inWord) { wordCount++; inWord = true; } }
                    if (wordCount > numToDelete) { splitIndex = i + 1; break; }
                }
                const safePart = val.substring(0, splitIndex); const burningPart = val.substring(splitIndex);
                const escapeHTML = (str) => str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
                overlay.innerHTML = `<span style="color: #000;">${escapeHTML(safePart)}</span><span class="burning-text">${escapeHTML(burningPart)}</span>`;
                overlay.scrollTop = textarea.scrollTop; 
                textarea.style.color = 'transparent'; textarea.disabled = true; 
                setTimeout(() => {
                    textarea.value = safePart; textarea.style.color = '#000'; textarea.disabled = false; overlay.innerHTML = '';
                    progressBar.style.width = '100%'; document.getElementById('progress-container').classList.remove('danger');
                    isBurning = false; textarea.focus(); if(textarea.value.trim() !== '') startTimer();
                }, 1500);
            }

            textarea.addEventListener('input', () => { if (textarea.composing) { clearInterval(timerInterval); return; } if(!isBurning) startTimer(); });
            textarea.addEventListener('compositionstart', () => { textarea.composing = true; clearInterval(timerInterval); });
            textarea.addEventListener('compositionend', () => { textarea.composing = false; if(!isBurning) startTimer(); });
            textarea.addEventListener('scroll', () => { overlay.scrollTop = textarea.scrollTop; });
            textarea.addEventListener('keydown', (e) => {
                if (isBurning) { e.preventDefault(); return; }
                if (e.key === 'Backspace') {
                    if (textarea.composing) return;
                    bsWarning.style.opacity = '1'; setTimeout(() => bsWarning.style.opacity = '0', 500);
                    bsCount++; if (bsCount < bsRequired) { e.preventDefault(); } else { bsCount = 0; bsRequired = Math.floor(Math.random() * 3) + 3; }
                } else { bsWarning.style.opacity = '0'; if(!isBurning) startTimer(); }
            });
        </script>
    </body>
    </html>
    """
    components.html(automaton_html, height=550)

# ==========================================
# TAB 4: The Erasure (모바일 터치 소거 대응)
# ==========================================
with tab4:
    st.markdown("""
    <div class="instruction-box">
        <b>[블랙아웃 지침: 소거의 미학]</b><br>
        - <b>은폐의 조각:</b> 텍스트 위를 드래그하거나 터치하여 불필요한 단어를 지워버리세요. 남은 조각들이 시가 됩니다.
    </div>
    """, unsafe_allow_html=True)
    
    default_text = "이성은 언제나 우리를 배신한다. 논리는 껍데기에 불과하며, 진정한 구원은 무의식의 심연 속에서 헤엄치는 파편화된 이미지들에 있다. 당신은 오늘 거울을 보며 무엇을 기억했는가? 망각은 구토를 유발하지만 동시에 새로운 미학의 탄생을 예고한다."
    erasure_input = st.text_area("원본 텍스트 (직접 입력 가능)", value=default_text, height=120, key="erasure_input")

    if st.button("⬛ 소거 캔버스 생성", key="create_erasure"):
        words = erasure_input.split()
        words_json = json.dumps(words)
        
        erasure_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{ font-family: 'Eulyoo1945', serif; margin: 0; padding: 15px; background: #fafafa; user-select: none; touch-action: none; }}
            #canvas {{ width: 100%; min-height: 300px; border: 3px solid #000; padding: 20px; line-height: 2.2; font-size: 1.5rem; background: #fff; box-shadow: 4px 4px 0px #000; box-sizing: border-box; }}
            .word {{ display: inline-block; padding: 2px 5px; margin: 0 3px; cursor: pointer; transition: background-color 0.1s, color 0.1s; border-radius: 2px; color: #000; touch-action: none; }}
            .blackout {{ background-color: #000 !important; color: #000 !important; text-shadow: none; user-select: none; }}
            
            @media (max-width: 768px) {{
                #canvas {{ font-size: 1.1rem; padding: 15px; line-height: 2.0; }}
            }}
        </style>
        </head>
        <body>
            <div id="canvas"></div>
            <script>
                const words = {words_json}; const canvas = document.getElementById('canvas'); let isDragging = false;
                
                canvas.addEventListener('pointerdown', () => isDragging = true);
                document.addEventListener('pointerup', () => isDragging = false);
                
                words.forEach(word => {{
                    const span = document.createElement('span'); span.className = 'word'; span.innerText = word;
                    span.addEventListener('pointerdown', (e) => {{ e.preventDefault(); span.classList.toggle('blackout'); }});
                    span.addEventListener('pointerenter', () => {{ if(isDragging) span.classList.add('blackout'); }});
                    canvas.appendChild(span);
                }});

                // 모바일 터치 드래그 호환 패치
                document.addEventListener('touchmove', (e) => {{
                    if(isDragging) {{
                        e.preventDefault();
                        let touch = e.touches[0];
                        let el = document.elementFromPoint(touch.clientX, touch.clientY);
                        if(el && el.classList.contains('word')) el.classList.add('blackout');
                    }}
                }}, {{passive: false}});
            </script>
        </body>
        </html>
        """
        components.html(erasure_html, height=450)

# ==========================================
# TAB 5: Cadavre Exquis (우아한 시체)
# ==========================================
with tab5:
    st.markdown("""
    <div class="instruction-box">
        <b>[우아한 시체 지침: 타자와의 결합]</b><br>
        - <b>은폐와 접속:</b> 문장을 쓰고 엔터를 누르면 문장은 은폐되고 <b>가장 마지막 3개의 어절</b>만 남습니다.<br>
        - 그 파편에만 기대어 다음 문장을 직관적으로 이어가세요. 논리는 필요 없습니다.
    </div>
    """, unsafe_allow_html=True)

    if 'corpse_lines' not in st.session_state:
        st.session_state.corpse_lines = []

    if st.session_state.corpse_lines:
        last_line = st.session_state.corpse_lines[-1]
        words_in_line = last_line.split()
        last_words = " ".join(words_in_line[-3:]) if len(words_in_line) >= 3 else last_line
        st.markdown(f"<h3 style='text-align: center; color: #ff4d4d !important; margin: 30px 0;'>... {last_words}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center; margin: 30px 0;'>첫 문장을 입력해 의식을 시작하세요.</h3>", unsafe_allow_html=True)

    with st.form(key='corpse_form', clear_on_submit=True):
        new_line = st.text_input("다음 문장 이어쓰기:", placeholder="무의식이 이끄는 대로 적으세요...")
        submit_btn = st.form_submit_button("✒️ 종이 접어 넘기기")
        
        if submit_btn and new_line.strip():
            st.session_state.corpse_lines.append(new_line.strip())
            st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("📜 종이 모두 펼치기 (결과 확인)"):
        if st.session_state.corpse_lines:
            st.divider()
            st.subheader("🖼️ Cadavre Exquis (완성된 시체)")
            poem_html = "<div style='padding: 20px; border: 3px solid #000; background: #fff; color: #000; line-height: 2.0; font-size: 1.1rem;'>"
            for line in st.session_state.corpse_lines:
                poem_html += f"{line}<br>"
            poem_html += "</div>"
            st.markdown(poem_html, unsafe_allow_html=True)
        else:
            st.warning("아직 작성된 문장이 없습니다.")
            
    if c2.button("🗑️ 시체 태우기 (초기화)"):
        st.session_state.corpse_lines = []
        st.rerun()

# ==========================================
# TAB 6: The Babel Glitch (폰트 적용 인라인 믹스 완벽 복구)
# ==========================================
with tab6:
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
    
    # 폰트 이름 직접 지정
    MIX_FONTS = ["Eulyoo1945", "GmarketSans", "KyoboHandwriting", "DungGeunMo"]

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

    if st.session_state.babel_raw_output:
        st.divider()
        st.subheader("👁️ 시각적 변형 제어")
        bc1, bc2 = st.columns(2)
        babel_bumpy = bc1.slider("글자 진동 (높을수록 들쭉날쭉)", 0.0, 1.0, 0.3, key="babel_bumpy")
        babel_tilt = bc2.slider("글자 비틀림 (각도)", 0, 45, 15, key="babel_tilt")

        # 모바일 대응을 위해 폰트 베이스 사이즈를 약간 줄임
        styled_html = "<div style='padding: 20px; border: 3px solid #000; background: #fff; color: #000; line-height: 2.2; word-wrap: break-word; white-space: pre-wrap;'>"
        
        for char in st.session_state.babel_raw_output:
            if char == ' ': 
                styled_html += '&nbsp;'
            else:
                fs = 1.3 + random.uniform(-babel_bumpy, babel_bumpy)
                rot = random.uniform(-babel_tilt, babel_tilt)
                font_choice = random.choice(MIX_FONTS) if random.random() > 0.65 else MIX_FONTS[0]
                
                styled_html += f'<span style="font-family: \'{font_choice}\', sans-serif !important; font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold; color: #000;">{char}</span>'
        
        styled_html += "</div>"
        
        st.subheader("👁️ 오독의 캔버스")
        st.markdown(styled_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 🏺 하단: 사전의 파편들 (Floating Animation)
# ---------------------------------------------------------
st.divider()
st.subheader("🏺 사전의 파편들")
samples = random.sample(NOUN_DICT, min(40, len(NOUN_DICT)))
tag_html = '<div style="text-align:center; padding-bottom: 50px;">'
for s in samples:
    color = random.choice(WASHED_COLORS)
    delay = random.uniform(0, 4)
    duration = random.uniform(5, 8)
    tag_html += f'<span class="fragment-tag" style="background-color:{color}; animation-delay:{delay}s; animation-duration:{duration}s;">{s}</span>'
tag_html += '</div>'
st.markdown(tag_html, unsafe_allow_html=True)

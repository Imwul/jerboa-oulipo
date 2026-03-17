import streamlit as st
import streamlit.components.v1 as components
from kiwipiepy import Kiwi
import random
import os
import re
import json

# --- 1. 공통 폰트 로더 (모든 Iframe에 강제 주입용) ---
FONT_CSS = """
<style>
    @font-face { font-family: 'Eulyoo1945-Regular'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff'); font-weight: normal; font-style: normal; }
    @font-face { font-family: 'GmarketSansMedium'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff'); font-weight: normal; font-style: normal; }
    @font-face { font-family: 'KyoboHandwriting2019'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_20-04@1.0/KyoboHandwriting2019.woff') format('woff'); font-weight: normal; font-style: normal; }
    @font-face { font-family: 'DungGeunMo'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.2/DungGeunMo.woff') format('woff'); font-weight: normal; font-style: normal; }
</style>
"""

# --- 2. 페이지 설정 & 🎨 Streamlit 전역 디자인 ---
st.set_page_config(page_title="Jerboa Circle", layout="wide")

st.markdown(f"""
{FONT_CSS}
<style>
    :root {{ color-scheme: light !important; }}
    [data-testid="stAppViewContainer"], .stApp {{ background-color: #FFFFFF !important; }}

    /* 기본 텍스트는 모두 을유명조 */
    html, body, [class*="st-"], p, span, div, h2, h3, h4, h5, h6, textarea, input, button, label {{ 
        font-family: 'Eulyoo1945-Regular', serif !important; 
    }}

    /* ❗ 모든 소제목, 슬라이더 라벨, 텍스트를 검은색으로 강제 고정 (다크모드 간섭 완벽 차단) */
    h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p {{
        color: #000000 !important;
    }}

    /* ❗ 제목 폰트 Trattatello 복구 및 보호 */
    h1, [data-testid="stHeadingWithActionElements"] h1, h1 * {{
        font-family: 'Trattatello', 'Apple Chancery', fantasy, cursive !important;
        font-size: 3.8rem !important; color: #000000 !important;
        text-align: center; margin-bottom: 1.5rem !important; padding-top: 1rem !important;
    }}

    /* ❗ 탭(Tab) 글씨가 하얗게 변하는 현상 픽스 (무조건 검은색) */
    button[data-baseweb="tab"] *, div[data-testid="stTabs"] button * {{
        color: #000000 !important;
        font-weight: bold !important;
    }}

    /* 해부대(입력창) 하얀 글씨 강제 고정 */
    .stTextArea textarea, .stTextInput input {{
        background-color: #111111 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        caret-color: #FFFFFF !important;
        font-size: 1.1rem !important;
    }}
    
    .instruction-box {{
        background-color: #F9F9F9; padding: 18px; border-left: 5px solid #000000;
        margin-bottom: 25px; line-height: 1.7; font-size: 0.95rem; color: #000000 !important;
    }}

    /* 하단 파편 애니메이션 CSS */
    @keyframes float {{
        0% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-12px) rotate(1.5deg); }}
        100% {{ transform: translateY(0px) rotate(0deg); }}
    }}
    .fragment-tag {{
        display: inline-block; padding: 8px 16px; margin: 10px; border-radius: 2px;
        border: 1px solid #000000; animation: float 5s ease-in-out infinite;
        font-weight: bold; cursor: default; color: #000000 !important;
    }}

    /* 버튼 스타일 */
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button {{ 
        background-color: #000000 !important; color: #FFFFFF !important; 
        border-radius: 0px !important; width: 100% !important;
        height: 3.5rem; font-size: 1.2rem !important;
    }}
    div.stButton > button p, div[data-testid="stFormSubmitButton"] > button p {{ color: #FFFFFF !important; }}
</style>
""", unsafe_allow_html=True)

# --- 3. 모델 및 사전 로드 ---
@st.cache_resource
def load_kiwi(): return Kiwi()
kiwi = load_kiwi()

@st.cache_data
def load_oulipo_dict():
    if os.path.exists("nouns.txt"):
        with open("nouns.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return ["거울", "파편", "심연", "공백", "기억", "망각", "미학", "구토", "이방인", "페스트", "시시포스", "환영", "균열", "기하학", "태엽", "미궁", "내장", "잿더미", "권태", "맹목"]

NOUN_DICT = load_oulipo_dict()
WASHED_COLORS = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]

st.title("Jerboa Circle: Surrealist Workshop")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏺 Oulipo", "🔪 Dissector", "🔥 Automaton", "⬛ Erasure", "📜 Cadavre", "🗼 Babel", "🌉 Roussel Procédé"
])

# ==========================================
# TAB 1: Oulipo Engine (S+N 치환 + 격리 렌더링)
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
                if not content: line_result.append(part); continue
                tokens = kiwi.tokenize(content)
                sub_res = []
                for t in tokens:
                    if t.tag.startswith('N') and (hash(t.form) % 100) < prob:
                        if t.form in NOUN_DICT: idx = (NOUN_DICT.index(t.form) + shift) % d_len; new_w = NOUN_DICT[idx]
                        else: random.seed(hash(t.form)); new_w = NOUN_DICT[random.randint(0, d_len-1)]
                        sub_res.append((new_w, 'NNG'))
                    else: sub_res.append((t.form, t.tag))
                line_result.append(leading_ws + kiwi.join(sub_res) + trailing_ws)
        return "".join(line_result)

    if st.button("✨ 문장 재단하기", key="engine_btn"):
        if user_input:
            lines = user_input.split('\n')
            html_res = f"""
            <!DOCTYPE html><html><head>{FONT_CSS}
            <style>body{{margin:0; padding:10px; background:transparent;}} .box{{padding:25px; border:3px solid #000; background:#fff; line-height:2.3; word-wrap:break-word; white-space:pre-wrap; color:#000; font-family:'Eulyoo1945-Regular', serif;}}</style>
            </head><body><div class="box">
            """
            for line in lines:
                if not line.strip(): html_res += '\n'; continue
                transformed_line = transform_with_logic(line, shift_val, prob_val)
                for char in transformed_line:
                    if char == ' ': html_res += '&nbsp;'
                    else:
                        fs = 1.4 + random.uniform(-bumpy_val, bumpy_val); rot = random.uniform(-tilt_val, tilt_val)
                        html_res += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold;">{char}</span>'
                html_res += '\n'
            html_res += '</div></body></html>'
            components.html(html_res, height=400)

# ==========================================
# TAB 2: The Dissector (모바일 터치 대응 마그넷)
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
            {FONT_CSS}
            <style>
                body {{ font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 0; overflow: hidden; user-select: none; }}
                #toolbar {{ background: #000; padding: 10px; display: flex; gap: 10px; align-items: center; justify-content: center; flex-wrap: wrap; }}
                .tool-btn {{ background: #fff; color: #000; border: 2px solid #fff; padding: 8px 16px; font-size: 0.95rem; font-weight: bold; cursor: pointer; transition: all 0.2s; touch-action: manipulation; font-family: 'Eulyoo1945-Regular', serif; }}
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
                @media (max-width: 768px) {{ #canvas-area {{ height: 450px; }} .magnet {{ font-size: 1.1rem; }} .char {{ padding: 4px 2px; }} }}
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
                            e.preventDefault(); div.style.zIndex = ++zIndex; 
                            let pos3 = e.clientX, pos4 = e.clientY;
                            const move = (ev) => {{
                                ev.preventDefault(); 
                                let p1 = pos3 - ev.clientX; let p2 = pos4 - ev.clientY; 
                                pos3 = ev.clientX; pos4 = ev.clientY;
                                div.style.top = (div.offsetTop - p2) + "px"; div.style.left = (div.offsetLeft - p1) + "px";
                            }};
                            const up = () => {{ document.removeEventListener('pointermove', move); document.removeEventListener('pointerup', up); }};
                            document.addEventListener('pointermove', move, {{passive: false}}); document.addEventListener('pointerup', up);
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
# TAB 3: The Automaton (오버레이 및 불타는 로직)
# ==========================================
with tab3:
    st.markdown("""
    <div class="instruction-box">
        <b>[자동 기술 지침: 파편의 증발]</b><br>
        - <b>무의식의 흐름:</b> 텍스트를 입력하세요. 5초간 멈추면 <b>최근 당신이 쏟아낸 3~5개의 어절</b>만 붉게 타오르며 사라집니다.<br>
        - <b>이성의 차단:</b> 백스페이스(수정)를 누르려면 3~5번을 연타해야 겨우 한 글자가 지워집니다.
    </div>
    """, unsafe_allow_html=True)

    automaton_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    {FONT_CSS}
    <style>
        body {{ font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 0; background: #fafafa; user-select: none; }}
        #progress-container {{ width: 100%; height: 8px; background: #ddd; }}
        #progress-bar {{ width: 100%; height: 100%; background: #000; transition: width 0.1s linear, background 1s ease; }}
        .danger #progress-bar {{ background: #ff4d4d; }}
        #editor-wrapper {{ position: relative; width: 100%; height: 500px; border: 3px solid #000; box-shadow: 4px 4px 0px #000; background: transparent; box-sizing: border-box; overflow: hidden; }}
        textarea, #overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; padding: 20px; box-sizing: border-box; margin: 0; font-family: 'Eulyoo1945-Regular', serif; font-size: 1.5rem; line-height: 1.8; border: none; outline: none; background: transparent; white-space: pre-wrap; word-wrap: break-word; overflow-y: auto; }}
        textarea {{ color: #000; resize: none; z-index: 2; cursor: text; }}
        #overlay {{ color: transparent; z-index: 1; pointer-events: none; }}
        .burning-text {{ display: inline-block; animation: burnTextOnly 1.5s forwards ease-in; }}
        @keyframes burnTextOnly {{
            0% {{ color: #ff4d4d; text-shadow: 0 0 0px #ff0000; opacity: 1; transform: translateY(0px); }}
            40% {{ color: #ff3333; text-shadow: 0 -3px 8px #ff9900; opacity: 0.8; transform: translateY(-2px); }}
            100% {{ color: transparent; text-shadow: 0 -15px 25px #ff0000; opacity: 0; transform: translateY(-8px); }}
        }}
        #bs-warning {{ position: absolute; top: 20px; right: 20px; color: #ff4d4d; font-weight: bold; opacity: 0; transition: opacity 0.2s; pointer-events: none; z-index: 100; }}
        @media (max-width: 768px) {{ #editor-wrapper {{ height: 350px; }} textarea, #overlay {{ font-size: 1.1rem; padding: 15px; }} }}
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

            function startTimer() {{
                clearInterval(timerInterval); timeRemaining = TIME_LIMIT; isBurning = false;
                document.getElementById('progress-container').classList.remove('danger'); progressBar.style.width = '100%';
                timerInterval = setInterval(() => {{
                    if(textarea.value.trim() === '') return; 
                    timeRemaining -= 100; progressBar.style.width = ((timeRemaining / TIME_LIMIT) * 100) + '%';
                    if (timeRemaining <= 2000) document.getElementById('progress-container').classList.add('danger');
                    if (timeRemaining <= 0) {{ clearInterval(timerInterval); triggerPartialBurn(); }}
                }}, 100);
            }}

            function triggerPartialBurn() {{
                if(isBurning) return; isBurning = true;
                const val = textarea.value; const numToDelete = Math.floor(Math.random() * 3) + 3; 
                let wordCount = 0; let splitIndex = 0; let inWord = false;
                for(let i = val.length - 1; i >= 0; i--) {{
                    if (/\\s/.test(val[i])) {{ inWord = false; }} else {{ if (!inWord) {{ wordCount++; inWord = true; }} }}
                    if (wordCount > numToDelete) {{ splitIndex = i + 1; break; }}
                }}
                const safePart = val.substring(0, splitIndex); const burningPart = val.substring(splitIndex);
                const escapeHTML = (str) => str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
                overlay.innerHTML = `<span>${{escapeHTML(safePart)}}</span><span class="burning-text">${{escapeHTML(burningPart)}}</span>`;
                overlay.scrollTop = textarea.scrollTop; 
                textarea.style.color = 'transparent'; textarea.disabled = true; 
                setTimeout(() => {{
                    textarea.value = safePart; textarea.style.color = '#000'; textarea.disabled = false; overlay.innerHTML = '';
                    progressBar.style.width = '100%'; document.getElementById('progress-container').classList.remove('danger');
                    isBurning = false; textarea.focus(); if(textarea.value.trim() !== '') startTimer();
                }}, 1500);
            }}

            textarea.addEventListener('input', () => {{ if (textarea.composing) {{ clearInterval(timerInterval); return; }} if(!isBurning) startTimer(); }});
            textarea.addEventListener('compositionstart', () => {{ textarea.composing = true; clearInterval(timerInterval); }});
            textarea.addEventListener('compositionend', () => {{ textarea.composing = false; if(!isBurning) startTimer(); }});
            textarea.addEventListener('scroll', () => {{ overlay.scrollTop = textarea.scrollTop; }});
            textarea.addEventListener('keydown', (e) => {{
                if (isBurning) {{ e.preventDefault(); return; }}
                if (e.key === 'Backspace') {{
                    if (textarea.composing) return;
                    bsWarning.style.opacity = '1'; setTimeout(() => bsWarning.style.opacity = '0', 500);
                    bsCount++; if (bsCount < bsRequired) {{ e.preventDefault(); }} else {{ bsCount = 0; bsRequired = Math.floor(Math.random() * 3) + 3; }}
                }} else {{ bsWarning.style.opacity = '0'; if(!isBurning) startTimer(); }}
            }});
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
        {FONT_CSS}
        <style>
            body {{ font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 15px; background: #fafafa; user-select: none; touch-action: none; }}
            #canvas {{ width: 100%; min-height: 300px; border: 3px solid #000; padding: 20px; line-height: 2.2; font-size: 1.5rem; background: #fff; box-shadow: 4px 4px 0px #000; box-sizing: border-box; }}
            .word {{ display: inline-block; padding: 2px 5px; margin: 0 3px; cursor: pointer; transition: background-color 0.1s, color 0.1s; border-radius: 2px; color: #000; touch-action: none; }}
            .blackout {{ background-color: #000 !important; color: #000 !important; text-shadow: none; user-select: none; }}
            @media (max-width: 768px) {{ #canvas {{ font-size: 1.1rem; padding: 15px; line-height: 2.0; }} }}
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
                document.addEventListener('touchmove', (e) => {{
                    if(isDragging) {{
                        e.preventDefault(); let touch = e.touches[0];
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
            for line in st.session_state.corpse_lines: poem_html += f"{line}<br>"
            poem_html += "</div>"
            st.markdown(poem_html, unsafe_allow_html=True)
        else:
            st.warning("아직 작성된 문장이 없습니다.")
    if c2.button("🗑️ 시체 태우기 (초기화)"):
        st.session_state.corpse_lines = []
        st.rerun()

# ==========================================
# TAB 6: The Babel Glitch (격리 렌더링을 통한 폰트 강제 적용)
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
    
    # 폰트 이름 (CSS @font-face에 정의된 이름과 정확히 일치)
    MIX_FONTS = ["'Eulyoo1945-Regular'", "'GmarketSansMedium'", "'KyoboHandwriting2019'", "'DungGeunMo'"]

    if 'babel_raw_output' not in st.session_state:
        st.session_state.babel_raw_output = ""

    if st.button("🗼 바벨탑 무너뜨리기", key="babel_btn"):
        if babel_input:
            tokens = kiwi.tokenize(babel_input)
            glitch_result = []
            for t in tokens:
                if t.tag.startswith('N') and random.random() > 0.8: glitch_result.append((random.choice(SURREAL_NOUNS), t.tag))
                elif t.tag.startswith('M') and random.random() > 0.5: glitch_result.append((random.choice(WEIRD_ADVERBS), t.tag))
                elif t.tag.startswith('J'): 
                    if random.random() > 0.4: glitch_result.append((random.choice(WEIRD_PARTICLES), t.tag))
                    else: glitch_result.append((t.form, t.tag))
                elif t.tag.startswith('E'):
                    if random.random() > 0.5: glitch_result.append((random.choice(WEIRD_ENDINGS), t.tag))
                    else: glitch_result.append((t.form, t.tag))
                else: glitch_result.append((t.form, t.tag))
                
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

        # Streamlit의 간섭을 100% 차단하기 위해 Iframe(components.html)으로 렌더링
        res_h = f"""
        <!DOCTYPE html>
        <html>
        <head>
        {FONT_CSS}
        <style>
            body {{ margin: 0; padding: 10px; background: transparent; }}
            .box {{ padding: 30px; border: 3px solid #000; background: #fff; color: #000; line-height: 2.5; word-wrap: break-word; white-space: pre-wrap; }}
            @media (max-width: 768px) {{ .box {{ padding: 15px; line-height: 2.0; }} }}
        </style>
        </head>
        <body>
            <div class="box">
        """
        for char in st.session_state.babel_raw_output:
            if char == ' ': 
                res_h += '&nbsp;'
            else:
                fs = 1.3 + random.uniform(-babel_bumpy, babel_bumpy)
                rot = random.uniform(-babel_tilt, babel_tilt)
                font_choice = random.choice(MIX_FONTS) if random.random() > 0.65 else MIX_FONTS[0]
                res_h += f'<span style="font-family: {font_choice}, sans-serif; font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold; color: #000;">{char}</span>'
        
        res_h += "</div></body></html>"
        components.html(res_h, height=500)
        
import streamlit as st
import math
import re
import random

# ==========================================
# [탭 7 전용 함수 구역]
# ==========================================

def get_rhyme_target(sentence):
    clean_sentence = re.sub(r'[^\w\s]', '', sentence)
    words = clean_sentence.strip().split()
    if not words: return ""
    last_word = words[-1]
    
    if len(words) == 1:
        return last_word[-3:] if len(last_word) >= 3 else last_word
    second_last_word = words[-2]
    
    if len(last_word) + len(second_last_word) <= 3:
        return second_last_word + last_word
    if len(last_word) >= 3:
        return last_word[-3:]
    elif len(last_word) == 2:
        return last_word[-2:]
    return last_word 

def decompose_hangul(char):
    if not ('가' <= char <= '힣'): return None
    char_code = ord(char) - 44032
    jong = char_code % 28
    jung = ((char_code - jong) // 28) % 21
    cho = ((char_code - jong) // 28) // 21
    return cho, jung, jong

def get_loose_vowel(jung):
    # 발음이 유사한 모음들을 파격적으로 통합합니다. ('까만색-말할게' 엇박자 라임 허용)
    mapping = {
        2: 0,           # ㅑ -> ㅏ
        6: 4,           # ㅕ -> ㅓ
        12: 8,          # ㅛ -> ㅗ
        17: 13,         # ㅠ -> ㅜ
        5: 1, 3: 1, 7: 1, 11: 1, 10: 1, 15: 1 # ㅔ, ㅒ, ㅖ, ㅚ, ㅙ, ㅞ -> ㅐ 
    }
    return mapping.get(jung, jung)

def is_loose_rhyme(target_char, word_char):
    t_decomp = decompose_hangul(target_char)
    w_decomp = decompose_hangul(word_char)
    if not t_decomp or not w_decomp:
        return target_char == word_char 
    
    # 초성(cho)과 종성(jong/받침)은 완전히 무시! 오직 중성(jung/모음)만 비교합니다.
    _, t_jung, _ = t_decomp
    _, w_jung, _ = w_decomp
    
    return get_loose_vowel(t_jung) == get_loose_vowel(w_jung)

def match_rhyme(target_str, word_str):
    if len(word_str) < len(target_str): return False
    for i in range(1, len(target_str) + 1):
        if not is_loose_rhyme(target_str[-i], word_str[-i]):
            return False
    return True

# 캐싱 해제! 무조건 25개를 꽉 채워서 반환하는 안전한 탐색 로직
def get_all_matched_words(target_rhyme, dictionary_data):
    if not target_rhyme or not dictionary_data: 
        return []
        
    def get_uniques(word_list):
        word_list.sort(key=len)
        uniques = []
        for w in word_list:
            if not any(w.endswith(u) for u in uniques):
                uniques.append(w)
        return uniques

    # 1차: 원래 타겟(2~3글자)으로 모음 검색
    matched_words = [word for word in dictionary_data if match_rhyme(target_rhyme, word)]
    unique_words = get_uniques(matched_words)
    
    # 2차: 파편이 25개 미만일 때, 타겟이 3글자 이상이었다면 마지막 2글자로 타협
    if len(unique_words) < 25 and len(target_rhyme) >= 3:
        shorter_target = target_rhyme[-2:]
        additional_words = [word for word in dictionary_data if match_rhyme(shorter_target, word) and word not in matched_words]
        matched_words.extend(additional_words)
        unique_words = get_uniques(matched_words)
        
    # 3차: 그래도 25개 미만이면, 마지막 1글자의 모음만으로 극단적 타협
    if len(unique_words) < 25 and len(target_rhyme) >= 2:
        last_char_target = target_rhyme[-1:]
        additional_words = [word for word in dictionary_data if match_rhyme(last_char_target, word) and word not in matched_words]
        matched_words.extend(additional_words)
        unique_words = get_uniques(matched_words)
        
    # 4차: 초현실적 우연의 개입 (사전에서 랜덤 추출하여 빈 공간 무조건 채우기)
    if len(unique_words) < 25:
        needed = 25 - len(unique_words)
        remainders = list(set(dictionary_data) - set(unique_words))
        if remainders:
            fillers = random.sample(remainders, min(needed, len(remainders)))
            unique_words.extend(fillers)
            
    return unique_words

# 동적 CSS 주입 함수
def inject_floating_grid_css(words_length):
    WASHED_COLORS = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]
    
    css = """
    <style>
    .block-container { perspective: 1000px; }
    
    @keyframes float3d {
        0% { transform: translateZ(0) rotateX(0deg) rotateY(0deg) scale(1); }
        25% { transform: translateZ(25px) rotateX(-2deg) rotateY(2deg) scale(1.02); }
        50% { transform: translateZ(-15px) rotateX(2deg) rotateY(-2deg) scale(0.98); }
        75% { transform: translateZ(35px) rotateX(-3deg) rotateY(3deg) scale(1.03); }
        100% { transform: translateZ(0) rotateX(0deg) rotateY(0deg) scale(1); }
    }

    /* 단어들을 다닥다닥 빽빽하게 밀집 */
    div[data-testid="stVerticalBlock"]:has(.grid-start) > div.element-container:has(button[kind="secondary"]) {
        display: inline-block !important;
        width: auto !important;
        margin: 6px !important; 
    }

    div[data-testid="stVerticalBlock"]:has(.grid-start) button[kind="secondary"] {
        transform-style: preserve-3d;
        animation: float3d 6s ease-in-out infinite;
        font-family: 'Eulyoo1945-Regular', serif;
        border-radius: 2px !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border 0.2s ease;
        height: 80px !important; 
        min-width: 85px !important; 
        padding: 10px 15px !important;
    }

    /* 흰색 글씨 강제 덮어쓰기 (무조건 검은색) */
    div[data-testid="stVerticalBlock"]:has(.grid-start) button[kind="secondary"] p {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 1.15em !important;
    }

    div[data-testid="stVerticalBlock"]:has(.grid-start) button[kind="secondary"]:hover {
        transform: translateZ(50px) scale(1.15) !important;
        animation: none !important;
        box-shadow: 4px 4px 12px rgba(0,0,0,0.4) !important;
        border: 2px solid #d32f2f !important;
        z-index: 999;
    }

    .torn-sentence {
        text-align: center;
        font-family: 'Eulyoo1945-Regular', serif;
        font-size: 1.8em;
        letter-spacing: 0.05em;
        line-height: 1.2;
    }
    .torn-sentence.top { color: #555; }
    .torn-sentence.bottom { color: #d32f2f; margin-top: 1em; }
    """

    for i in range(words_length):
        bg_color = random.choice(WASHED_COLORS)
        delay = random.uniform(0, 5)
        css += f"""
        div[data-testid="stVerticalBlock"]:has(.grid-start) > div.element-container:nth-of-type({i+2}) button[kind="secondary"] {{
            background-color: {bg_color} !important;
            border: 1px solid {bg_color} !important;
            animation-delay: {delay}s !important;
        }}
        """
    css += "</style>"
    st.markdown(css, unsafe_allow_html=True)


# ==========================================
# TAB 7: The Roussel Bridge 
# ==========================================
with tab7:
    st.markdown("""
    <div class="instruction-box">
        <b>[두 문장의 심연: 레몽 루셀 기법]</b><br>
        - <b>균열의 시작:</b> 문장을 입력하면 마지막 단어의 모음과 받침(라임)을 분해하여 추출합니다.<br>
        - <b>사전의 파편들:</b> 낯선 단어들이 허공에 밀집되어 3D로 부유하며 파생됩니다.<br>
        - <b>심연의 다리:</b> 파편을 선택하면 두 문장이 위아래로 찢어지며 고정됩니다. 당신은 그 사이의 불가능한 간극을 이야기로 이어 붙여야 합니다.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Jerboa Oulipo Engine 🕰️")

    if 't7_step' not in st.session_state: st.session_state.t7_step = 1
    if 't7_pinned_sentences' not in st.session_state: st.session_state.t7_pinned_sentences = []
    if 't7_all_matched_words' not in st.session_state: st.session_state.t7_all_matched_words = []
    if 't7_generated_words' not in st.session_state: st.session_state.t7_generated_words = []
    if 't7_initial_phrase' not in st.session_state: st.session_state.t7_initial_phrase = ""
    if 't7_base_phrase' not in st.session_state: st.session_state.t7_base_phrase = ""
    if 't7_selected_word' not in st.session_state: st.session_state.t7_selected_word = ""

    # ----------------------------------------
    # Step 1: 시간의 파편 던지기
    # ----------------------------------------
    if st.session_state.t7_step == 1:
        st.markdown("##### 시간의 파편 던지기")
        initial_phrase = st.text_input("한 줄의 어구를 입력하세요:", key="t7_input")
        
        if st.button("✨ 언어의 파편 흩뿌리기", type="primary", key="t7_btn1"):
            if initial_phrase:
                st.session_state.t7_initial_phrase = initial_phrase
                words = initial_phrase.strip().split()
                st.session_state.t7_base_phrase = " ".join(words[:-1]) if len(words) > 1 else ""
                
                rhyme_target = get_rhyme_target(initial_phrase)
                # NOUN_DICT 연동 & 에러 유발 함수 완벽 분리
                all_words = get_all_matched_words(rhyme_target, NOUN_DICT)
                
                if all_words:
                    st.session_state.t7_all_matched_words = all_words
                    st.session_state.t7_generated_words = random.sample(all_words, min(25, len(all_words)))
                    st.session_state.t7_step = 2
                    st.rerun()
                else:
                    st.error("사전에 모음이 일치하는 파편이 단 하나도 없습니다. 다른 어구를 던져보세요.")

    # ----------------------------------------
    # Step 2: 사전의 파편들 선택 (초밀집 Floating Layout)
    # ----------------------------------------
    elif st.session_state.t7_step == 2:
        st.markdown("##### 허공을 부유하는 사전의 파편들")
        
        words = st.session_state.t7_generated_words
        inject_floating_grid_css(len(words))
        
        with st.container():
            st.markdown('<div class="grid-start"></div>', unsafe_allow_html=True)
            for i, word in enumerate(words):
                if st.button(word, key=f"t7_word_{i}"):
                    st.session_state.t7_selected_word = word
                    st.session_state.t7_step = 3
                    st.rerun()
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 파편 다시 부르기", type="primary", key="t7_refresh"):
                all_words = st.session_state.t7_all_matched_words
                st.session_state.t7_generated_words = random.sample(all_words, min(25, len(all_words)))
                st.rerun()
        with col2:
            if st.button("처음부터 다시", type="primary", key="t7_reset_step2"):
                st.session_state.t7_step = 1
                st.rerun()

    # ----------------------------------------
    # Step 3: 두 문장 찢어지고 텍스트창 등장
    # ----------------------------------------
    elif st.session_state.t7_step == 3:
        st.markdown("##### 두 문장의 심연 잇기")
        
        st.markdown(f"<div class='torn-sentence top'>{st.session_state.t7_initial_phrase}</div>", unsafe_allow_html=True)
        body_text = st.text_area("사이를 이을 불가능한 간극의 본문을 작성하세요:", height=200, key="t7_body")
        
        new_sentence = f"{st.session_state.t7_base_phrase} {st.session_state.t7_selected_word}".strip()
        st.markdown(f"<div class='torn-sentence bottom'>{new_sentence}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("문장 확정 및 심연에 기록", type="primary", key="t7_confirm"):
                final_sentence = f"{st.session_state.t7_initial_phrase} {body_text} {new_sentence}"
                st.session_state.t7_pinned_sentences.append(final_sentence)
                st.session_state.t7_step = 1
                st.rerun()
        with col2:
            if st.button("⬅️ 뒤로가기 (파편 다시 고르기)", type="primary", key="t7_back"):
                st.session_state.t7_step = 2
                st.rerun()

    # ----------------------------------------
    # 하단: 기록된 텍스트 고정
    # ----------------------------------------
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("📜 **기록된 잠재적 텍스트들**")
    if st.session_state.t7_pinned_sentences:
        for idx, sentence in enumerate(st.session_state.t7_pinned_sentences):
            st.info(f"**{idx+1}.** {sentence}")
    else:
        st.caption("아직 기록된 문장이 없습니다.")
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

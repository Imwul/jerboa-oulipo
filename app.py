import streamlit as st
import streamlit.components.v1 as components
from kiwipiepy import Kiwi
import random
import os
import re
import json

# --- 1. 페이지 설정 & 🎨 디자인 (CSS) ---
st.set_page_config(page_title="Jerboa Circle", layout="wide")

st.markdown("""
<style>
    :root { color-scheme: light !important; }
    [data-testid="stAppViewContainer"], .stApp { background-color: #FFFFFF !important; }

    @font-face {
        font-family: 'Eulyoo1945-Regular';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
    }

    h1 {
        font-family: 'Trattatello', 'Apple Chancery', 'Chalkduster', cursive !important;
        font-size: 3.8rem !important; color: #000000 !important;
        text-align: center; margin-bottom: 1.5rem !important; padding-top: 1rem !important;
    }

    * { font-family: 'Eulyoo1945-Regular', serif !important; color: #000000 !important; }

    textarea, input[type="text"] {
        background-color: #111111 !important; color: #FFFFFF !important;
        border: 2px solid #000000 !important; caret-color: #FFFFFF !important;
        font-size: 1.1rem !important;
    }
    
    .instruction-box {
        background-color: #F9F9F9; padding: 18px; border-left: 5px solid #000000;
        margin-bottom: 25px; line-height: 1.7; font-size: 0.95rem;
    }

    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(1.5deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    .fragment-tag {
        display: inline-block; padding: 8px 16px; margin: 10px; border-radius: 2px;
        border: 1px solid #000000; animation: float 5s ease-in-out infinite;
        font-weight: bold; cursor: default;
    }

    /* 일반 버튼 및 Form 제출 버튼 텍스트 색상 통합 수정 */
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button { 
        background-color: #000000 !important; color: #FFFFFF !important; 
        border-radius: 0px !important; width: 100% !important;
        height: 3.5rem; font-size: 1.2rem !important; transition: all 0.2s;
    }
    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover { background-color: #333333 !important; }
    div.stButton > button p, div[data-testid="stFormSubmitButton"] > button p { color: #FFFFFF !important; }
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
    return ["거울", "파편", "심연", "공백", "기억", "망각", "미학", "구토", "이방인", "페스트", "시시포스", "환영"]

NOUN_DICT = load_oulipo_dict()
WASHED_COLORS = ["#ffc9c9", "#ffe3b3", "#fff3b5", "#d4f0d4", "#c9ebff", "#d9cbf2", "#ffcbf2"]

st.title("Jerboa Circle: Surrealist Workshop")

# 6개의 거대한 실험실 탭 구성
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏺 Oulipo (S+N)", 
    "🔪 Dissector (마그넷)", 
    "🔥 Automaton (자동기술)", 
    "⬛ Erasure (소거)", 
    "📜 Cadavre Exquis (시체)", 
    "🗼 Babel Glitch (오독)"
])

# ==========================================
# TAB 1: 기존 Oulipo Engine (S+N)
# ==========================================
with tab1:
    st.markdown("<div class='instruction-box'><b>[S+N 치환]</b> 명사를 사전의 N번째 뒤 단어로 교체합니다. &lt;단어&gt;로 성역을 보호하세요.</div>", unsafe_allow_html=True)
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
            st.subheader("🖼️ Resulting Fragment")
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
                        html_res += f'<span style="font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold;">{char}</span>'
                html_res += '\n'
            html_res += '</div>'
            st.markdown(html_res, unsafe_allow_html=True)

# ==========================================
# TAB 2: The Dissector (커스텀 캔버스 로직)
# ==========================================
with tab2:
    st.markdown("""
    <div class="instruction-box">
        <b>[마그넷 & 나이프 해부 지침]</b><br>
        - <b>🧲 마그넷:</b> 자유롭게 드래그하여 배치합니다. 뿌리가 같은 파편은 고유의 색상을 공유합니다.<br>
        - <b>🔪 칼 툴:</b> 켜진 상태로 마그넷의 특정 글자를 클릭하면, 그 위치에서 텍스트가 잘려나갑니다.<br>
        - <b>🧴 풀 툴:</b> 켜진 상태로 두 마그넷을 클릭하면 붙습니다. 서로 다른 색상도 모자이크처럼 유지됩니다.<br>
        - <b>✨ 영감 (셔플):</b> 파편들을 임의의 행(3~5개)으로 재배치하여 우연의 시를 만듭니다.<br>
    </div>
    """, unsafe_allow_html=True)

    user_input_2 = st.text_area("해부대 (마그넷 생성용)", placeholder="캔버스에 뿌릴 시를 입력하세요.", height=150, key="magnet_input")

    if st.button("🧲 캔버스에 마그넷 생성", key="create_magnet"):
        if user_input_2:
            words = [w for w in re.split(r'\s+', user_input_2) if w]
            words_json = json.dumps(words)
            colors_json = json.dumps(WASHED_COLORS)

            custom_html_2 = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                @font-face {{
                    font-family: 'Eulyoo1945-Regular';
                    src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff');
                }}
                body {{ font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 0; overflow: hidden; user-select: none; }}
                #toolbar {{ background: #000; padding: 10px; display: flex; gap: 10px; align-items: center; justify-content: center; flex-wrap: wrap; }}
                .tool-btn {{ background: #fff; color: #000; border: 2px solid #fff; padding: 8px 16px; font-size: 0.95rem; font-weight: bold; cursor: pointer; transition: all 0.2s; }}
                .tool-btn.active-knife {{ background: #ff4d4d; color: #fff; border-color: #ff4d4d; }}
                .tool-btn.active-glue {{ background: #4d79ff; color: #fff; border-color: #4d79ff; }}
                #shuffleBtn {{ background: #ffe3b3; color: #000; border-color: #ffe3b3; }}
                #shuffleBtn:active {{ transform: scale(0.95); }}
                #canvas-area {{ width: 100%; height: 650px; background: #fafafa; position: relative; border: 3px solid #000; border-top: none; cursor: default; overflow: hidden; }}
                .magnet {{ position: absolute; border: 2px solid #000; padding: 0; display: flex; font-size: 1.4rem; font-weight: bold; cursor: grab; white-space: nowrap; box-shadow: 4px 4px 0px #000; transition: transform 0.1s, box-shadow 0.2s; background: transparent; }}
                .magnet:active {{ cursor: grabbing; transform: scale(1.05); z-index: 1000 !important; }}
                .char {{ display: inline-block; padding: 6px 3px; transition: color 0.2s; }}
                .char:first-child {{ padding-left: 8px; }}
                .char:last-child {{ padding-right: 8px; }}
                body.knife-mode #canvas-area, body.knife-mode .magnet {{ cursor: crosshair; }}
                body.knife-mode .magnet:active {{ transform: none; cursor: crosshair; }}
                body.knife-mode .char:hover {{ color: #ff4d4d; font-weight: 900; transform: translateY(-2px); }}
                body.glue-mode #canvas-area, body.glue-mode .magnet {{ cursor: cell; }}
                body.glue-mode .magnet:active {{ transform: none; cursor: cell; }}
                body.glue-mode .char {{ pointer-events: none; }}
                .magnet.glue-selected {{ box-shadow: 0 0 15px 5px #4d79ff !important; border-color: #4d79ff; transform: scale(1.05); }}
            </style>
            </head>
            <body>
                <div id="toolbar">
                    <button id="knifeToggle" class="tool-btn">🔪 칼 툴 (Off)</button>
                    <button id="glueToggle" class="tool-btn">🧴 풀 툴 (Off)</button>
                    <button id="shuffleBtn" class="tool-btn">✨ 영감 (셔플)</button>
                </div>
                <div id="canvas-area"></div>
                <script>
                    const initialWords = {words_json};
                    const colorPalette = {colors_json};
                    const canvas = document.getElementById('canvas-area');
                    let knifeMode = false; let glueMode = false; let glueTarget = null; let zIndex = 10;
                    const knifeBtn = document.getElementById('knifeToggle');
                    const glueBtn = document.getElementById('glueToggle');
                    const shuffleBtn = document.getElementById('shuffleBtn');

                    knifeBtn.addEventListener('click', () => {{ knifeMode = !knifeMode; if(knifeMode) {{ glueMode = false; clearGlueTarget(); updateButtons(); }} updateButtons(); }});
                    glueBtn.addEventListener('click', () => {{ glueMode = !glueMode; if(glueMode) {{ knifeMode = false; updateButtons(); }} else {{ clearGlueTarget(); }} updateButtons(); }});

                    function updateButtons() {{
                        document.body.classList.toggle('knife-mode', knifeMode);
                        document.body.classList.toggle('glue-mode', glueMode);
                        knifeBtn.classList.toggle('active-knife', knifeMode);
                        glueBtn.classList.toggle('active-glue', glueMode);
                        knifeBtn.innerText = knifeMode ? '🔪 칼 툴 (On)' : '🔪 칼 툴 (Off)';
                        glueBtn.innerText = glueMode ? '🧴 풀 툴 (On)' : '🧴 풀 툴 (Off)';
                    }}

                    function clearGlueTarget() {{ if (glueTarget) glueTarget.classList.remove('glue-selected'); glueTarget = null; }}
                    function getCharData(magnetEl) {{ return Array.from(magnetEl.children).map(span => ({{ char: span.innerText, bg: span.style.backgroundColor }})); }}

                    function createMagnet(charDataArray, startX, startY) {{
                        if (!charDataArray || charDataArray.length === 0) return;
                        const div = document.createElement('div'); div.className = 'magnet'; div.style.left = startX + 'px'; div.style.top = startY + 'px'; div.style.zIndex = ++zIndex;
                        charDataArray.forEach((item, index) => {{
                            const span = document.createElement('span'); span.className = 'char'; span.innerText = item.char; span.style.backgroundColor = item.bg; span.dataset.index = index;
                            span.addEventListener('mousedown', (e) => {{
                                if (!knifeMode) return; e.stopPropagation(); 
                                const clickedIdx = parseInt(e.target.dataset.index); if (clickedIdx === 0) return;
                                const currentData = getCharData(div);
                                const part1 = currentData.slice(0, clickedIdx); const part2 = currentData.slice(clickedIdx);
                                const pX = parseFloat(div.style.left); const pY = parseFloat(div.style.top);
                                div.remove();
                                createMagnet(part1, pX, pY); createMagnet(part2, pX + e.target.offsetLeft + 5, pY + 15);
                            }});
                            div.appendChild(span);
                        }});

                        div.addEventListener('mousedown', (e) => {{
                            if (knifeMode) return;
                            if (glueMode) {{
                                e.stopPropagation();
                                if (!glueTarget) {{ glueTarget = div; div.classList.add('glue-selected'); }} 
                                else if (glueTarget !== div) {{
                                    const data1 = getCharData(glueTarget); const data2 = getCharData(div);
                                    const t1X = parseFloat(glueTarget.style.left); const t2X = parseFloat(div.style.left);
                                    const combinedData = t1X <= t2X ? data1.concat(data2) : data2.concat(data1);
                                    const newX = Math.min(t1X, t2X); const newY = parseFloat(glueTarget.style.top);
                                    glueTarget.remove(); div.remove(); glueTarget = null;
                                    createMagnet(combinedData, newX, newY);
                                }} else {{ clearGlueTarget(); }}
                                return;
                            }}
                            e.preventDefault(); div.style.zIndex = ++zIndex; let pos3 = e.clientX, pos4 = e.clientY;
                            document.onmouseup = () => {{ document.onmouseup = null; document.onmousemove = null; }};
                            document.onmousemove = (ev) => {{
                                ev.preventDefault(); let pos1 = pos3 - ev.clientX; let pos2 = pos4 - ev.clientY; pos3 = ev.clientX; pos4 = ev.clientY;
                                div.style.top = (div.offsetTop - pos2) + "px"; div.style.left = (div.offsetLeft - pos1) + "px";
                            }};
                        }});
                        canvas.appendChild(div);
                    }}

                    shuffleBtn.addEventListener('click', () => {{
                        let allMagnets = Array.from(document.querySelectorAll('.magnet'));
                        let dataList = allMagnets.map(m => getCharData(m));
                        for (let i = dataList.length - 1; i > 0; i--) {{
                            const j = Math.floor(Math.random() * (i + 1)); [dataList[i], dataList[j]] = [dataList[j], dataList[i]];
                        }}
                        canvas.innerHTML = ''; clearGlueTarget();
                        let currentY = 50; let currentX = 50; let countInRow = 0; let targetInRow = Math.floor(Math.random() * 3) + 3;
                        dataList.forEach((charData) => {{
                            createMagnet(charData, currentX, currentY); currentX += (charData.length * 28) + 30; countInRow++;
                            if (countInRow >= targetInRow || currentX > canvas.offsetWidth - 150) {{
                                currentY += 75; currentX = 40 + Math.random() * 60; countInRow = 0; targetInRow = Math.floor(Math.random() * 3) + 3;
                            }}
                        }});
                    }});

                    initialWords.forEach((word, i) => {{
                        const x = 30 + (i % 6) * 110 + Math.random() * 30; const y = 30 + Math.floor(i / 6) * 70 + Math.random() * 30;
                        const initialColor = colorPalette[Math.floor(Math.random() * colorPalette.length)];
                        const charDataArray = Array.from(word).map(c => ({{ char: c, bg: initialColor }}));
                        createMagnet(charDataArray, x, y);
                    }});
                </script>
            </body>
            </html>
            """
            components.html(custom_html_2, height=750)

# ==========================================
# TAB 3: The Automaton (무의식의 방 & 불타는 캔버스)
# ==========================================
with tab3:
    st.markdown("""
    <div class="instruction-box">
        <b>[자동 기술 지침: 파편의 증발]</b><br>
        - <b>무의식의 흐름:</b> 5초간 키보드가 멈추면 <b>최근 쏟아낸 3~5개의 어절</b>만 붉게 타오릅니다.<br>
        - <b>이성의 차단:</b> 백스페이스(수정)를 누르려면 3~5번을 미친 듯이 연타해야 합니다.<br>
        - <b>활자의 호흡:</b> 타이핑 속도가 빠르면 텍스트가 고양되어 커지고, 망설이면 불안하게 비틀거립니다.
    </div>
    """, unsafe_allow_html=True)

    automaton_html_updated = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @font-face { font-family: 'Eulyoo1945-Regular'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff'); }
        body { font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 0; background: #fafafa; user-select: none; }
        #progress-container { width: 100%; height: 8px; background: #ddd; }
        #progress-bar { width: 100%; height: 100%; background: #000; transition: width 0.1s linear, background 1s ease; }
        .danger #progress-bar { background: #ff4d4d; }
        #editor-wrapper { position: relative; width: 100%; height: 500px; border: 3px solid #000; box-shadow: 4px 4px 0px #000; background: transparent; box-sizing: border-box; overflow: hidden; }
        textarea, #overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; padding: 20px; box-sizing: border-box; margin: 0; font-family: 'Eulyoo1945-Regular', serif; line-height: 1.8; border: none; outline: none; background: transparent; white-space: pre-wrap; word-wrap: break-word; overflow-y: auto; }
        
        /* 타이핑 호흡을 위한 미묘한 트랜지션 추가 */
        textarea { color: #000; resize: none; z-index: 2; cursor: text; font-size: 1.5rem; transition: font-size 0.2s ease, transform 0.3s ease; transform-origin: center center; }
        #overlay { color: transparent; z-index: 1; pointer-events: none; font-size: 1.5rem; }
        
        .burning-text { display: inline-block; animation: burnTextOnly 1.5s forwards ease-in; }
        @keyframes burnTextOnly {
            0% { color: #ff4d4d; text-shadow: 0 0 0px #ff0000; filter: blur(0px); opacity: 1; transform: translateY(0px); }
            40% { color: #ff3333; text-shadow: 0 -3px 8px #ff9900; filter: blur(2px); transform: translateY(-2px); }
            100% { color: transparent; text-shadow: 0 -15px 25px #ff0000; filter: blur(6px); opacity: 0; transform: translateY(-8px); }
        }
        #bs-warning { position: absolute; top: 20px; right: 20px; color: #ff4d4d; font-weight: bold; opacity: 0; transition: opacity 0.2s; pointer-events: none; z-index: 100; }
    </style>
    </head>
    <body>
        <div id="progress-container"><div id="progress-bar"></div></div>
        <div id="editor-wrapper">
            <div id="overlay"></div>
            <textarea id="auto-text" placeholder="의식의 검열을 멈추고 쏟아내세요. 당신의 호흡에 따라 활자가 요동칩니다..."></textarea>
            <div id="bs-warning">이성이 저항합니다! 연타하세요!</div>
        </div>
        <script>
            const textarea = document.getElementById('auto-text');
            const overlay = document.getElementById('overlay');
            const progressBar = document.getElementById('progress-bar');
            const bsWarning = document.getElementById('bs-warning');
            
            const TIME_LIMIT = 5000; let timerInterval; let timeRemaining = TIME_LIMIT; let isBurning = false;
            let bsCount = 0; let bsRequired = Math.floor(Math.random() * 3) + 3;

            // 타이핑 호흡 변수
            let lastKeyTime = Date.now();

            function startTimer() {
                clearInterval(timerInterval); timeRemaining = TIME_LIMIT; isBurning = false;
                document.getElementById('progress-container').classList.remove('danger');
                progressBar.style.width = '100%';

                timerInterval = setInterval(() => {
                    if(textarea.value.trim() === '') return; 
                    timeRemaining -= 100;
                    progressBar.style.width = ((timeRemaining / TIME_LIMIT) * 100) + '%';
                    
                    // 시간이 지날수록(망설일수록) 서서히 삐뚤어짐
                    if(timeRemaining < 4000 && !isBurning) {
                        let sway = (4000 - timeRemaining) * 0.0005; // 최대 2도 내외
                        let tilt = (Math.random() - 0.5) * sway * 2;
                        textarea.style.transform = `rotate(${tilt}deg)`;
                        textarea.style.fontSize = '1.45rem'; // 살짝 위축됨
                    }

                    if (timeRemaining <= 2000) document.getElementById('progress-container').classList.add('danger');
                    if (timeRemaining <= 0) { clearInterval(timerInterval); triggerPartialBurn(); }
                }, 100);
            }

            function triggerPartialBurn() {
                if(isBurning) return;
                isBurning = true;
                
                // 불타는 동안 캔버스 안정화
                textarea.style.transform = `rotate(0deg)`;
                textarea.style.fontSize = '1.5rem';

                const val = textarea.value;
                const numToDelete = Math.floor(Math.random() * 3) + 3;
                let wordCount = 0; let splitIndex = 0; let inWord = false;
                
                for(let i = val.length - 1; i >= 0; i--) {
                    if (/\\s/.test(val[i])) { inWord = false; } else { if (!inWord) { wordCount++; inWord = true; } }
                    if (wordCount > numToDelete) { splitIndex = i + 1; break; }
                }
                
                const safePart = val.substring(0, splitIndex);
                const burningPart = val.substring(splitIndex);
                const escapeHTML = (str) => str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
                
                overlay.innerHTML = `<span style="color: #000;">${escapeHTML(safePart)}</span><span class="burning-text">${escapeHTML(burningPart)}</span>`;
                overlay.scrollTop = textarea.scrollTop;
                
                textarea.style.color = 'transparent'; textarea.disabled = true;
                
                setTimeout(() => {
                    textarea.value = safePart; textarea.style.color = '#000'; textarea.disabled = false; overlay.innerHTML = '';
                    progressBar.style.width = '100%'; document.getElementById('progress-container').classList.remove('danger');
                    isBurning = false; textarea.focus();
                    if(textarea.value.trim() !== '') startTimer();
                }, 1500);
            }

            // 호흡(타이핑 속도) 계산 로직
            textarea.addEventListener('keyup', (e) => {
                const now = Date.now();
                const diff = now - lastKeyTime;
                lastKeyTime = now;

                if (!isBurning && diff < 300 && diff > 10) {
                    // 빠를 때: 폰트가 미묘하게 커짐 (최대 1.65rem)
                    let newSize = 1.5 + (300 - diff) * 0.0005;
                    textarea.style.fontSize = newSize + 'rem';
                    textarea.style.transform = `rotate(0deg)`; // 빠를 땐 비틀림 제거
                }
            });

            textarea.addEventListener('input', () => { if (textarea.composing) { clearInterval(timerInterval); return; } if(!isBurning) startTimer(); });
            textarea.addEventListener('compositionstart', () => { textarea.composing = true; clearInterval(timerInterval); });
            textarea.addEventListener('compositionend', () => { textarea.composing = false; if(!isBurning) startTimer(); });
            textarea.addEventListener('scroll', () => { overlay.scrollTop = textarea.scrollTop; });

            textarea.addEventListener('keydown', (e) => {
                if (isBurning) { e.preventDefault(); return; }
                if (e.key === 'Backspace') {
                    if (textarea.composing) return;
                    bsWarning.style.opacity = '1'; setTimeout(() => bsWarning.style.opacity = '0', 500);
                    bsCount++;
                    if (bsCount < bsRequired) { e.preventDefault(); } else { bsCount = 0; bsRequired = Math.floor(Math.random() * 3) + 3; }
                } else {
                    bsWarning.style.opacity = '0'; if(!isBurning) startTimer();
                }
            });
        </script>
    </body>
    </html>
    """
    components.html(automaton_html_updated, height=600)

# ==========================================
# TAB 4: The Erasure (블랙아웃 캔버스 - 소거의 미학)
# ==========================================
with tab4:
    st.markdown("""
    <div class="instruction-box">
        <b>[블랙아웃 지침: 소거의 미학]</b><br>
        - <b>은폐의 조각:</b> 방대한 텍스트 위를 마우스로 드래그(또는 클릭)하여 불필요한 단어를 지워버리세요.<br>
        - 마치 돌을 깎아 조각상을 만들듯, <b>살아남은 텍스트들만이 모여 한 편의 시</b>가 됩니다.
    </div>
    """, unsafe_allow_html=True)
    
    default_text = "이성은 언제나 우리를 배신한다. 논리는 껍데기에 불과하며, 진정한 구원은 무의식의 심연 속에서 헤엄치는 파편화된 이미지들에 있다. 당신은 오늘 거울을 보며 무엇을 기억했는가? 망각은 구토를 유발하지만 동시에 새로운 미학의 탄생을 예고한다. 보이지 않는 것을 보라."
    erasure_input = st.text_area("원본 텍스트 (직접 입력 가능)", value=default_text, height=120, key="erasure_input")

    if st.button("⬛ 소거 캔버스 생성", key="create_erasure"):
        words = erasure_input.split()
        words_json = json.dumps(words)
        
        erasure_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            @font-face {{ font-family: 'Eulyoo1945-Regular'; src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2102-01@1.0/Eulyoo1945-Regular.woff') format('woff'); }}
            body {{ font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 20px; background: #fafafa; user-select: none; }}
            #canvas {{ width: 100%; min-height: 400px; border: 3px solid #000; padding: 30px; line-height: 2.5; font-size: 1.6rem; background: #fff; box-shadow: 4px 4px 0px #000; box-sizing: border-box; }}
            .word {{ display: inline-block; padding: 2px 6px; margin: 0 4px; cursor: pointer; transition: background-color 0.2s, color 0.2s; border-radius: 2px; }}
            .blackout {{ background-color: #000; color: #000; text-shadow: none; user-select: none; }}
            .word:hover:not(.blackout) {{ background-color: #eee; }}
        </style>
        </head>
        <body>
            <div id="canvas"></div>
            <script>
                const words = {words_json};
                const canvas = document.getElementById('canvas');
                let isDragging = false;

                document.body.onmousedown = () => isDragging = true;
                document.body.onmouseup = () => isDragging = false;

                words.forEach(word => {{
                    const span = document.createElement('span'); span.className = 'word'; span.innerText = word;
                    span.onmousedown = (e) => {{ e.preventDefault(); span.classList.toggle('blackout'); }};
                    span.onmouseenter = (e) => {{ if(isDragging) span.classList.add('blackout'); }};
                    canvas.appendChild(span);
                }});
            </script>
        </body>
        </html>
        """
        components.html(erasure_html, height=500)

# ==========================================
# TAB 5: Cadavre Exquis (우아한 시체 - 타자와의 결합)
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

    # 현재 상태 보여주기 (마지막 3어절 노출 로직 수정)
    if st.session_state.corpse_lines:
        last_line = st.session_state.corpse_lines[-1]
        words_in_line = last_line.split()
        # 3어절보다 길면 뒤의 3개만, 짧으면 전체 라인을 보여줌
        last_words = " ".join(words_in_line[-3:]) if len(words_in_line) >= 3 else last_line
        st.markdown(f"<h3 style='text-align: center; color: #ff4d4d !important; margin: 30px 0;'>... {last_words}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center; margin: 30px 0;'>첫 문장을 입력해 의식을 시작하세요.</h3>", unsafe_allow_html=True)

    # 입력 폼
    with st.form(key='corpse_form', clear_on_submit=True):
        new_line = st.text_input("다음 문장 이어쓰기:", placeholder="무의식이 이끄는 대로 적으세요...")
        submit_btn = st.form_submit_button("✒️ 종이 접어 넘기기")
        
        if submit_btn and new_line.strip():
            st.session_state.corpse_lines.append(new_line.strip())
            st.rerun()

    # 결과 확인 및 초기화
    c1, c2 = st.columns(2)
    if c1.button("📜 종이 모두 펼치기 (결과 확인)"):
        if st.session_state.corpse_lines:
            st.divider()
            st.subheader("🖼️ Cadavre Exquis (완성된 시체)")
            poem_html = "<div style='padding: 30px; border: 3px solid #000; background: #fff; line-height: 2.2; font-size: 1.3rem;'>"
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
# TAB 6: The Babel Glitch (바벨의 균열 - 오독의 시학)
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
    
    # 4가지 기괴한 폰트 믹스
    MIX_FONTS = ["'Eulyoo1945-Regular', serif", "'Courier New', monospace", "Impact, sans-serif", "'Comic Sans MS', cursive, sans-serif"]

    # 세션에 원본(Glitch 완료된) 텍스트를 저장하여 슬라이더 조작 시 텍스트 자체가 바뀌지 않도록 함
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
            
            # 생성된 텍스트를 세션에 고정
            st.session_state.babel_raw_output = final_text

    # 결과물이 있을 때만 슬라이더와 결과창 렌더링 (실시간 업데이트)
    if st.session_state.babel_raw_output:
        st.divider()
        st.subheader("👁️ 시각적 변형 제어")
        bc1, bc2 = st.columns(2)
        babel_bumpy = bc1.slider("글자 진동 (높을수록 들쭉날쭉)", 0.0, 1.0, 0.3, key="babel_bumpy")
        babel_tilt = bc2.slider("글자 비틀림 (각도)", 0, 45, 15, key="babel_tilt")

        styled_html = "<div style='padding: 30px; border: 3px solid #000; background: #fff; color: #000 !important; line-height: 2.5; word-wrap: break-word; white-space: pre-wrap;'>"
        
        # 글자별로 다른 폰트와 크기, 기울기를 적용
        for char in st.session_state.babel_raw_output:
            if char == ' ': 
                styled_html += '&nbsp;'
            else:
                fs = 1.4 + random.uniform(-babel_bumpy, babel_bumpy)
                rot = random.uniform(-babel_tilt, babel_tilt)
                # 30% 확률로 기본 폰트(을유)를 벗어나 이질적인 폰트로 변형
                font_choice = random.choice(MIX_FONTS) if random.random() > 0.7 else MIX_FONTS[0]
                
                styled_html += f'<span style="font-family:{font_choice}; font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold;">{char}</span>'
        
        styled_html += "</div>"
        
        st.subheader("👁️ 오독의 캔버스")
        st.markdown(styled_html, unsafe_allow_html=True)

# --- 하단 🏺 따로 움직이는 파편들 (공통) ---
st.subheader("🏺 사전의 파편들")
samples = random.sample(NOUN_DICT, min(40, len(NOUN_DICT)))

html_tags = '<div style="text-align:center; padding-bottom: 50px;">'
for w in samples:
    color = random.choice(WASHED_COLORS)
    delay = random.uniform(0, 4)
    duration = random.uniform(5, 8)
    html_tags += f'<span class="fragment-tag" style="background-color:{color}; animation-delay: {delay}s; animation-duration: {duration}s;">{w}</span>'
html_tags += '</div>'

st.markdown(html_tags, unsafe_allow_html=True)

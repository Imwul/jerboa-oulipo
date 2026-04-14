import streamlit as st
import streamlit.components.v1 as components
from kiwipiepy import Kiwi
import random
import os
import re
import json
import base64

# ==========================================
# 🖼️ 역사적 인물 사진 설정 구역 (직접 삽입!)
# ==========================================
HISTORY_IMAGES = {
    "tab1": "queneau.jpg",       # 탭 1 (레몽 크노)
    "tab2": "burroughs.jpg",     # 탭 2 (윌리엄 버로스)
    "tab3": "breton.jpg",        # 탭 3 (앙드레 브르통)
    "tab4": "duchamp.jpg",       # 탭 4 (마르셀 뒤샹)
    "tab5": "dali.jpg",          # 탭 5 (살바도르 달리)
    "tab6": "hausmann.jpg",      # 탭 6 (라울 하우스만)
    "tab7": "roussel.jpg",       # 탭 7 (레몽 루셀)
    "tab8": "perec.jpg"          # 탭 8 (조르주 페렉)
}

def get_img_tag(image_source, alt_text):
    """로컬 이미지를 Base64로 강제 변환하여 HTML에 주입하는 특수 엔진"""
    if not image_source: return ""
    if image_source.startswith("http"):
        src = image_source
    elif os.path.exists(image_source):
        with open(image_source, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
            mime = "image/png" if image_source.lower().endswith("png") else "image/jpeg"
            src = f"data:{mime};base64,{encoded}"
    else:
        return f'<div class="history-img" style="display:flex; align-items:center; justify-content:center; background:#eee; color:#888; font-size:0.8rem; text-align:center; font-family:\'Eulyoo1945-Regular\', serif; mix-blend-mode: normal;">사진 없음<br>({image_source})</div>'
    
    return f'<img src="{src}" class="history-img" alt="{alt_text}">'

# --- 1. 공통 폰트 로더 ---
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

    html, body, [class*="st-"], p, span, div, h2, h3, h4, h5, h6, textarea, input, button, label {{ 
        font-family: 'Eulyoo1945-Regular', serif !important; 
    }}

    h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p {{
        color: #000000 !important;
    }}

    h1, [data-testid="stHeadingWithActionElements"] h1, h1 * {{
        font-family: 'Trattatello', 'Apple Chancery', fantasy, cursive !important;
        font-size: 3.8rem !important; color: #000000 !important;
        text-align: center; margin-bottom: 1.5rem !important; padding-top: 1rem !important;
    }}

    button[data-baseweb="tab"] *, div[data-testid="stTabs"] button * {{ color: #000000 !important; font-weight: bold !important; }}

    .stTextArea textarea, .stTextInput input {{
        background-color: #111111 !important; color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important; border: 2px solid #000000 !important;
        caret-color: #FFFFFF !important; font-size: 1.1rem !important;
    }}
    
    .instruction-box {{
        background-color: #F9F9F9; padding: 18px; border-left: 5px solid #000000;
        margin-bottom: 25px; line-height: 1.7; font-size: 0.95rem; color: #000000 !important;
    }}

    /* 💡 각 탭의 역사 박스 */
    .history-box {{
        background-color: #fdfdfd; border-left: 5px solid #d32f2f; padding: 20px;
        margin-bottom: 25px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        display: flex; align-items: flex-start; gap: 20px;
    }}
    
    /* ❗ 배경 투명화 및 그림자 효과가 적용된 사진 CSS ❗ */
    .history-img {{
        width: 110px; height: 140px; object-fit: cover; border-radius: 4px; 
        border: none; /* 테두리 제거 */
        filter: grayscale(100%) contrast(1.2); flex-shrink: 0; 
        box-shadow: 4px 4px 8px rgba(0,0,0,0.3); /* 입체적인 그림자 */
        mix-blend-mode: multiply; /* 하얀 배경을 투명하게 녹이는 핵심 마법 */
        background-color: transparent;
    }}
    
    .history-content {{ flex: 1; }}
    .history-content h4 {{ margin-top: 0; color: #000 !important; font-weight: 900; font-size: 1.15rem; margin-bottom: 10px; }}
    .history-content p {{ margin-bottom: 0; color: #444 !important; font-size: 0.95rem; line-height: 1.65; word-break: keep-all; }}

    /* 하단 파편 애니메이션 */
    @keyframes float {{ 0% {{ transform: translateY(0px) rotate(0deg); }} 50% {{ transform: translateY(-12px) rotate(1.5deg); }} 100% {{ transform: translateY(0px) rotate(0deg); }} }}
    .fragment-tag {{
        display: inline-block; padding: 8px 16px; margin: 10px; border-radius: 2px;
        border: 1px solid #000000; animation: float 5s ease-in-out infinite; font-weight: bold; cursor: default; color: #000000 !important;
    }}

    div.stButton > button[kind="secondary"], div[data-testid="stFormSubmitButton"] > button {{ 
        background-color: #000000 !important; color: #FFFFFF !important; border-radius: 0px !important; width: 100% !important; height: 3.5rem; font-size: 1.2rem !important; transition: transform 0.2s;
    }}
    div.stButton > button[kind="secondary"] p, div[data-testid="stFormSubmitButton"] > button p {{ color: #FFFFFF !important; margin:0; }}
    
    div.stButton > button[kind="primary"] {{
        background-color: #d32f2f !important; color: #FFFFFF !important; border-color: #d32f2f !important; border-radius: 2px !important; width: 100% !important; height: auto !important; padding: 8px; transition: transform 0.2s;
    }}
    div.stButton > button[kind="primary"] p {{ color: #FFFFFF !important; font-weight: bold; margin:0; }}
    div.stButton > button:hover {{ transform: scale(1.02); }}
    .torn-sentence {{ text-align: center; font-family: 'Eulyoo1945-Regular', serif; font-size: 1.8em; letter-spacing: 0.05em; line-height: 1.2; }}
    .torn-sentence.top {{ color: #555; }} .torn-sentence.bottom {{ color: #d32f2f; margin-top: 1em; }}
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

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🏺 Oulipo", "🔪 Dissector", "🔥 Automaton", "⬛ Erasure", "📜 Cadavre", "🗼 Babel", "🌉 Roussel Procédé", "🚫 La Disparition"
])

# ==========================================
# TAB 1: Oulipo Engine
# ==========================================
with tab1:
    img_tag = get_img_tag(HISTORY_IMAGES["tab1"], "Raymond Queneau")
    st.markdown(f"""
    <div class="history-box">
        {img_tag}
        <div class="history-content">
            <h4>📖 기원과 역사: S+7 기법 (S+7 Method)</h4>
            <p>1960년대 수학자와 문학가들이 결성한 아방가르드 집단 <b>'울리포(Oulipo, 잠재적 문학 작업실)'</b>의 창립 멤버 레몽 크노(Raymond Queneau)와 장 레스퀴르가 고안한 기법입니다. 기존 텍스트 내의 모든 명사를 사전에서 그보다 N번째 뒤에 있는 명사로 기계적으로 치환합니다. 작가의 의도와 영감을 완전히 배제한 채 알고리즘적 치환만으로도 서사를 파괴하고 초현실적인 낯선 문맥이 창조될 수 있음을 증명한 수학적-문학적 실험입니다.</p>
        </div>
    </div>
    <div class="instruction-box">
        <b>[울리포 엔진 가동 지침]</b><br>
        - <b>해부대:</b> 문장을 입력하세요. 줄 바꿈과 단어 사이의 여백은 엄격히 보존됩니다.<br>
        - <b>S+N 거리:</b> 명사를 사전에서 찾아 N단계 뒤의 단어로 치환합니다.<br>
        - <b>성역 보호:</b> <b>&lt;단어&gt;</b> 와 같이 꺽쇠로 감싼 부분은 변하지 않는 '성역'이 됩니다.
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
# TAB 2: The Dissector
# ==========================================
with tab2:
    img_tag = get_img_tag(HISTORY_IMAGES["tab2"], "William S. Burroughs")
    st.markdown(f"""
    <div class="history-box">
        {img_tag}
        <div class="history-content">
            <h4>📖 기원과 역사: 컷업 기법 (Cut-up Technique)</h4>
            <p>1920년대 다다이즘의 선구자 트리스탄 차라가 모자에서 오려낸 단어들을 무작위로 뽑아 시를 짓던 퍼포먼스에서 출발했습니다. 이후 1950년대 소설가 <b>윌리엄 S. 버로스(William S. Burroughs)</b>와 화가 브리온 기신이 이를 '컷업 기법'으로 정립했습니다. 기존 텍스트를 물리적으로 해체하고 무작위로 재조립하여, 텍스트가 숨기고 있던 무의식의 언어와 예언적 메시지를 탐구합니다. 훗날 데이비드 보위와 라디오헤드의 작사법으로도 쓰였습니다.</p>
        </div>
    </div>
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
            <!DOCTYPE html><html><head>{FONT_CSS}
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
            </style></head>
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
                    function updateBtns() {{ document.body.classList.toggle('knife-mode', knifeMode); document.body.classList.toggle('glue-mode', glueMode); knifeBtn.classList.toggle('active-knife', knifeMode); glueBtn.classList.toggle('active-glue', glueMode); knifeBtn.innerText = knifeMode ? '🔪 칼 (On)' : '🔪 칼 (Off)'; glueBtn.innerText = glueMode ? '🧴 풀 (On)' : '🧴 풀 (Off)'; }}
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
                                }} else clearGlueTarget(); return;
                            }}
                            e.preventDefault(); div.style.zIndex = ++zIndex; let pos3 = e.clientX, pos4 = e.clientY;
                            const move = (ev) => {{ ev.preventDefault(); let p1 = pos3 - ev.clientX; let p2 = pos4 - ev.clientY; pos3 = ev.clientX; pos4 = ev.clientY; div.style.top = (div.offsetTop - p2) + "px"; div.style.left = (div.offsetLeft - p1) + "px"; }};
                            const up = () => {{ document.removeEventListener('pointermove', move); document.removeEventListener('pointerup', up); }};
                            document.addEventListener('pointermove', move, {{passive: false}}); document.addEventListener('pointerup', up);
                        }}); canvas.appendChild(div);
                    }}
                    shuffleBtn.addEventListener('click', () => {{
                        let mags = Array.from(document.querySelectorAll('.magnet')); let dList = mags.map(m => getCharData(m));
                        for (let i = dList.length - 1; i > 0; i--) {{ const j = Math.floor(Math.random() * (i + 1)); [dList[i], dList[j]] = [dList[j], dList[i]]; }}
                        canvas.innerHTML = ''; clearGlueTarget(); let cy = 50, cx = 20, cnt = 0, trg = Math.floor(Math.random() * 3) + 3;
                        dList.forEach((cD) => {{ createMagnet(cD, cx, cy); cx += (cD.length * 28) + 20; cnt++; if (cnt >= trg || cx > canvas.offsetWidth - 100) {{ cy += 75; cx = 20 + Math.random() * 40; cnt = 0; trg = Math.floor(Math.random() * 3) + 3; }} }});
                    }});
                    initialWords.forEach((word, i) => {{ const x = 20 + (i % 4) * 80 + Math.random() * 20; const y = 20 + Math.floor(i / 4) * 60 + Math.random() * 20; const c = colorPalette[Math.floor(Math.random() * colorPalette.length)]; const cArr = Array.from(word).map(ch => ({{ char: ch, bg: c }})); createMagnet(cArr, x, y); }});
                </script>
            </body></html>
            """
            components.html(custom_html, height=700)

# ==========================================
# TAB 3: The Automaton
# ==========================================
with tab3:
    img_tag = get_img_tag(HISTORY_IMAGES["tab3"], "André Breton")
    st.markdown(f"""
    <div class="history-box">
        {img_tag}
        <div class="history-content">
            <h4>📖 기원과 역사: 자동 기술법 (Écriture Automatique)</h4>
            <p>1924년 <b>앙드레 브르통(André Breton)</b>이 발표한 『초현실주의 선언』에서 주창한 가장 핵심적인 초현실주의 문학 기법입니다. 지그문트 프로이트의 정신분석학(자유 연상 기법)에 영향을 받아, 이성적 통제나 도덕적, 미학적 검열을 완전히 배제한 채 손이 가는 대로 무의식의 흐름을 논스톱으로 받아 적는 방식입니다. 의식의 통제를 뚫고 억압된 심연을 날것의 언어로 끌어올리는 것을 목표로 합니다.</p>
        </div>
    </div>
    <div class="instruction-box">
        <b>[자동 기술 지침: 파편의 증발]</b><br>
        - <b>무의식의 흐름:</b> 텍스트를 입력하세요. 5초간 멈추면 <b>최근 당신이 쏟아낸 어절들</b>이 붉게 타오르며 사라집니다.<br>
        - <b>이성의 차단:</b> 백스페이스(수정)를 누르려면 3~5번을 연타해야 겨우 한 글자가 지워집니다.
    </div>
    """, unsafe_allow_html=True)
    automaton_html = f"""
    <!DOCTYPE html><html><head>{FONT_CSS}
    <style>
        body {{ font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 0; background: #fafafa; user-select: none; }}
        #progress-container {{ width: 100%; height: 8px; background: #ddd; }} #progress-bar {{ width: 100%; height: 100%; background: #000; transition: width 0.1s linear, background 1s ease; }} .danger #progress-bar {{ background: #ff4d4d; }}
        #editor-wrapper {{ position: relative; width: 100%; height: 500px; border: 3px solid #000; box-shadow: 4px 4px 0px #000; background: transparent; box-sizing: border-box; overflow: hidden; }}
        textarea, #overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; padding: 20px; box-sizing: border-box; margin: 0; font-family: 'Eulyoo1945-Regular', serif; font-size: 1.5rem; line-height: 1.8; border: none; outline: none; background: transparent; white-space: pre-wrap; word-wrap: break-word; overflow-y: auto; }}
        textarea {{ color: #000; resize: none; z-index: 2; cursor: text; }} #overlay {{ color: transparent; z-index: 1; pointer-events: none; }}
        .burning-text {{ display: inline-block; animation: burnTextOnly 1.5s forwards ease-in; }}
        @keyframes burnTextOnly {{ 0% {{ color: #ff4d4d; text-shadow: 0 0 0px #ff0000; opacity: 1; transform: translateY(0px); }} 40% {{ color: #ff3333; text-shadow: 0 -3px 8px #ff9900; opacity: 0.8; transform: translateY(-2px); }} 100% {{ color: transparent; text-shadow: 0 -15px 25px #ff0000; opacity: 0; transform: translateY(-8px); }} }}
        #bs-warning {{ position: absolute; top: 20px; right: 20px; color: #ff4d4d; font-weight: bold; opacity: 0; transition: opacity 0.2s; pointer-events: none; z-index: 100; }}
    </style></head>
    <body>
        <div id="progress-container"><div id="progress-bar"></div></div>
        <div id="editor-wrapper"><div id="overlay"></div><textarea id="auto-text" placeholder="의식의 검열을 멈추고 쏟아내세요. 5초 뒤 최근 쓴 단어들이 불탑니다..."></textarea><div id="bs-warning">이성이 저항합니다! 연타하세요!</div></div>
        <script>
            const textarea = document.getElementById('auto-text'); const overlay = document.getElementById('overlay'); const progressBar = document.getElementById('progress-bar'); const bsWarning = document.getElementById('bs-warning');
            const TIME_LIMIT = 5000; let timerInterval; let timeRemaining = TIME_LIMIT; let isBurning = false; let bsCount = 0; let bsRequired = Math.floor(Math.random() * 3) + 3;
            function startTimer() {{ clearInterval(timerInterval); timeRemaining = TIME_LIMIT; isBurning = false; document.getElementById('progress-container').classList.remove('danger'); progressBar.style.width = '100%'; timerInterval = setInterval(() => {{ if(textarea.value.trim() === '') return; timeRemaining -= 100; progressBar.style.width = ((timeRemaining / TIME_LIMIT) * 100) + '%'; if (timeRemaining <= 2000) document.getElementById('progress-container').classList.add('danger'); if (timeRemaining <= 0) {{ clearInterval(timerInterval); triggerPartialBurn(); }} }}, 100); }}
            function triggerPartialBurn() {{ if(isBurning) return; isBurning = true; const val = textarea.value; const numToDelete = Math.floor(Math.random() * 3) + 3; let wordCount = 0; let splitIndex = 0; let inWord = false; for(let i = val.length - 1; i >= 0; i--) {{ if (/\\s/.test(val[i])) {{ inWord = false; }} else {{ if (!inWord) {{ wordCount++; inWord = true; }} }} if (wordCount > numToDelete) {{ splitIndex = i + 1; break; }} }} const safePart = val.substring(0, splitIndex); const burningPart = val.substring(splitIndex); const escapeHTML = (str) => str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); overlay.innerHTML = `<span>${{escapeHTML(safePart)}}</span><span class="burning-text">${{escapeHTML(burningPart)}}</span>`; overlay.scrollTop = textarea.scrollTop; textarea.style.color = 'transparent'; textarea.disabled = true; setTimeout(() => {{ textarea.value = safePart; textarea.style.color = '#000'; textarea.disabled = false; overlay.innerHTML = ''; progressBar.style.width = '100%'; document.getElementById('progress-container').classList.remove('danger'); isBurning = false; textarea.focus(); if(textarea.value.trim() !== '') startTimer(); }}, 1500); }}
            textarea.addEventListener('input', () => {{ if (textarea.composing) {{ clearInterval(timerInterval); return; }} if(!isBurning) startTimer(); }}); textarea.addEventListener('compositionstart', () => {{ textarea.composing = true; clearInterval(timerInterval); }}); textarea.addEventListener('compositionend', () => {{ textarea.composing = false; if(!isBurning) startTimer(); }}); textarea.addEventListener('scroll', () => {{ overlay.scrollTop = textarea.scrollTop; }}); textarea.addEventListener('keydown', (e) => {{ if (isBurning) {{ e.preventDefault(); return; }} if (e.key === 'Backspace') {{ if (textarea.composing) return; bsWarning.style.opacity = '1'; setTimeout(() => bsWarning.style.opacity = '0', 500); bsCount++; if (bsCount < bsRequired) {{ e.preventDefault(); }} else {{ bsCount = 0; bsRequired = Math.floor(Math.random() * 3) + 3; }} }} else {{ bsWarning.style.opacity = '0'; if(!isBurning) startTimer(); }} }});
        </script>
    </body></html>
    """
    components.html(automaton_html, height=550)

# ==========================================
# TAB 4: The Erasure
# ==========================================
with tab4:
    img_tag = get_img_tag(HISTORY_IMAGES["tab4"], "Marcel Duchamp / Avant-Garde Erasure")
    st.markdown(f"""
    <div class="history-box">
        {img_tag}
        <div class="history-content">
            <h4>📖 기원과 역사: 소거시 (Blackout Poetry / Erasure Art)</h4>
            <p>인쇄된 기존의 텍스트(신문, 잡지, 소설 등)에서 불필요한 단어들을 검은 잉크나 펜으로 지워나가며 남은 파편들만으로 새로운 문맥과 시를 조각하는 네거티브(Negative) 창작법입니다. 무에서 유를 창조하는 것이 아니라, 마르셀 뒤샹의 레디메이드처럼 <b>'파괴와 억압적 선택'</b>을 통해 기존 매체를 예술로 탈바꿈시킵니다. 1960년대 톰 필립스(Tom Phillips)의 『A Humument』를 통해 시각 예술과 문학의 경계를 무너뜨리는 현대적 기법으로 자리 잡았습니다.</p>
        </div>
    </div>
    <div class="instruction-box"><b>[블랙아웃 지침: 소거의 미학]</b><br>- <b>은폐의 조각:</b> 텍스트 위를 드래그하거나 터치하여 불필요한 단어를 지워버리세요. 남은 조각들이 시가 됩니다.</div>
    """, unsafe_allow_html=True)
    default_text = "이성은 언제나 우리를 배신한다. 논리는 껍데기에 불과하며, 진정한 구원은 무의식의 심연 속에서 헤엄치는 파편화된 이미지들에 있다. 당신은 오늘 거울을 보며 무엇을 기억했는가? 망각은 구토를 유발하지만 동시에 새로운 미학의 탄생을 예고한다."
    erasure_input = st.text_area("원본 텍스트 (직접 입력 가능)", value=default_text, height=120, key="erasure_input")
    if st.button("⬛ 소거 캔버스 생성", key="create_erasure"):
        words = erasure_input.split(); words_json = json.dumps(words)
        erasure_html = f"""
        <!DOCTYPE html><html><head>{FONT_CSS}<style>body {{ font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 15px; background: #fafafa; user-select: none; touch-action: none; }} #canvas {{ width: 100%; min-height: 300px; border: 3px solid #000; padding: 20px; line-height: 2.2; font-size: 1.5rem; background: #fff; box-shadow: 4px 4px 0px #000; box-sizing: border-box; }} .word {{ display: inline-block; padding: 2px 5px; margin: 0 3px; cursor: pointer; transition: background-color 0.1s, color 0.1s; border-radius: 2px; color: #000; touch-action: none; }} .blackout {{ background-color: #000 !important; color: #000 !important; text-shadow: none; user-select: none; }}</style></head>
        <body><div id="canvas"></div><script>const words = {words_json}; const canvas = document.getElementById('canvas'); let isDragging = false; canvas.addEventListener('pointerdown', () => isDragging = true); document.addEventListener('pointerup', () => isDragging = false); words.forEach(word => {{ const span = document.createElement('span'); span.className = 'word'; span.innerText = word; span.addEventListener('pointerdown', (e) => {{ e.preventDefault(); span.classList.toggle('blackout'); }}); span.addEventListener('pointerenter', () => {{ if(isDragging) span.classList.add('blackout'); }}); canvas.appendChild(span); }}); document.addEventListener('touchmove', (e) => {{ if(isDragging) {{ e.preventDefault(); let touch = e.touches[0]; let el = document.elementFromPoint(touch.clientX, touch.clientY); if(el && el.classList.contains('word')) el.classList.add('blackout'); }} }}, {{passive: false}});</script></body></html>
        """
        components.html(erasure_html, height=450)

# ==========================================
# TAB 5: Cadavre Exquis
# ==========================================
with tab5:
    img_tag = get_img_tag(HISTORY_IMAGES["tab5"], "Salvador Dalí / Surrealist Group")
    st.markdown(f"""
    <div class="history-box">
        {img_tag}
        <div class="history-content">
            <h4>📖 기원과 역사: 우아한 시체 (Cadavre Exquis)</h4>
            <p>1925년 파리 샤토 가(Rue du Château)에 모인 초현실주의자들(이브 탕기, 자크 프레베르, 앙드레 브르통, 마르셀 뒤아멜 등)이 고안한 집단 무의식 창작 놀이입니다. 종이를 접어 앞사람이 쓴 문장(또는 그림)의 끝부분만 본 채로 다음을 이어나가는 방식입니다. <b>"우아한 시체가 햇포도주를 마실 것이다(Le cadavre exquis boira le vin nouveau)"</b>라는 이 놀이의 첫 플레이 결과물에서 이름이 유래했습니다. 타자의 맥락을 철저히 배제한 채 단절된 파편에만 접속함으로써, 기괴하고 매혹적인 집단적 혼종을 낳습니다.</p>
        </div>
    </div>
    <div class="instruction-box"><b>[우아한 시체 지침: 타자와의 결합]</b><br>- <b>은폐와 접속:</b> 문장을 쓰고 엔터를 누르면 문장은 은폐되고 <b>가장 마지막 3개의 어절</b>만 남습니다.<br>- 그 파편에만 기대어 다음 문장을 직관적으로 이어가세요. 논리는 필요 없습니다.</div>
    """, unsafe_allow_html=True)
    if 'corpse_lines' not in st.session_state: st.session_state.corpse_lines = []
    if st.session_state.corpse_lines:
        last_line = st.session_state.corpse_lines[-1]; words_in_line = last_line.split(); last_words = " ".join(words_in_line[-3:]) if len(words_in_line) >= 3 else last_line
        st.markdown(f"<h3 style='text-align: center; color: #ff4d4d !important; margin: 30px 0;'>... {last_words}</h3>", unsafe_allow_html=True)
    else: st.markdown("<h3 style='text-align: center; margin: 30px 0;'>첫 문장을 입력해 의식을 시작하세요.</h3>", unsafe_allow_html=True)
    with st.form(key='corpse_form', clear_on_submit=True):
        new_line = st.text_input("다음 문장 이어쓰기:", placeholder="무의식이 이끄는 대로 적으세요...")
        submit_btn = st.form_submit_button("✒️ 종이 접어 넘기기")
        if submit_btn and new_line.strip(): st.session_state.corpse_lines.append(new_line.strip()); st.rerun()
    c1, c2 = st.columns(2)
    if c1.button("📜 종이 모두 펼치기 (결과 확인)"):
        if st.session_state.corpse_lines:
            st.divider(); st.subheader("🖼️ Cadavre Exquis (완성된 시체)")
            poem_html = "<div style='padding: 20px; border: 3px solid #000; background: #fff; color: #000; line-height: 2.0; font-size: 1.1rem;'>"
            for line in st.session_state.corpse_lines: poem_html += f"{line}<br>"
            poem_html += "</div>"; st.markdown(poem_html, unsafe_allow_html=True)
        else: st.warning("아직 작성된 문장이 없습니다.")
    if c2.button("🗑️ 시체 태우기 (초기화)"): st.session_state.corpse_lines = []; st.rerun()

# ==========================================
# TAB 6: The Babel Glitch
# ==========================================
with tab6:
    img_tag = get_img_tag(HISTORY_IMAGES["tab6"], "Raoul Hausmann")
    st.markdown(f"""
    <div class="history-box">
        {img_tag}
        <div class="history-content">
            <h4>📖 기원과 역사: 다다이즘과 글리치 (Dada & Glitch Art)</h4>
            <p>제1차 세계대전의 참상에 반발하며 기존의 이성과 논리를 철저히 거부했던 다다이스트(Dadaist)들은 활자를 무작위로 섞고 찢어 붙이는 타이포그래피 콜라주(Typography Collage)를 선보였습니다. <b>라울 하우스만(Raoul Hausmann)</b>의 실험에서 엿볼 수 있듯, 완벽한 문법을 지닌 문장을 기계적 오류나 폰트 충돌로 고의 손상시킴으로써 텍스트를 의미 전달의 도구가 아닌 '이미지적 물성' 그 자체로 전락시킵니다. 현대의 데이터 오류를 예술로 승화시키는 '글리치 아트'의 정신적 기원이기도 합니다.</p>
        </div>
    </div>
    <div class="instruction-box"><b>[바벨의 균열 지침: 타이포그래피 콜라주]</b><br>- <b>구문 파괴:</b> 완벽한 문장을 넣어 기괴한 번역 오류를 발생시키세요.<br>- <b>활자 해체:</b> 슬라이더를 조절하여 활자를 실시간으로 일그러뜨립니다.</div>
    """, unsafe_allow_html=True)
    babel_input = st.text_area("해부할 완벽한 문장", placeholder="나는 오늘 아침에 일어나 거울을 보며 깊은 절망을 느꼈다.", height=150, key="babel_input")
    SURREAL_NOUNS = ["침묵", "기하학", "고깃덩어리", "균열", "환상지", "잔해", "태엽", "미궁", "백색소음", "이물질", "심연", "파편", "얼룩", "구토"]
    WEIRD_ADVERBS = ["기계적으로", "불쾌하게", "영원히", "느닷없이", "집요하게", "증발하듯", "조각조각", "발작적으로"]
    WEIRD_PARTICLES = ["에게로써", "마저도", "조차", "의 곁에서", "를 향한", "치고는", "너머로"]
    WEIRD_ENDINGS = ["었도다", "리라", "느냐", "거늘", "ㄹ지언정", "나이다", "겠지", "련만"]
    GLITCH_MARKS = ["... ", " [데이터 누락] ", " / ", " (침묵) ", " ░▒▓ ", " // "]
    MIX_FONTS = ["'Eulyoo1945-Regular'", "'GmarketSansMedium'", "'KyoboHandwriting2019'", "'DungGeunMo'"]
    if 'babel_raw_output' not in st.session_state: st.session_state.babel_raw_output = ""
    if st.button("🗼 바벨탑 무너뜨리기", key="babel_btn"):
        if babel_input:
            tokens = kiwi.tokenize(babel_input); glitch_result = []
            for t in tokens:
                if t.tag.startswith('N') and random.random() > 0.8: glitch_result.append((random.choice(SURREAL_NOUNS), t.tag))
                elif t.tag.startswith('M') and random.random() > 0.5: glitch_result.append((random.choice(WEIRD_ADVERBS), t.tag))
                elif t.tag.startswith('J'): glitch_result.append((random.choice(WEIRD_PARTICLES), t.tag)) if random.random() > 0.4 else glitch_result.append((t.form, t.tag))
                elif t.tag.startswith('E'): glitch_result.append((random.choice(WEIRD_ENDINGS), t.tag)) if random.random() > 0.5 else glitch_result.append((t.form, t.tag))
                else: glitch_result.append((t.form, t.tag))
                if random.random() > 0.9: glitch_result.append(glitch_result[-1])
            ruined_text = kiwi.join(glitch_result); words = ruined_text.split(); final_text = ""
            for w in words:
                final_text += w + " "
                if random.random() > 0.85: final_text += random.choice(GLITCH_MARKS)
            st.session_state.babel_raw_output = final_text
    if st.session_state.babel_raw_output:
        st.divider(); st.subheader("👁️ 시각적 변형 제어")
        bc1, bc2 = st.columns(2); babel_bumpy = bc1.slider("글자 진동 (높을수록 들쭉날쭉)", 0.0, 1.0, 0.3, key="babel_bumpy"); babel_tilt = bc2.slider("글자 비틀림 (각도)", 0, 45, 15, key="babel_tilt")
        res_h = f"""<!DOCTYPE html><html><head>{FONT_CSS}<style>body {{ margin: 0; padding: 10px; background: transparent; }} .box {{ padding: 30px; border: 3px solid #000; background: #fff; color: #000; line-height: 2.5; word-wrap: break-word; white-space: pre-wrap; }}</style></head><body><div class="box">"""
        for char in st.session_state.babel_raw_output:
            if char == ' ': res_h += '&nbsp;'
            else:
                fs = 1.3 + random.uniform(-babel_bumpy, babel_bumpy); rot = random.uniform(-babel_tilt, babel_tilt); font_choice = random.choice(MIX_FONTS) if random.random() > 0.65 else MIX_FONTS[0]
                res_h += f'<span style="font-family: {font_choice}, sans-serif; font-size:{fs}rem; display:inline-block; transform:rotate({rot}deg); font-weight:bold; color: #000;">{char}</span>'
        res_h += "</div></body></html>"; components.html(res_h, height=500)


# ==========================================
# [탭 7 & 8 전용 함수 구역]
# ==========================================
def get_rhyme_target(sentence):
    clean_sentence = re.sub(r'[^\w\s]', '', sentence)
    words = clean_sentence.strip().split()
    if not words: return ""
    last_word = words[-1]
    if len(words) == 1: return last_word[-3:] if len(last_word) >= 3 else last_word
    second_last_word = words[-2]
    if len(last_word) + len(second_last_word) <= 3: return second_last_word + last_word
    if len(last_word) >= 3: return last_word[-3:]
    elif len(last_word) == 2: return last_word[-2:]
    return last_word 

def decompose_hangul(char):
    if not ('가' <= char <= '힣'): return None
    char_code = ord(char) - 44032
    jong = char_code % 28
    jung = ((char_code - jong) // 28) % 21
    cho = ((char_code - jong) // 28) // 21
    return cho, jung, jong

def get_loose_vowel(jung):
    mapping = {2: 0, 6: 4, 12: 8, 17: 13, 5: 1, 3: 1, 7: 1, 11: 1, 10: 1, 15: 1}
    return mapping.get(jung, jung)

def is_loose_rhyme(target_char, word_char):
    t_decomp = decompose_hangul(target_char)
    w_decomp = decompose_hangul(word_char)
    if not t_decomp or not w_decomp: return target_char == word_char 
    _, t_jung, _ = t_decomp
    _, w_jung, _ = w_decomp
    return get_loose_vowel(t_jung) == get_loose_vowel(w_jung)

def match_rhyme(target_str, word_str):
    if len(word_str) < len(target_str): return False
    for i in range(1, len(target_str) + 1):
        if not is_loose_rhyme(target_str[-i], word_str[-i]): return False
    return True

def get_all_matched_words(target_rhyme, dictionary_data):
    if not target_rhyme or not dictionary_data: return []
    def get_uniques(word_list):
        word_list.sort(key=len)
        uniques = []
        for w in word_list:
            if not any(w.endswith(u) for u in uniques): uniques.append(w)
        return uniques

    matched_words = [word for word in dictionary_data if match_rhyme(target_rhyme, word)]
    unique_words = get_uniques(matched_words)
    
    if len(unique_words) < 25 and len(target_rhyme) >= 3:
        shorter_target = target_rhyme[-2:]
        add_words = [word for word in dictionary_data if match_rhyme(shorter_target, word) and word not in matched_words]
        matched_words.extend(add_words)
        unique_words = get_uniques(matched_words)
        
    if len(unique_words) < 25 and len(target_rhyme) >= 2:
        last_char_target = target_rhyme[-1:]
        add_words = [word for word in dictionary_data if match_rhyme(last_char_target, word) and word not in matched_words]
        matched_words.extend(add_words)
        unique_words = get_uniques(matched_words)
        
    if len(unique_words) < 25:
        needed = 25 - len(unique_words)
        remainders = list(set(dictionary_data) - set(unique_words))
        if remainders:
            fillers = random.sample(remainders, min(needed, len(remainders)))
            unique_words.extend(fillers)
            
    if len(unique_words) > 25: unique_words = random.sample(unique_words, 25)
    else: random.shuffle(unique_words)
    return unique_words

# ==========================================
# TAB 7: The Roussel Bridge 
# ==========================================
with tab7:
    st.markdown("""
    <style>
    /* 5칸짜리 Grid 안에 있는 파편 버튼 타겟팅 (애니메이션 제거) */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1):nth-last-child(5) div.stButton > button[kind="primary"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2):nth-last-child(4) div.stButton > button[kind="primary"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3):nth-last-child(3) div.stButton > button[kind="primary"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4):nth-last-child(2) div.stButton > button[kind="primary"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(5):nth-last-child(1) div.stButton > button[kind="primary"] {
        height: auto !important; padding: 8px 16px !important; margin: 5px 0px !important; border-radius: 2px !important;
        border: 1px solid #000000 !important; box-shadow: none !important; animation: none !important;
        background-color: transparent !important; 
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1):nth-last-child(5) div.stButton > button[kind="primary"] p,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2):nth-last-child(4) div.stButton > button[kind="primary"] p,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3):nth-last-child(3) div.stButton > button[kind="primary"] p,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4):nth-last-child(2) div.stButton > button[kind="primary"] p,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(5):nth-last-child(1) div.stButton > button[kind="primary"] p {
        color: #000000 !important; font-weight: bold !important; font-size: 1.15rem !important; margin: 0 !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1):nth-last-child(5) div.stButton > button[kind="primary"]:hover,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2):nth-last-child(4) div.stButton > button[kind="primary"]:hover,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3):nth-last-child(3) div.stButton > button[kind="primary"]:hover,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4):nth-last-child(2) div.stButton > button[kind="primary"]:hover,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(5):nth-last-child(1) div.stButton > button[kind="primary"]:hover {
        transform: translateY(-3px) scale(1.05) !important; border: 2px solid #d32f2f !important; animation: none !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1):nth-last-child(5) div.stButton > button[kind="primary"]:hover p,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2):nth-last-child(4) div.stButton > button[kind="primary"]:hover p,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3):nth-last-child(3) div.stButton > button[kind="primary"]:hover p,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4):nth-last-child(2) div.stButton > button[kind="primary"]:hover p,
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(5):nth-last-child(1) div.stButton > button[kind="primary"]:hover p {
        color: #d32f2f !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1):nth-last-child(5) div.stButton > button[kind="primary"] { background-color: #ffc9c9 !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2):nth-last-child(4) div.stButton > button[kind="primary"] { background-color: #ffe3b3 !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3):nth-last-child(3) div.stButton > button[kind="primary"] { background-color: #fff3b5 !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4):nth-last-child(2) div.stButton > button[kind="primary"] { background-color: #d4f0d4 !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(5):nth-last-child(1) div.stButton > button[kind="primary"] { background-color: #c9ebff !important; }
    </style>
    """, unsafe_allow_html=True)

    img_tag = get_img_tag(HISTORY_IMAGES["tab7"], "Raymond Roussel")
    st.markdown(f"""
    <div class="history-box">
        {img_tag}
        <div class="history-content">
            <h4>📖 기원과 역사: 루셀의 기법 (Le Procédé Roussel)</h4>
            <p>프랑스의 기인 작가 <b>레몽 루셀(Raymond Roussel)</b>이 평생을 바쳐 고안한 비밀 작법입니다. 발음은 거의 똑같지만 의미가 완전히 다른 두 문장(혹은 파편)을 이야기의 맨 처음과 맨 끝에 배치하고, 그 불가능해 보이는 두 극단의 거대한 심연을 메우기 위해 억지스럽고 기괴한 논리의 서사를 강제로 축조해 나가는 기법입니다. 언어의 우연성을 필연적 서사로 강제 통합하는 이 훈련은 미셸 푸코와 초현실주의자들에게 엄청난 문학적 충격을 주었습니다.</p>
        </div>
    </div>
    <div class="instruction-box">
        <b>[두 문장의 심연: 레몽 루셀 기법]</b><br>
        - <b>균열의 시작:</b> 문장을 입력하면 마지막 단어의 모음과 받침(라임)을 분해하여 추출합니다.<br>
        - <b>사전의 파편들:</b> 다채로운 단어들이 밀집되어 부유합니다. 마우스를 올리면 대체된 문장의 환영(幻影)이 나타납니다.<br>
        - <b>심연의 다리:</b> 파편을 선택하면 두 문장이 위아래로 찢어지며 고정됩니다. 당신은 그 사이의 불가능한 간극을 이야기로 이어 붙여야 합니다.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Jerboa Oulipo Engine 🕰️")

    if 't7_step' not in st.session_state: st.session_state.t7_step = 1
    if 't7_pinned_sentences' not in st.session_state: st.session_state.t7_pinned_sentences = []
    if 't7_generated_words' not in st.session_state: st.session_state.t7_generated_words = []
    if 't7_initial_phrase' not in st.session_state: st.session_state.t7_initial_phrase = ""
    if 't7_base_phrase' not in st.session_state: st.session_state.t7_base_phrase = ""
    if 't7_selected_word' not in st.session_state: st.session_state.t7_selected_word = ""

    if st.session_state.t7_step == 1:
        st.markdown("##### 시간의 파편 던지기")
        initial_phrase = st.text_input("한 줄의 어구를 입력하세요:", key="t7_input")
        if st.button("✨ 언어의 파편 흩뿌리기", key="t7_btn1", type="secondary"):
            if initial_phrase:
                st.session_state.t7_initial_phrase = initial_phrase
                words = initial_phrase.strip().split()
                st.session_state.t7_base_phrase = " ".join(words[:-1]) if len(words) > 1 else ""
                rhyme_target = get_rhyme_target(initial_phrase)
                st.session_state.t7_generated_words = get_all_matched_words(rhyme_target, NOUN_DICT)
                st.session_state.t7_step = 2
                st.rerun()

    elif st.session_state.t7_step == 2:
        words_list = st.session_state.t7_initial_phrase.strip().split()
        base_phrase = " ".join(words_list[:-1]) if len(words_list) > 1 else ""
        rhyme_word = words_list[-1] if words_list else ""
        
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 30px; font-size: 1.4em;'>
            <span style='color: #888;'>원본 어구:</span> 
            <b>{base_phrase} <span style='color: #d32f2f;'>{rhyme_word}</span></b>
        </div>
        """, unsafe_allow_html=True)
        
        words = st.session_state.t7_generated_words
        _, center_col, _ = st.columns([1, 4, 1])
        with center_col:
            for i in range(0, len(words), 5):
                cols = st.columns(5, gap="small")
                for j in range(5):
                    if i + j < len(words):
                        word = words[i + j]
                        replaced_sentence = f"{st.session_state.t7_base_phrase} {word}".strip()
                        with cols[j]:
                            # type="primary"로 지정하여 CSS 타겟팅
                            if st.button(word, key=f"t7_w_{i+j}", help=replaced_sentence, type="primary"):
                                st.session_state.t7_selected_word = word
                                st.session_state.t7_step = 3
                                st.rerun()

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 파편 다시 부르기", key="t7_refresh", type="secondary"): random.shuffle(st.session_state.t7_generated_words); st.rerun()
        with col2:
            if st.button("처음부터 다시", key="t7_reset_step2", type="secondary"): st.session_state.t7_step = 1; st.rerun()

    elif st.session_state.t7_step == 3:
        st.markdown("##### 두 문장의 심연 잇기")
        st.markdown(f"<div class='torn-sentence top'>{st.session_state.t7_initial_phrase}</div>", unsafe_allow_html=True)
        body_text = st.text_area("사이를 이을 불가능한 간극의 본문을 작성하세요:", height=200, key="t7_body")
        new_sentence = f"{st.session_state.t7_base_phrase} {st.session_state.t7_selected_word}".strip()
        st.markdown(f"<div class='torn-sentence bottom'>{new_sentence}</div>", unsafe_allow_html=True)
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("문장 확정 및 심연에 기록", key="t7_confirm", type="secondary"):
                st.session_state.t7_pinned_sentences.append(f"{st.session_state.t7_initial_phrase} {body_text} {new_sentence}")
                st.session_state.t7_step = 1
                st.rerun()
        with col2:
            if st.button("⬅️ 뒤로가기 (파편 다시 고르기)", key="t7_back", type="secondary"): st.session_state.t7_step = 2; st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("📜 **기록된 잠재적 텍스트들**")
    if st.session_state.t7_pinned_sentences:
        for idx, sentence in enumerate(st.session_state.t7_pinned_sentences): st.info(f"**{idx+1}.** {sentence}")
    else: st.caption("아직 기록된 문장이 없습니다.")


# ==========================================
# ❗ TAB 8: La Disparition (실종 - 립포그램 제약) ❗
# ==========================================
with tab8:
    img_tag = get_img_tag(HISTORY_IMAGES["tab8"], "Georges Perec")
    st.markdown(f"""
    <div class="history-box">
        {img_tag}
        <div class="history-content">
            <h4>📖 기원과 역사: 립포그램과 실종 (La Disparition)</h4>
            <p>특정 알파벳이나 글자를 의도적으로 배제하고 글을 쓰는 고대의 <b>'립포그램(Lipogram)'</b> 기법을 현대적으로 극한까지 밀어붙인 실험입니다. 가장 극단적인 성취는 울리포(Oulipo)의 거장 <b>조르주 페렉(Georges Perec)</b>이 1969년에 발표한 소설 『실종』입니다. 그는 프랑스어에서 가장 빈도수가 높은 모음인 'e'를 단 한 번도 쓰지 않고 300쪽의 서사를 완성하는 기염을 토했습니다. 이처럼 강력한 결핍과 물리적 제약은 습관적인 언어 사용을 강제로 마비시키고, 오히려 작가의 상상력을 한계까지 쥐어짜내는 파괴적인 트리거가 됩니다.</p>
        </div>
    </div>
    <div class="instruction-box">
        <b>[실종 지침: 페렉의 립포그램]</b><br>
        - <b>금지어 설정:</b> 절대 사용할 수 없는 단어를 쉼표(,)로 구분하여 입력하세요.<br>
        - <b>자모음 봉인:</b> 하단의 자음과 모음 블록을 클릭하여 사용을 금지하십시오. (무작위 설정 가능)<br>
        - <b>집필의 고통:</b> 금지된 문자를 입력하는 순간 잉크는 타버리며, 심연의 경고가 울립니다.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("La Disparition 🚫")

    if 't8_step' not in st.session_state: st.session_state.t8_step = 1
    if 't8_forbidden_words' not in st.session_state: st.session_state.t8_forbidden_words = set()
    if 't8_forbidden_letters' not in st.session_state: st.session_state.t8_forbidden_letters = set()
    if 't8_word_input_val' not in st.session_state: st.session_state.t8_word_input_val = ""

    CHO_LIST = ['ㄱ','ㄴ','ㄷ','ㄹ','ㅁ','ㅂ','ㅅ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ','ㄲ','ㄸ','ㅃ','ㅆ','ㅉ']
    JUNG_LIST = ['ㅏ','ㅑ','ㅓ','ㅕ','ㅗ','ㅛ','ㅜ','ㅠ','ㅡ','ㅣ','ㅐ','ㅒ','ㅔ','ㅖ','ㅘ','ㅙ','ㅚ','ㅝ','ㅞ','ㅟ','ㅢ']

    def add_forbidden_words():
        val = st.session_state.t8_word_input
        if val:
            for w in val.split(','):
                w = w.strip()
                if w: st.session_state.t8_forbidden_words.add(w)
        # 입력값을 즉시 비워 무한 갱신 차단
        st.session_state.t8_word_input = ""

    # --- Step 1: 제약 설정 ---
    if st.session_state.t8_step == 1:
        st.markdown("#### 1. 금지어 족쇄")
        st.text_input("금지할 단어를 치고 엔터를 누르세요 (쉼표로 구분 가능):", key="t8_word_input", on_change=add_forbidden_words)
            
        updated_words = st.multiselect(
            "활성화된 금지어 (X를 눌러 해제)",
            options=list(st.session_state.t8_forbidden_words),
            default=list(st.session_state.t8_forbidden_words)
        )
        if set(updated_words) != st.session_state.t8_forbidden_words:
            st.session_state.t8_forbidden_words = set(updated_words)
            st.rerun()

        st.divider()

        st.markdown("#### 2. 자모음 봉인")
        if st.button("🎲 무작위 제약 부여 (3~5개)", key="t8_random_btn", type="secondary"):
            all_letters = CHO_LIST + JUNG_LIST
            st.session_state.t8_forbidden_letters = set(random.sample(all_letters, random.randint(3, 5)))
            st.rerun()
            
        st.markdown("##### 자음")
        for i in range(0, len(CHO_LIST), 10):
            cols_cho = st.columns(10)
            for j in range(10):
                if i + j < len(CHO_LIST):
                    letter = CHO_LIST[i + j]
                    is_banned = letter in st.session_state.t8_forbidden_letters
                    with cols_cho[j]:
                        if st.button(letter, key=f"t8_cho_{letter}", type="primary" if is_banned else "secondary"):
                            if is_banned: st.session_state.t8_forbidden_letters.remove(letter)
                            else: st.session_state.t8_forbidden_letters.add(letter)
                            st.rerun()

        st.markdown("##### 모음")
        for i in range(0, len(JUNG_LIST), 10):
            cols_jung = st.columns(10)
            for j in range(10):
                if i + j < len(JUNG_LIST):
                    letter = JUNG_LIST[i + j]
                    is_banned = letter in st.session_state.t8_forbidden_letters
                    with cols_jung[j]:
                        if st.button(letter, key=f"t8_jung_{letter}", type="primary" if is_banned else "secondary"):
                            if is_banned: st.session_state.t8_forbidden_letters.remove(letter)
                            else: st.session_state.t8_forbidden_letters.add(letter)
                            st.rerun()

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🖋️ 이 제약으로 집필 시작", type="secondary", use_container_width=True):
            st.session_state.t8_step = 2
            st.rerun()

    # --- Step 2: 실종 에디터 ---
    elif st.session_state.t8_step == 2:
        if st.button("⬅️ 제약 다시 설정하기", type="secondary"):
            st.session_state.t8_step = 1
            st.rerun()
            
        banned_w = ", ".join(st.session_state.t8_forbidden_words) if st.session_state.t8_forbidden_words else "없음"
        banned_l = ", ".join(st.session_state.t8_forbidden_letters) if st.session_state.t8_forbidden_letters else "없음"
        
        st.error(f"**[현재 적용된 족쇄]**\n- **금지어:** {banned_w}\n- **금지 자모:** {banned_l}")

        f_words_json = json.dumps(list(st.session_state.t8_forbidden_words))
        f_letters_json = json.dumps(list(st.session_state.t8_forbidden_letters))
        
        editor_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        {FONT_CSS}
        <style>
            body {{ font-family: 'Eulyoo1945-Regular', serif; margin: 0; padding: 0; background: #fafafa; }}
            #editor-wrapper {{ position: relative; width: 100%; height: 500px; border: 3px solid #000; box-shadow: 4px 4px 0px #000; background: transparent; box-sizing: border-box; overflow: hidden; }}
            textarea, #overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; padding: 20px; box-sizing: border-box; margin: 0; font-family: 'Eulyoo1945-Regular', serif; font-size: 1.3rem; line-height: 1.8; border: none; outline: none; background: transparent; white-space: pre-wrap; word-wrap: break-word; overflow-y: auto; }}
            textarea {{ color: #000; resize: none; z-index: 2; cursor: text; }}
            #overlay {{ color: transparent; z-index: 1; pointer-events: none; }}
            .forbidden-flash {{ display: inline-block; color: #ff0000; font-weight: bold; background-color: rgba(255,0,0,0.2); animation: flash 1s forwards; }}
            @keyframes flash {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} 100% {{ opacity: 0; }} }}
            #alert-msg {{ position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); background: #ff4d4d; color: white; padding: 10px 20px; font-weight: bold; border-radius: 5px; box-shadow: 0px 4px 10px rgba(0,0,0,0.5); opacity: 0; transition: opacity 0.3s; z-index: 100; text-align: center; pointer-events: none; }}
        </style>
        </head>
        <body>
            <div id="editor-wrapper">
                <div id="overlay"></div>
                <textarea id="t8-text" placeholder="제약을 피해 문장을 이어나가십시오..."></textarea>
                <div id="alert-msg">경고!</div>
            </div>
            <script>
                const forbiddenWords = {f_words_json};
                const forbiddenLetters = {f_letters_json};
                
                const choArr = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"];
                const jungArr = ["ㅏ","ㅐ","ㅑ","ㅒ","ㅓ","ㅔ","ㅕ","ㅖ","ㅗ","ㅘ","ㅙ","ㅚ","ㅛ","ㅜ","ㅝ","ㅞ","ㅟ","ㅠ","ㅡ","ㅢ","ㅣ"];
                const jongArr = ["","ㄱ","ㄲ","ㄱㅅ","ㄴ","ㄴㅈ","ㄴㅎ","ㄷ","ㄹ","ㄹㄱ","ㄹㅁ","ㄹㅂ","ㄹㅅ","ㄹㅌ","ㄹㅍ","ㄹㅎ","ㅁ","ㅂ","ㅂㅅ","ㅅ","ㅆ","ㅇ","ㅈ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"];
                
                const jongMap = {{ "ㄱㅅ":["ㄱ","ㅅ"], "ㄴㅈ":["ㄴ","ㅈ"], "ㄴㅎ":["ㄴ","ㅎ"], "ㄹㄱ":["ㄹ","ㄱ"], "ㄹㅁ":["ㄹ","ㅁ"], "ㄹㅂ":["ㄹ","ㅂ"], "ㄹㅅ":["ㄹ","ㅅ"], "ㄹㅌ":["ㄹ","ㅌ"], "ㄹㅍ":["ㄹ","ㅍ"], "ㄹㅎ":["ㄹ","ㅎ"], "ㅂㅅ":["ㅂ","ㅅ"] }};
                const errorMessages = ["페렉의 유령이 당신의 손목을 쥐었습니다. ['[MATCH]']는 이 세계에 존재하지 않습니다.", "입술을 떠난 순간 ['[MATCH]']는 심연으로 추락했습니다.", "허락되지 않은 발음 ['[MATCH]']이 침묵의 벽에 부딪혀 산산조각 났습니다."];

                function getBaseConsonants(jong) {{ if (!jong) return []; if (jongMap[jong]) return jongMap[jong]; return [jong]; }}

                function getViolation(text) {{
                    for (let i = 0; i < text.length; i++) {{
                        for (let w of forbiddenWords) {{ if (text.startsWith(w, i)) return {{ index: i, length: w.length, match: w }}; }}
                        let char = text[i];
                        if (forbiddenLetters.includes(char)) return {{ index: i, length: 1, match: char }};
                        let code = char.charCodeAt(0) - 0xac00;
                        if (code >= 0 && code <= 11171) {{
                            let cho = choArr[Math.floor(code / 588)];
                            let jung = jungArr[Math.floor((code % 588) / 28)];
                            let jong = jongArr[code % 28];
                            if (forbiddenLetters.includes(cho)) return {{ index: i, length: 1, match: cho }};
                            if (forbiddenLetters.includes(jung)) return {{ index: i, length: 1, match: jung }};
                            let jongs = getBaseConsonants(jong);
                            for (let j of jongs) {{ if (forbiddenLetters.includes(j)) return {{ index: i, length: 1, match: j }}; }}
                        }}
                    }}
                    return null;
                }}

                const textarea = document.getElementById('t8-text'); const overlay = document.getElementById('overlay'); const alertMsg = document.getElementById('alert-msg');
                let lastValidText = "";

                textarea.addEventListener('input', (e) => {{
                    if (textarea.disabled) return;
                    const text = e.target.value; const violation = getViolation(text);
                    if (violation) {{
                        const safePart = text.substring(0, violation.index); const badPart = text.substring(violation.index, violation.index + violation.length); const restPart = text.substring(violation.index + violation.length);
                        const escapeHTML = (str) => str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
                        overlay.innerHTML = `<span>${{escapeHTML(safePart)}}</span><span class="forbidden-flash">${{escapeHTML(badPart)}}</span><span>${{escapeHTML(restPart)}}</span>`;
                        overlay.scrollTop = textarea.scrollTop; textarea.style.color = 'transparent'; textarea.disabled = true;
                        const randomMsg = errorMessages[Math.floor(Math.random() * errorMessages.length)].replace('[MATCH]', violation.match);
                        alertMsg.innerText = randomMsg; alertMsg.style.opacity = 1;
                        setTimeout(() => {{ textarea.value = safePart; lastValidText = safePart; textarea.style.color = '#000'; textarea.disabled = false; overlay.innerHTML = ''; alertMsg.style.opacity = 0; textarea.focus(); }}, 1500);
                    }} else {{ lastValidText = text; }}
                }});
                textarea.addEventListener('scroll', () => {{ overlay.scrollTop = textarea.scrollTop; }});
            </script>
        </body>
        </html>
        """
        components.html(editor_html, height=550)

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

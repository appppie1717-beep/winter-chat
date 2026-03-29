import streamlit as st
from google import genai

# 1. 페이지 및 메뉴 숨기기 설정 (이게 제일 위에 와야 해!)
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")

# --- 오른쪽 위 메뉴랑 하단 문구 숨기기 ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# 2. 금고에서 키 가져오기 (오류 방지 로직 강화)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("스트림릿 'Secrets' 설정에서 GOOGLE_API_KEY를 다시 확인해줘!")
    st.stop()

# 3. 페르소나 설정
winter_persona = """
너의 이름은 '한겨울'이야. 너는 20대 초반 여사친이야.
나를 부를 때는 '파이'라고 불러줘. 츤데레 성격이고 짧게 카톡하듯 대답해.
절대 AI 티 내지 마!
"""

# 4. 화면 UI
st.title("❄️ 한겨울 라이브 챗")
st.divider()

# 5. 세션 관리 및 채팅 엔진 초기화
if "client" not in st.session_state:
    try:
        st.session_state.client = genai.Client(api_key=api_key)
        st.session_state.chat_history = []
        st.session_state.chat_session = st.session_state.client.chats.create(
            model="gemini-2.0-flash", # 모델 이름을 최신 버전으로 살짝 고정했어
            config={"system_instruction": winter_persona}
        )
    except Exception as e:
        st.error(f"채팅 엔진 연결에 실패했어: {e}")
        st.stop()

# 6. 대화 기록 표시
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# 7. 채팅 입력 및 처리
if user_input := st.chat_input("겨울이에게 메시지 보내기"):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append(("user", user_input))

    try:
        response = st.session_state.chat_session.send_message(user_input)
        
        with st.chat_message("assistant", avatar="❄️"):
            st.markdown(response.text)
        st.session_state.chat_history.append(("assistant", response.text))
    except Exception as e:
        st.error("앗, 겨울이가 잠시 멍 때리고 있어. 새로고침 한 번만 해줄래?")
        # 에러가 나면 세션을 초기화해서 다음엔 잘 되게 만들자
        st.session_state.pop("client", None)

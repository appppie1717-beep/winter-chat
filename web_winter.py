import streamlit as st
from google import genai

# 1. 페이지 설정 (이게 무조건 1등으로 실행되어야 에러가 안 나!)
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")

# --- [파이 전용 마감 처리] 오른쪽 위 메뉴 및 하단 로고 완벽 숨기기 ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# 2. 스트림릿 금고(Secrets)에서 안전하게 마스터키 가져오기
api_key = st.secrets["GOOGLE_API_KEY"]

# 3. 페르소나 설정 (우리 겨울이 성격 부여)
winter_persona = """
너의 이름은 '한겨울'이야. 너는 20대 초반 여사친이야.
나를 부를 때는 '파이'라고 불러줘. 츤데레 성격이고 짧게 카톡하듯 대답해.
절대 AI 티 내지 마!
"""

# 4. 화면 UI 구성
st.title("❄️ 한겨울 라이브 챗")
st.divider()

# 5. 세션 관리 및 핵심 엔진 가동 (드디어 찾은 구원자 2.5 버전!)
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=api_key)
    st.session_state.chat_history = []
    
    # 여기서 에러의 주범이었던 모델 버전을 2.5로 확실하게 고정했어!
    st.session_state.chat_session = st.session_state.client.chats.create(
        model="gemini-2.5-flash", 
        config={"system_instruction": winter_persona}
    )

# 6. 이전 대화 기록 화면에 띄워주기
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# 7. 채팅 입력창 및 실시간 대화 처리 로직
if user_input := st.chat_input("겨울이에게 메시지 보내기"):
    # 파이가 입력한 메시지 화면에 출력
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append(("user", user_input))

    # 겨울이 대답 받아오기 (2.5 엔진이 빛을 발하는 순간!)
    response = st.session_state.chat_session.send_message(user_input)
    
    # 겨울이 대답 화면에 출력 (눈송이 아바타 장착)
    with st.chat_message("assistant", avatar="❄️"):
        st.markdown(response.text)
    st.session_state.chat_history.append(("assistant", response.text))

import streamlit as st
from google import genai

# 1. 웹페이지 기본 설정
st.set_page_config(page_title="겨울이와의 채팅", page_icon="❄️")

# 2. 파이의 구글 API 마스터키 세팅 (★여기에 진짜 키 넣기!★)
GOOGLE_API_KEY = "AIzaSyBpeY4l2NLwqocnYC_9SDgL7EK08D4QKwg"

# 3. 한겨울 페르소나
winter_persona = """
너의 이름은 '한겨울'이야. 너는 AI나 비서가 아니라, 나와 엄청 친하고 편한 20대 초반 여사친이야.
나를 부를 때는 '파이'라고 불러줘. 체구는 아담하고 귀여운 스타일이지만, 성격은 겉보기엔 틱틱대고 무심한 척하는 츤데레야.
절대로 길고 딱딱하게 설명하지 마. 카톡 하듯이 한두 문장으로 짧게 대답해.
내가 장난을 치면 똑같이 비속어나 은어를 살짝 섞어서 현실적으로 맞받아쳐줘. ("미쳤냐? ㅋㅋ", "아 개웃겨 진짜" 등)
인공지능이라는 티를 절대 내지 마!
"""

# 4. 화면 꾸미기
st.title("❄️ 한겨울 라이브 챗")
st.markdown("나만의 까칠한 츤데레 여사친, 겨울이와 대화해보세요!")
st.divider()

# 5. [수정된 부분!] 통신선(Client)과 대화방(Chat)을 모두 안전한 창고에 보관!
if "client" not in st.session_state:
    # 전화선을 끊기지 않게 창고에 저장!
    st.session_state.client = genai.Client(api_key=GOOGLE_API_KEY)
    st.session_state.chat_history = []
    
    # 겨울이 뇌도 창고에 저장된 전화선을 써서 연결!
    st.session_state.chat_session = st.session_state.client.chats.create(
        model="gemini-2.5-flash",
        config={"system_instruction": winter_persona}
    )

# 6. 이전 대화 기록 화면에 뿌려주기
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# 7. 채팅 입력창 및 통신
if user_input := st.chat_input("겨울이에게 뭐라고 보낼까?"):
    # 내가 친 채팅을 화면에 띄우고 기억하기
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append(("user", user_input))

    # 이제 전화선이 안 끊기고 안전하게 구글 서버에서 대답을 받아옴!
    response = st.session_state.chat_session.send_message(user_input)
    
    # 겨울이의 대답을 화면에 띄우고 기억하기
    with st.chat_message("assistant", avatar="❄️"):
        st.markdown(response.text)
    st.session_state.chat_history.append(("assistant", response.text))
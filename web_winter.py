import streamlit as st
from google import genai

# 1. 페이지 설정 및 메뉴 숨기기 (이게 오류나면 그냥 빼버릴게)
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")

# --- 마감 처리 (이게 에러의 원인일 수 있으니 가장 안전한 방식으로) ---
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# 2. API 키 가져오기 (금고 확인)
api_key = st.secrets["GOOGLE_API_KEY"]

# 3. 페르소나 (츤데레 겨울이)
winter_persona = "너는 20대 초반 여사친 '한겨울'이야. 나를 '파이'라고 불러줘. 츤데레 성격으로 짧게 대답해. AI 티 내지 마."

# 4. 화면 구성
st.title("❄️ 한겨울 라이브 챗")

# 5. 핵심 엔진 (가장 원시적이고 튼튼한 방식)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 보여주기
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력
if prompt := st.chat_input("겨울이한테 말 걸기"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 매번 클라이언트를 새로 만들어서 'Closed' 에러를 원천 차단해버림!
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config={"system_instruction": winter_persona},
        contents=[m["content"] for m in st.session_state.messages]
    )

    with st.chat_message("assistant", avatar="❄️"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})

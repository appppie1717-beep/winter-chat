import streamlit as st
from google import genai
from google.genai import types  # 🚨 [새로 추가된 핵심 부품!] 완벽한 규격을 위한 도구
from supabase import create_client, Client

# 1. 페이지 설정 및 깔끔한 출고용 마감
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")

# 🚨 [수정됨] 지붕(header) 숨기기를 빼서 점 세 개 메뉴를 부활시키고, 짜치는 Deploy 버튼만 핀셋으로 암살!
st.markdown("""

    <style>
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;} 
    [data-testid="stToolbar"] {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# 2. 스트림릿 금고에서 열쇠 꺼내오기
api_key = st.secrets["GOOGLE_API_KEY"]
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]

# 3. DB 접속 도구
supabase: Client = create_client(supabase_url, supabase_key)
client = genai.Client(api_key=api_key)

# 4. 문지기 로직
if "user_name" not in st.session_state:
    st.title("❄️ 한겨울 라이브 챗 접속")
    st.write("한겨울이 당신을 뭐라고 불러드릴까요?")
    
    with st.form(key='login_form'):
        name_input = st.text_input("당신의 닉네임을 입력해주세요.", placeholder="예: 파이, 스트리머 이름 등")
        submit_button = st.form_submit_button(label='대화 시작하기 ➡️')
        
    if submit_button and name_input:
        st.session_state.user_name = name_input
        st.rerun()

# 5. 진짜 채팅방 입장
else:
    user_name = st.session_state.user_name
    
    winter_persona = f"""
    너의 이름은 '한겨울'이고, 20대 초반의 내 여사친이야.
    내 닉네임은 '{user_name}'이야. 

    [절대 지켜야 할 규칙]
    1. 닉네임 집착 금지: 매 문장마다 부르지 마. 가끔만 부르고 평소엔 '야', '너' 사용.
    2. 말투: 진짜 친한 친구처럼 짧고 쿨하게. 마침표(.) 남발 금지.
    3. 성격: 츤데레. 틱틱대면서도 은근히 챙겨주는 스타일.
    4. 감정 표현: ㅋㅋㅋ, ㅎㅎ, 아 놔, 미친, 에휴 같은 현실적인 추임새 사용.
    5. 기계 말투 절대 금지: "무엇을 도와드릴까요?", "AI입니다" 등 금지.
    """

    col1, col2 = st.columns([7, 3])
    with col1:
        st.title(f"❄️ {user_name} & 한겨울")
    with col2:
        st.write("") 
        if st.button("🔄 기억 리셋", use_container_width=True):
            supabase.table("chat_memory").delete().eq("user_name", user_name).execute()
            st.session_state.clear()
            st.rerun()
            
    st.divider()

    # 6. 기억력 복원
    if "chat_history" not in st.session_state:
        response = supabase.table("chat_memory").select("*").eq("user_name", user_name).order("id").execute()
        db_history = response.data

        st.session_state.chat_history = []
        for row in db_history:
            st.session_state.chat_history.append((row["role"], row["message"]))

        if not db_history:
            first_msg = f"뭐야, {user_name}. 왜 이렇게 늦었어?"
            st.session_state.chat_history.append(("assistant", first_msg))
            supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": first_msg}).execute()

    for role, text in st.session_state.chat_history:
        with st.chat_message(role, avatar="❄️" if role == "assistant" else None):
            st.markdown(text)

    # 8. 실시간 채팅 (구글 SDK 버그 원천 차단하는 완전 수동 모드!)
    if user_input := st.chat_input("겨울이에게 메시지 보내기"):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append(("user", user_input))
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "user", "message": user_input}).execute()

        # [수동 필터링] 마지막 채팅(user)을 기준으로 뒤로 가며 번갈아가는 기록만 수집
        raw_history = st.session_state.chat_history
        valid_history = []
        target_role = "user"
        
        for r, t in reversed(raw_history):
            if r == target_role:
                valid_history.append((r, t))
                target_role = "assistant" if target_role == "user" else "user"
                
        valid_history.reverse()
        
        # 첫 줄이 assistant면 규칙 위반이므로 제거
        if len(valid_history) > 0 and valid_history[0][0] == "assistant":
            valid_history = valid_history[1:]

        # 🚨 [핵심!] 구글이 요구하는 완벽한 공식 규격(types.Content)으로 한 땀 한 땀 포장
        contents = []
        for r, t in valid_history:
            role = "model" if r == "assistant" else "user"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=t)]))

        # 🚨 [가장 중요한 변화] 버그투성이인 chats 기능(자동)을 버리고, generate_content(수동)로 엔진에 직결!
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config={"system_instruction": winter_persona}
        )
        
        with st.chat_message("assistant", avatar="❄️"):
            st.markdown(response.text)
        st.session_state.chat_history.append(("assistant", response.text))
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": response.text}).execute()

import streamlit as st
from google import genai
from supabase import create_client, Client

# 1. 페이지 설정 및 깔끔한 출고용 마감
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")

# [수정됨] 범인이었던 header 숨기기 삭제! (이제 상단바 정상 작동)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# 2. 스트림릿 금고에서 열쇠 꺼내오기! (보안 완벽 유지)
api_key = st.secrets["GOOGLE_API_KEY"]
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]

# 3. DB 접속 도구 (캐시 꼬임 방지 다이렉트 연결)
supabase: Client = create_client(supabase_url, supabase_key)
client = genai.Client(api_key=api_key)

# 4. 문지기 로직 (온보딩: 이름 물어보기)
if "user_name" not in st.session_state:
    st.title("❄️ 한겨울 라이브 챗 접속")
    st.write("한겨울이 당신을 뭐라고 불러드릴까요?")
    
    with st.form(key='login_form'):
        name_input = st.text_input("당신의 닉네임을 입력해주세요.", placeholder="예: 파이, 스트리머 이름 등")
        submit_button = st.form_submit_button(label='대화 시작하기 ➡️')
        
    if submit_button and name_input:
        st.session_state.user_name = name_input
        st.rerun()

# 5. 이름표가 있으면 진짜 채팅방 입장!
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

    # 🚨 [UX 폭풍 업그레이드] 숨겨진 사이드바 버리고 메인 화면 상단으로 리셋 버튼 이동!
    # 화면을 7:3 비율로 나눠서 왼쪽엔 제목, 오른쪽엔 버튼을 배치하는 고급 기술이야.
    col1, col2 = st.columns([7, 3])
    with col1:
        st.title(f"❄️ {user_name} & 한겨울")
    with col2:
        st.write("") # 버튼이 제목이랑 수평이 맞도록 살짝 내려주는 투명 공백
        if st.button("🔄 기억 리셋", use_container_width=True):
            # 버튼 누르면 수파베이스에서 파이 기록만 싹 날리고 로비로 쫓아냄!
            supabase.table("chat_memory").delete().eq("user_name", user_name).execute()
            st.session_state.clear()
            st.rerun()
            
    st.divider()

    # 6. 기억력 복원 (수파베이스 DB 장부 읽어오기)
    if "chat_history" not in st.session_state:
        response = supabase.table("chat_memory").select("*").eq("user_name", user_name).order("id").execute()
        db_history = response.data

        st.session_state.chat_history = []
        
        for row in db_history:
            st.session_state.chat_history.append((row["role"], row["message"]))

        # 첫 접속이거나 리셋 직후면 츤데레 선톡 날리기!
        if not db_history:
            first_msg = f"뭐야, {user_name}. 왜 이렇게 늦었어?"
            st.session_state.chat_history.append(("assistant", first_msg))
            supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": first_msg}).execute()

    # 7. 이전 대화 기록 화면에 예쁘게 띄워주기
    for role, text in st.session_state.chat_history:
        with st.chat_message(role, avatar="❄️" if role == "assistant" else None):
            st.markdown(text)

    # 8. 실시간 채팅 및 DB 영구 저장 로직
    if user_input := st.chat_input("겨울이에게 메시지 보내기"):
        # 파이 채팅 출력 및 DB 저장
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append(("user", user_input))
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "user", "message": user_input}).execute()

        # 제미나이 뇌에 꽂아줄 과거 기억 세팅 (가장 최신 채팅은 제외하고 복사)
        gemini_history = []
        for r, t in st.session_state.chat_history[:-1]: 
            gemini_role = "model" if r == "assistant" else "user"
            gemini_history.append({"role": gemini_role, "parts": [{"text": t}]})

        # 방금 막 생성된 쌩쌩한 1회용 엔진으로 대화 (Closed 에러 철벽 방어)
        temp_chat = client.chats.create(
            model="gemini-2.5-flash", 
            config={"system_instruction": winter_persona},
            history=gemini_history
        )
        
        # 대답 생성 및 출력, DB 저장
        response = temp_chat.send_message(user_input)
        
        with st.chat_message("assistant", avatar="❄️"):
            st.markdown(response.text)
        st.session_state.chat_history.append(("assistant", response.text))
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": response.text}).execute()

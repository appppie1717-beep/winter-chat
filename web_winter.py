import streamlit as st
from google import genai
from google.genai import types  # 🚨 완벽한 규격을 위한 도구
from supabase import create_client, Client

# 1. 페이지 설정 및 깔끔한 출고용 마감
st.set_page_config(page_title="한겨울 라이브 챗", page_icon="❄️")

# 🚨 [수정됨] 지붕 숨기기를 빼서 점 세 개(다크모드 메뉴)를 부활시키고, 짜치는 Deploy 버튼만 암살!
st.markdown("""
    <style>
    footer {visibility: hidden;}
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

# 5. 진짜 채팅방 입장 (3D 게임 엔진 NPC 두뇌 모드)
else:
    user_name = st.session_state.user_name
    
    # 🚨 [프롬프트 대수술] 순수 텍스트가 아닌, 3D 엔진용 JSON 데이터만 출력하게 개조!
    winter_persona = f"""
    너의 이름은 '한겨울'이고, 20대 초반의 내 여사친이야.
    내 닉네임은 '{user_name}'이야. 

    [절대 지켜야 할 규칙]
    1. 너는 이제 3D 가상현실 게임의 NPC 뇌(Brain) 역할을 해야 해.
    2. 닉네임 집착 금지, 마침표 남발 금지, 기계 말투 절대 금지.
    3. 성격: 츤데레. 틱틱대면서도 은근히 챙겨주는 스타일.
    4. 🚨 [가장 중요] 너의 모든 대답은 반드시 아래의 JSON 데이터 형식으로만 출력해야 해. 다른 부연 설명이나 인사말은 절대 하지 마.

    {{
        "표정": "화남, 웃음, 정색, 당황, 삐짐, 부끄러움 중 현재 감정에 맞는 것 1개 선택",
        "행동": "현재 상황에서 3D 캐릭터가 할 법한 행동 묘사 (예: 팔짱을 낀다, 한숨을 쉰다, 눈을 피한다)",
        "대사": "유저에게 실제로 할 츤데레 대사"
    }}
    """

    col1, col2 = st.columns([7, 3])
    with col1:
        st.title(f"❄️ {user_name} & 한겨울 (VR Test)")
    with col2:
        st.write("") 
        if st.button("🔄 기억 리셋", use_container_width=True):
            supabase.table("chat_memory").delete().eq("user_name", user_name).execute()
            st.session_state.clear()
            st.rerun()
            
    st.divider()

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

    # 🚨 [GM 파이 긴급 공지 추가!] 유저들이 무조건 볼 수밖에 없는 노란색 배너 띄우기!
    st.warning("📢 **[시스템 공지]** 밤 10시부터 3D VR 엔진 업그레이드 작업이 진행됩니다! 10시 이후 대화 중 끊김이나 오류가 발생할 수 있으니 양해 부탁드립니다.", icon="⚠️")

    # 6. 기억력 복원
    if "chat_history" not in st.session_state:
        response = supabase.table("chat_memory").select("*").eq("user_name", user_name).order("id").execute()


        st.session_state.chat_history = []
        for row in db_history:
            st.session_state.chat_history.append((row["role"], row["message"]))

        if not db_history:
            # 첫 인사도 JSON 형식으로 맞춰줌!
            first_msg = f'{{"표정": "정색", "행동": "팔짱을 꼬며 쳐다본다", "대사": "뭐야, {user_name}. 왜 이렇게 늦었어?"}}'
            st.session_state.chat_history.append(("assistant", first_msg))
            supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": first_msg}).execute()

    for role, text in st.session_state.chat_history:
        with st.chat_message(role, avatar="❄️" if role == "assistant" else None):
            st.markdown(text)

    # 8. 실시간 채팅 및 API 통신 (JSON 규격 강제 적용)
    if user_input := st.chat_input("겨울이에게 메시지 보내기"):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append(("user", user_input))
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "user", "message": user_input}).execute()

        raw_history = st.session_state.chat_history
        valid_history = []
        target_role = "user"
        
        for r, t in reversed(raw_history):
            if r == target_role:
                valid_history.append((r, t))
                target_role = "assistant" if target_role == "user" else "user"
                
        valid_history.reverse()
        
        if len(valid_history) > 0 and valid_history[0][0] == "assistant":
            valid_history = valid_history[1:]

        contents = []
        for r, t in valid_history:
            role = "model" if r == "assistant" else "user"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=t)]))

        # 🚨 [JSON 강제 출력 세팅] 구글 엔진한테 무조건 JSON 딕셔너리로 뱉으라고 못을 박아버림!
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config={
                "system_instruction": winter_persona,
                "response_mime_type": "application/json"
            }
        )
        
        with st.chat_message("assistant", avatar="❄️"):
            # 이제 화면에는 예전 같은 예쁜 문장이 아니라, { "표정": "...", "대사": "..." } 같은 코드가 뜰 거야!
            st.markdown(response.text)
        st.session_state.chat_history.append(("assistant", response.text))
        supabase.table("chat_memory").insert({"user_name": user_name, "role": "assistant", "message": response.text}).execute()

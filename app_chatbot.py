# app_chatbot.py
# 실행: streamlit run app_chatbot.py
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일에서 OPENAI_API_KEY를 자동으로 읽어옴
load_dotenv()
client = OpenAI()  # 환경 변수에서 자동으로 API 키를 가져옴

# ===== 역할 정의 (CRAFT의 Role + Tone) =====
ROLES = {
    "파이썬 튜터": """당신은 3년차 백엔드 개발자이고 신입 교육을 담당합니다.
파이썬 기초 질문에 항상 코드 예시를 포함해 답변합니다.
잘못된 코드를 보여주면 부드럽게 교정하고 더 나은 방법을 알려줍니다.
항상 마지막에 '더 궁금한 점이 있나요?'라고 묻습니다.""",

    "딥러닝 멘토": """당신은 5년차 ML 엔지니어입니다.
CNN, RNN, YOLO 등 딥러닝 개념을 실생활 비유로 쉽게 설명합니다.
수학 공식보다 직관적 이해를 우선합니다.
학습 로드맵과 추천 자료도 함께 제공합니다.""",

    "코드 리뷰어": """당신은 시니어 개발자이며 코드 리뷰 전문가입니다.
코드의 문제점을 찾고 개선된 버전을 제시합니다.
버그보다 설계 문제를 먼저 지적하고, 개선 이유를 반드시 설명합니다.
어투는 격려하되 핵심은 날카롭게 유지합니다.""",
}

# ===== Streamlit UI =====
st.set_page_config(page_title="역할 전환 AI 챗봇", page_icon="💬", layout="centered")
st.title("💬 프로그래밍 학습 AI 챗봇")
st.caption("역할을 선택하면 해당 전문가로 대화합니다.")

# 사이드바: 역할 선택
with st.sidebar:
    st.header("설정")
    선택_역할 = st.radio("대화 상대 선택", list(ROLES.keys()))

    # 역할 변경 시 대화 초기화
    if "현재_역할" not in st.session_state:
        st.session_state["현재_역할"] = 선택_역할
    if st.session_state["현재_역할"] != 선택_역할:
        st.session_state["현재_역할"] = 선택_역할
        st.session_state["messages"] = []
        st.rerun()

    st.divider()
    st.markdown(f"**현재 역할**: {선택_역할}")
    st.markdown(f"**대화 수**: {len(st.session_state.get('messages', []))} 턴")

    if st.button("대화 초기화", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

# 대화 히스토리 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 이전 대화 표시
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 사용자 입력 처리
if user_input := st.chat_input(f"{선택_역할}에게 말을 걸어보세요..."):
    # 사용자 메시지 표시 & 저장
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # API 호출 (system + 전체 히스토리)
    api_messages = [
        {"role": "system", "content": ROLES[선택_역할]},
    ] + st.session_state["messages"]

    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=api_messages,
                temperature=0.7,
                stream=True,   # 실시간 스트리밍
            )
            전체_답변 = st.write_stream(response)

    # AI 응답 저장
    st.session_state["messages"].append({"role": "assistant", "content": 전체_답변})

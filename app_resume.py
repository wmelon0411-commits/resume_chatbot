# app_resume.py
# 실행: streamlit run app_resume.py
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일에서 OPENAI_API_KEY를 자동으로 읽어옴
load_dotenv()
client = OpenAI()

# ===== 직무별 Few-shot 예시 =====
EXAMPLES = {
    "마케팅": [
        {"role": "user", "content": "자소서: '마케팅에 관심이 있고 열심히 하겠습니다.'\n직무: 마케팅"},
        {"role": "assistant", "content": """**강점**
1. 마케팅 직무에 대한 관심을 표현했습니다.
2. 열정과 의지를 보여주었습니다.
3. 간결한 표현을 사용했습니다.

**개선점**
1. 구체적인 경험이나 성과가 없어 역량 증명이 부족합니다.
2. '열심히 하겠습니다'는 모든 지원자가 쓰는 표현으로 차별화가 없습니다.
3. 마케팅의 어떤 분야(디지털, 콘텐츠, 브랜딩)에 관심이 있는지 불명확합니다.

**수정된 자소서**
대학 동아리에서 인스타그램 계정을 운영하며 팔로워를 500명에서 3,000명으로 성장시킨 경험이 있습니다.
콘텐츠 기획부터 성과 분석까지 직접 수행하며, 데이터 기반 마케팅의 중요성을 체감했습니다.
이 경험을 바탕으로 귀사의 디지털 마케팅 팀에서 실질적인 성과를 만들어내겠습니다."""},
    ],
}

# ===== 첨삭 함수 =====
def review_resume(job: str, content: str) -> str:
    system = """당신은 IT 기업 인사 담당자이며 10년 경력의 자기소개서 전문 멘토입니다.
항상 다음 형식으로 출력하세요:
**강점** (3개) → **개선점** (3개) → **수정된 자소서** (완성본)"""

    few_shot = EXAMPLES.get(job, EXAMPLES["마케팅"])
    messages = [
        {"role": "system", "content": system},
        *few_shot,
        {"role": "user", "content": f"자소서: '{content}'\n직무: {job}"},
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
        temperature=0.5,
    )
    return response.choices[0].message.content

# ===== Streamlit UI =====
st.set_page_config(page_title="자소서 첨삭", page_icon="📝", layout="centered")
st.title("📝 자기소개서 첨삭 서비스")
st.caption("직무를 선택하고 자소서를 입력하면 맞춤 피드백을 드립니다.")

job_role = st.selectbox("지원 직무", ["마케팅", "기획/PM", "디자인", "개발", "영업"])
resume_input = st.text_area("자기소개서 입력", height=200, placeholder="첨삭받을 내용을 입력하세요.")

if resume_input:
    st.caption(f"입력 글자 수: {len(resume_input)}자")

if st.button("첨삭하기", type="primary", use_container_width=True):
    if not resume_input or len(resume_input.strip()) < 20:
        st.warning("최소 20자 이상 입력해주세요.")
    else:
        with st.spinner(f"{job_role} 직무 기준으로 첨삭 중..."):
            result = review_resume(job_role, resume_input)

        st.divider()
        st.subheader(f"첨삭 결과 — {job_role}")
        st.markdown(result)

        st.download_button(
            label="결과 저장 (.txt)",
            data=result,
            file_name=f"자소서_첨삭_{job_role}.txt",
        )

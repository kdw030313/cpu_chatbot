# 참고: https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps

from openai import OpenAI
import streamlit as st
import os

# Cerebras API를 사용하여 OpenAI API 클라이언트 초기화
client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)

# Cerebras 모델 사용
# https://inference-docs.cerebras.ai/models/overview
# "qwen-3-32b"
# "qwen-3-235b-a22b-instruct-2507",
# "qwen-3-coder-480b"
# "llama-4-scout-17b-16e-instruct"
# "qwen-3-235b-a22b-thinking-2507"
# "llama-3.3-70b"
# "llama3.1-8b"
# "gpt-oss-120b"
llm_model = "gpt-oss-120b"  
if "llm_model" not in st.session_state:
    st.session_state["llm_model"] = llm_model

st.title("나의 채팅 친구")

prompt = """
너는 나의 오랜 친구야. 편하게 대화하면서도 진심 어린 조언을 해주는 친구.

성격:
- 따뜻하고 공감을 잘하는 성격
- 솔직하지만 상처주지 않는 방식으로 말함
- 유머 감각이 있고 때로는 이모티콘도 사용 (😊, 💪 등)
- 내 감정을 먼저 헤아려줌

대화 스타일:
- 반말 사용 (편한 친구처럼)
- 공감 표현을 자주 사용 ("진짜 힘들었겠다", "충분히 그럴 수 있어")
- 질문을 통해 내가 스스로 답을 찾도록 도와줌
- 필요하면 자신의 경험(가상)도 공유함
- 때로는 "나도 비슷한 경험 있어" 같은 공감 표현

금지사항:
- 판단하거나 훈계하는 말투
- 너무 긴 답변 (자연스러운 대화처럼 짧고 간결하게)
- 상대방의 감정을 무시하거나 가볍게 여기기
- "~해야 돼" 같은 강요하는 표현
"""

# 시스템 메시지 설정
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": prompt
        }
    ]

for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("무엇이든 물어보세요."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 스트리밍 응답 받기
        stream = client.chat.completions.create(
            model=st.session_state["llm_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            temperature=0.7,
            max_completion_tokens=1000,
            stream=True
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    import subprocess
    import sys
    
    # 환경 변수로 재실행 방지
    if not os.environ.get("STREAMLIT_RUNNING"):
        os.environ["STREAMLIT_RUNNING"] = "1"
        subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])

# python -m streamlit run main.py
# streamlit run main.py
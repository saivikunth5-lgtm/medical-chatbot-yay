import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()  

api_key = os.getenv("OPENAI_API_KEY")



try:
    from openai import OpenAI
    NEW_SDK = True
except Exception:
    import openai
    NEW_SDK = False

APP_TITLE = "⚕️ MED-INTEL — Your AI Healthcare Assistant"

SYSTEM_PROMPT = (
    "You are MED-INTEL, a careful, evidence-informed healthcare assistant. "
    "Provide clear, structured answers in simple language. "
    "When relevant, include typical symptoms, red flags, differential considerations, "
    "self-care guidance, and when to seek in-person care. "
    "Cite authoritative public sources (e.g., WHO/CDC/NHS) in plain text when possible. "
    "NEVER give definitive diagnoses, prescriptions, or instructions that require a clinician. "
    "ALWAYS include: 'I am not a doctor—this is not medical advice.' "
    "If user shares sensitive info, be respectful and privacy-conscious. "
    "If the query suggests an emergency, urge immediate in-person care."
)

EMERGENCY_KEYWORDS = [
    "chest pain", "pressure in chest", "heart attack", "stroke",
    "suicidal", "suicide", "homicidal", "overdose", "fainting",
    "severe bleeding", "difficulty breathing", "shortness of breath",
    "not breathing", "seizure", "confusion new", "slurred speech",
    "one-sided weakness", "anaphylaxis", "severe allergic", "burn large"
]

st.set_page_config(page_title="MED-INTEL", page_icon="⚕️", layout="centered")
st.title(APP_TITLE)

st.markdown(
    " **Disclaimer:** I am not a doctor—this is not medical advice. "
    "For emergencies, call your local emergency number immediately."
)

with st.sidebar:
    st.header("🔧 Settings")
    st.caption("API key is read from your environment.")
    show_sources = st.toggle("Add short source suggestions", value=True)
    temp = st.slider("Creativity (temperature)", 0.0, 1.0, 0.3, 0.05)
    max_tokens = st.slider("Max response tokens", 256, 1200, 700, 32)


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]


def maybe_show_emergency_notice(user_text: str):
    lt = user_text.lower()
    if any(k in lt for k in EMERGENCY_KEYWORDS):
        st.error(
            "🚨 This may be a medical emergency. "
            "Please call your local emergency number or seek in-person care **now**."
        )

def append_footer(text: str):
    footer = "\n\n—\nI am not a doctor—this is not medical advice."
    if show_sources:
        footer += (
            "\nFor reputable information, see: WHO, CDC, NHS, MedlinePlus."
        )
    return text.strip() + footer


for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message("assistant" if m["role"] == "assistant" else "user"):
            st.markdown(m["content"])

user_input = st.chat_input("Ask anything about your health…")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    maybe_show_emergency_notice(user_input)

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        with st.chat_message("assistant"):
            st.error(
                "No API key detected. Set the environment variable "
                "`OPENAI_API_KEY` and try again."
            )
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    if NEW_SDK:
                        client = OpenAI(api_key=api_key)
                        resp = client.chat.completions.create(
                            model="gpt-4o-mini",  
                            messages=st.session_state.messages,
                            temperature=temp,
                            max_tokens=max_tokens,
                        )
                        answer = resp.choices[0].message.content
                    else:
                        import openai
                        openai.api_key = api_key
                        resp = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=st.session_state.messages,
                            temperature=temp,
                            max_tokens=max_tokens,
                        )
                        answer = resp.choices[0].message["content"]

                    final_answer = append_footer(answer)
                    st.markdown(final_answer)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": final_answer}
                    )
                except Exception as e:
                    st.error(f"API error: {e}")

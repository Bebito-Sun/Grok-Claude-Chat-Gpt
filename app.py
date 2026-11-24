import streamlit as st
from openai import OpenAI
from anthropic import Anthropic

# ============================================================
# Load API keys from Streamlit Secrets (safe way)
# ============================================================

chatgpt = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
claude = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
grok = OpenAI(
    api_key=st.secrets["XAI_API_KEY"],
    base_url="https://api.x.ai/v1"
)

# ============================================================
# Agents
# ============================================================

AGENTI = [
    {
        "name": "ChatGPT",
        "role": "You are ChatGPT. You analyze problems in a clear, structured and complete way.",
        "provider": "openai",
        "client": chatgpt,
        "model": "gpt-4o"
    },
    {
        "name": "Claude",
        "role": "You are Claude. You are careful, thoughtful and good at finding risks and nuances. You prefer safe and well-reasoned solutions.",
        "provider": "anthropic",
        "client": claude,
        "model": "claude-3-5-sonnet-20241022"
    },
    {
        "name": "Grok",
        "role": "You are Grok, created by xAI. You are direct, a bit sarcastic when needed, and you prefer practical, fast and slightly unconventional solutions.",
        "provider": "openai",
        "client": grok,
        "model": "grok-2"
    }
]

def call_agent(agent, history, problem):
    system_prompt = f"{agent['role']}\nAlways reply in English, clear and concise (max 130 words)."

    if agent["provider"] == "openai":
        response = agent["client"].chat.completions.create(
            model=agent["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Problem:\n{problem}\n\nConversation so far:\n{history}\n\nYour turn. Give your contribution."}
            ],
            temperature=0.7,
            max_tokens=350
        )
        return response.choices[0].message.content.strip()

    elif agent["provider"] == "anthropic":
        response = agent["client"].messages.create(
            model=agent["model"],
            max_tokens=350,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Problem:\n{problem}\n\nConversation so far:\n{history}\n\nYour turn. Give your contribution."}
            ]
        )
        return response.content[0].text.strip()

# ============================================================
# Interface
# ============================================================

st.set_page_config(page_title="3 AI Council", page_icon="🧠", layout="centered")

st.title("3 AI Council")
st.caption("ChatGPT + Claude + Grok discuss together to solve a problem")

problem = st.text_area("Describe the problem you want to solve:", height=130)

if st.button("Let the 3 AIs discuss", type="primary", use_container_width=True):
    if not problem.strip():
        st.warning("Please write a problem first.")
    else:
        history = ""
        with st.spinner("The 3 AIs are discussing..."):
            for round_num in range(1, 4):
                st.subheader(f"Round {round_num}")
                for agent in AGENTI:
                    with st.chat_message(agent["name"]):
                        contribution = call_agent(agent, history, problem)
                        st.markdown(f"**{agent['name']}**")
                        st.write(contribution)
                        history += f"\n{agent['name']}: {contribution}\n"

            st.divider()
            st.subheader("Final Solution")

            final = call_agent(
                {
                    "name": "Grok",
                    "role": "You are the moderator. Summarize in 5-7 clear, practical and immediately actionable points the best solution that emerged from the discussion.",
                    "provider": "openai",
                    "client": grok,
                    "model": "grok-2"
                },
                history,
                problem
            )
            st.success(final)

from openai import OpenAI
import streamlit as st

st.title("ChatGPT-like clone")

st.markdown(
    """
    <style>
    .user-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        width: fit-content;
        max-width: 80%;
        align-self: flex-end;
    }
    .assistant-message {
        background-color: #f1f3f4;
        color: #333;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        width: fit-content;
        max-width: 80%;
        align-self: flex-start;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Textinhalt als Systemnachricht (wird im Chat selbst nicht angezeigt)
with open("kontext_cf.txt", "r", encoding="utf-8") as file:
    text_inhalt = file.read()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    # Füge `text_inhalt` nur als systeminterne Nachricht hinzu
    st.session_state.messages = [{"role": "system", "content": text_inhalt}]

# Anzeigen der Nachrichten, ohne die Systemnachricht `text_inhalt`
for message in st.session_state.messages:
    if message["role"] != "system":  # Systemnachricht wird nicht angezeigt
        css_class = "user-message" if message["role"] == "user" else "assistant-message"
        with st.chat_message(message["role"]):
            st.markdown(f"<div class='{css_class}'>{message['content']}</div>", unsafe_allow_html=True)

# Benutzer-Eingabe und Antwort-Verarbeitung
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"<div class='user-message'>{prompt}</div>", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        # Übergibt die Systemnachricht intern, ohne sie anzuzeigen
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)

    # Antwort zur Sitzung hinzufügen
    st.session_state.messages.append({"role": "assistant", "content": response})

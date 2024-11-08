from openai import OpenAI
import streamlit as st

# CSS laden
def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

load_css()

# Textinhalt als Systemnachricht (wird im Chat selbst nicht angezeigt)
with open("kontext_cf.txt", "r", encoding="utf-8") as file:
    text_inhalt = file.read()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    # Füge text_inhalt nur als systeminterne Nachricht hinzu
    st.session_state.messages = [{"role": "system", "content": text_inhalt}]

# Avatar-Bildpfade definieren
assistant_avatar = "cf_logo.png"

# Anzeigen der Nachrichten, ohne die Systemnachricht text_inhalt
for message in st.session_state.messages:
    if message["role"] != "system":  # Systemnachricht wird nicht angezeigt
        css_class = "user-message" if message["role"] == "user" else "assistant-message"
        avatar = assistant_avatar if message["role"] == "assistant" else None  # Avatar nur für den Bot
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(
                f"<div class='{css_class}'>{message['content']}</div>",
                unsafe_allow_html=True
            )

# Benutzer-Eingabe und Antwort-Verarbeitung
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(
            f"<div class='user-message'>{prompt}</div>",
            unsafe_allow_html=True
        )

    with st.chat_message("assistant", avatar=assistant_avatar):
        # Platzhalter für die Nachricht erstellen
        message_placeholder = st.empty()
        full_response = ""
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        for chunk in stream:
            # Versuche, den Inhalt zu erhalten, oder setze ihn auf einen leeren String
            content = getattr(chunk.choices[0].delta, 'content', None)
            if content:
                full_response += content
                # Aktualisiere den Platzhalter mit dem gestreamten Inhalt und wende die CSS-Klasse an
                message_placeholder.markdown(
                    f"<div class='assistant-message'>{full_response}</div>",
                    unsafe_allow_html=True
                )
        response = full_response  # Speichere die vollständige Antwort

    # Antwort zur Sitzung hinzufügen
    st.session_state.messages.append({"role": "assistant", "content": response})

from openai import OpenAI
import streamlit as st

# Font Awesome CSS einbinden
# st.markdown(
#     """
#     <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
#     <link href="https://fonts.googleapis.com/css2?family=Noto+Sans&family=Noto+Sans+SC&family=Noto+Sans+Arabic&family=Source+Sans+Pro:wght@400&display=swap" rel="stylesheet">

#     """,
#     unsafe_allow_html=True
# )

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

# Stelle sicher, dass die Systemnachricht immer an das Modell übergeben wird
system_message = {"role": "system", "content": text_inhalt}


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    # Füge text_inhalt nur als systeminterne Nachricht hinzu
    st.session_state.messages = [{"role": "system", "content": text_inhalt}]

    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            # Englischer Text
            "Welcome, I am the chatbot of the Chernoff Faces. I'm here to help.<br><br>"
            # Französischer Text
            "Bienvenue, je suis le chatbot des visages de Chernoff. Je suis là pour vous aider.<br><br>"
            # Vereinfachtes Chinesisch
            "欢迎，我是切尔诺夫面孔的聊天机器人。我是来帮忙的。"
        )
    })

# Avatar-Bildpfad definieren
assistant_avatar = "chernoff_chat.png"

# Anzeigen der Nachrichten, ohne die Systemnachricht text_inhalt
for message in st.session_state.messages:
    if message["role"] != "system":  # Systemnachricht wird nicht angezeigt
        # Überprüfe die Rolle und setze das Avatar entsprechend
        if message["role"] == "assistant":
            with st.chat_message(message["role"], avatar=assistant_avatar):
                # Füge eine Klasse zum Nachrichteninhalt hinzu
                st.markdown(
                    f"<div class='assistant-message'>{message['content']}</div>",
                    unsafe_allow_html=True
                )
        else:
            with st.chat_message(message["role"], avatar=None):  # Kein Avatar für den Nutzer
                st.write(
                    f"<div class='user-message'>{message['content']}</div>",
                    unsafe_allow_html=True
                )

# Benutzer-Eingabe und Antwort-Verarbeitung
if prompt := st.chat_input("Message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=None):  # Kein Avatar für den Nutzer
        st.write(
            f"<div class='user-message'>{prompt}</div>",
            unsafe_allow_html=True
        )

    with st.chat_message("assistant", avatar=assistant_avatar):
        # Platzhalter für die Nachricht erstellen
        message_placeholder = st.empty()
        full_response = ""
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
            temperature=0.0,
            top_p=0.3
        )
        for chunk in stream:
            content = getattr(chunk.choices[0].delta, 'content', None)
            if content:
                full_response += content
                # Aktualisiere den Platzhalter mit dem gestreamten Inhalt
                message_placeholder.markdown(
                    f"<div class='assistant-message'>{full_response}</div>",
                    unsafe_allow_html=True
                )
        response = full_response  # Speichere die vollständige Antwort

    # Antwort zur Sitzung hinzufügen
    st.session_state.messages.append({"role": "assistant", "content": response})

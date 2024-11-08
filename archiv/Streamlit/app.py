import streamlit as st
import openai

# API-Schlüssel und Kontext laden
with open("Streamlit/api_key.txt", "r") as key_file:
    OPENAI_API_KEY = key_file.read().strip()

with open("Streamlit/kontext_cf.txt", "r", encoding="utf-8") as file:
    text_inhalt = file.read()

# OpenAI-API-Schlüssel setzen
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Chatverlauf und Eingabewert im Session State speichern
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

# Funktion, um eine Antwort vom Chatbot zu erhalten
def get_response(user_input):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": text_inhalt},
            {"role": "user", "content": user_input}
        ],
        temperature=0  # Schnellere und deterministische Antwort
    )
    return response.choices[0].message.content

# Streamlit App Layout
st.title("Chatbot Interface")

# Anzeige des Chatverlaufs
st.write("### Chatverlauf")
for role, message in st.session_state["chat_history"]:
    if role == "user":
        st.markdown(f"<div style='text-align: right; background-color: #DCF8C6; padding: 8px; margin: 5px; border-radius: 10px;'>{message}</div>", unsafe_allow_html=True)
    elif role == "assistant":
        st.markdown(f"<div style='text-align: left; background-color: #ECECEC; padding: 8px; margin: 5px; border-radius: 10px;'>{message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color: red; padding: 8px; margin: 5px; border-radius: 10px;'>{message}</div>", unsafe_allow_html=True)

# Eingabefeld für Benutzereingabe
user_input = st.text_input("Geben Sie Ihre Frage ein:", value=st.session_state["user_input"], placeholder="z.B.: Was ist die Hauptstadt von Deutschland?")

# Wenn eine Frage gestellt wird, wird die Antwort angezeigt
if st.button("Frage stellen") and user_input:
    try:
        # Antwort des Chatbots abrufen
        answer = get_response(user_input)
        # Chatverlauf aktualisieren
        st.session_state["chat_history"].append(("user", user_input))
        st.session_state["chat_history"].append(("assistant", answer))
        # Eingabefeld nach dem Senden der Nachricht leeren
        st.session_state["user_input"] = ""  # Eingabefeld zurücksetzen
    except Exception as e:
        # Fehlerbehandlung
        st.session_state["chat_history"].append(("error", f"Ein Fehler ist aufgetreten: {e}"))

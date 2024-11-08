import shiny
from shiny import App, render, ui, reactive, Inputs, Outputs
import openai
from pathlib import Path

# OpenAI-API-Schlüssel setzen
with open("app/api_key.txt", "r") as key_file:
    OPENAI_API_KEY = key_file.read().strip()

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Lies den Inhalt der Kontextdatei ein, wenn die App startet
with open("app/kontext_cf.txt", "r", encoding="utf-8") as file:
    text_inhalt = file.read()

# Dynamischer Pfad zur CSS-Datei
css_path = Path(__file__).parent / "styles.css"

# UI-Definition der Shiny App
app_ui = ui.page_fluid(
    ui.include_css(css_path),  # CSS-Datei mit dynamischem Pfad einbinden
    ui.div(
        ui.div(
            # Hauptcontainer für die gesamte App
            ui.div(
                # Chatverlauf-Anzeige
                ui.div(
                    ui.output_ui("chat_display"),
                    class_="chat-display"
                ),
                # Eingabefeld und Button in einer Zeile im Container
                ui.div(
                    ui.input_text("question", None, placeholder="Ask please..."),
                    ui.input_action_button("ask_button", None, class_="ask-button"),
                    class_="input-container"
                ),
                class_="content-container"
            ),
            class_="app-container"
        )
    )
)

# Server-Logik der Shiny App
def server(input: Inputs, output: Outputs, session):
    # Liste zum Speichern des Chatverlaufs
    chat_history = reactive.Value([])

    @output
    @render.ui
    @reactive.event(input.ask_button)
    def chat_display():
        question = input.question().strip()

        if question:
            try:
                # Anfrage an die OpenAI API mit dem Kontext
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": text_inhalt},
                        {"role": "user", "content": question}
                    ]
                )
                answer_text = response.choices[0].message.content

                # Füge Frage und Antwort zum Chatverlauf hinzu
                chat_history.set(chat_history.get() + [("user", question), ("assistant", answer_text)])

            except Exception as e:
                chat_history.set(chat_history.get() + [("error", f"Ein Fehler ist aufgetreten: {e}")])

        # HTML für den Chatverlauf erstellen
        chat_html = []
        for role, message in chat_history.get():
            if role == "user":
                chat_html.append(f'<div class="user-message">{message}</div>')
            elif role == "assistant":
                chat_html.append(f'<div class="assistant-message">{message}</div>')
            else:  # Fehlernachricht
                chat_html.append(f'<div class="error-message">{message}</div>')

        # Lösche den Inhalt des Eingabefelds nach dem Senden der Nachricht
        ui.update_text("question", value="")

        return ui.HTML("".join(chat_html))

# Erstellen der Shiny App
app = App(app_ui, server)

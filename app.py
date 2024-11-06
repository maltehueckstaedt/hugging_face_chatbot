import shiny
from shiny import App, render, ui, reactive, Inputs, Outputs
import openai

# OpenAI-API-Schlüssel setzen
with open("api_key.txt", "r") as key_file:
    OPENAI_API_KEY = key_file.read().strip()
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Lies den Inhalt der Kontextdatei ein, wenn die App startet
with open("kontext_cf.txt", "r", encoding="utf-8") as file:
    text_inhalt = file.read()


# UI-Definition der Shiny App
app_ui = ui.page_fluid(
    # Chatverlauf-Anzeige
    ui.div(
        ui.output_ui("chat_display"),
        style="height: 80vh; overflow-y: auto; padding-bottom: 60px;"  # Platz für das Eingabefeld unten
    ),
    
    # Eingabefeld und Button am unteren Rand fixieren
    ui.div(
        ui.div(
            ui.input_text("question", "Geben Sie Ihre Frage ein:", placeholder="z.B.: Was ist die Hauptstadt von Deutschland?"),
            style="width: 100%; margin-bottom: 5px;"
        ),
        ui.div(
            ui.input_action_button("ask_button", "Frage stellen"),
            style="width: 100%;"
        ),
        style="position: fixed; bottom: 0; width: 100%; background-color: white; padding: 10px; box-shadow: 0px -1px 5px rgba(0,0,0,0.1);"
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
                chat_html.append(f'<div style="display: inline-block; max-width: 70%; float: right; background-color: #DCF8C6; padding: 8px; margin: 5px; border-radius: 10px; clear: both;">{message}</div>')
            elif role == "assistant":
                chat_html.append(f'<div style="display: inline-block; max-width: 70%; float: left; background-color: #ECECEC; padding: 8px; margin: 5px; border-radius: 10px; clear: both;">{message}</div>')
            else:  # Fehlernachricht
                chat_html.append(f'<div style="display: block; color: red; padding: 8px; margin: 5px; border-radius: 10px; clear: both;">{message}</div>')

        return ui.HTML("".join(chat_html))

# Erstellen der Shiny App
app = App(app_ui, server)

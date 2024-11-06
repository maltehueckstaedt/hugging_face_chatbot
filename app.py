import shiny
from shiny import App, render, ui, reactive, Inputs, Outputs
import openai

# OpenAI-API-Schlüssel setzen
# Lies den API-Schlüssel aus der Textdatei ein
with open("api_key.txt", "r") as key_file:
    OPENAI_API_KEY = key_file.read().strip()
client = openai.OpenAI(api_key=OPENAI_API_KEY)


# Lies den Inhalt der Kontextdatei ein, wenn die App startet
with open("kontext_cf.txt", "r") as file:
    text_inhalt = file.read()

# Lies den Inhalt der Kontextdatei ein, wenn die App startet
with open("kontext_cf.txt", "r") as file:
    text_inhalt = file.read()

# UI-Definition der Shiny App
app_ui = ui.page_fluid(
    ui.h2("Fragen Sie OpenAI!"),
    ui.input_text("question", "Geben Sie Ihre Frage ein:", placeholder="z.B.: Was ist die Hauptstadt von Deutschland?"),
    ui.input_action_button("ask_button", "Frage stellen"),
    ui.output_text_verbatim("answer")  # Output definiert
)

# Server-Logik der Shiny App
def server(input: Inputs, output: Outputs, session):

    @output  # Dekoriert das Output-Element
    @render.text  # Definiert den Render-Typ
    @reactive.event(input.ask_button)  # Wird nur aktiviert, wenn der Button "Frage stellen" geklickt wird
    def answer():
        question = input.question()

        if question:
            try:
                # Anfrage an die OpenAI API mit der Hintergrunddatei als Kontext
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": text_inhalt},
                        {"role": "user", "content": question}
                    ]
                )

                # Extrahiere die Antwort und gebe sie zurück
                answer_text = response.choices[0].message.content
                return answer_text

            except Exception as e:
                return f"Ein Fehler ist aufgetreten: {e}"
        else:
            return "Bitte geben Sie eine Frage ein."
            
# Erstellen der Shiny App
app = App(app_ui, server)
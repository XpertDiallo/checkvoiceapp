import streamlit as st
import speech_recognition as sr
from googletrans import Translator
import os

def transcribe_speech(api_choice, speech_language, translation_language, duration=60):
    """
    Fonction pour transcrire l'audio et traduire la transcription.
    Limite l'enregistrement à 60 secondes.
    """
    r = sr.Recognizer()

    # Chemins pour PocketSphinx
    sphinx_config = {
        "language_model": f"C:\\pocketsphinx\\{speech_language}\\language-model\\{speech_language}.lm.bin",
        "acoustic_model": f"C:\\pocketsphinx\\{speech_language}\\acoustic-model",
        "dictionary": f"C:\\pocketsphinx\\{speech_language}\\language-model\\{speech_language}.dic",
    }

    with sr.Microphone() as source:
        st.info("Parlez maintenant... (60 secondes maximum)")
        try:
            audio_text = r.listen(source, timeout=1, phrase_time_limit=duration)
            st.info("Transcription en cours...")
            if api_choice == "Google":
                text = r.recognize_google(audio_text, language=speech_language)
            elif api_choice == "Sphinx":
                text = r.recognize_sphinx(
                    audio_text,
                    language_model=sphinx_config["language_model"],
                    acoustic_model=sphinx_config["acoustic_model"],
                    dictionary=sphinx_config["dictionary"]
                )
            else:
                return "API non supportée.", None

            # Traduction
            if translation_language != "Aucune traduction":
                translator = Translator()
                translated_text = translator.translate(text, dest=translation_language).text
                return text, translated_text

            return text, None
        except sr.UnknownValueError:
            return "Désolé, je n'ai pas compris.", None
        except sr.RequestError as e:
            return f"Erreur du service de reconnaissance vocale : {e}", None
        except Exception as e:
            return f"Erreur : {str(e)}", None

def save_transcription(text, filename="transcription.txt"):
    """
    Fonction pour sauvegarder le texte transcrit dans un fichier.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename

def open_file(filepath):
    """
    Fonction pour ouvrir le fichier dans le système d'exploitation par défaut.
    """
    try:
        os.startfile(filepath)
    except Exception as e:
        st.error(f"Impossible d'ouvrir le fichier : {e}")

def main():
    st.title("Application de Reconnaissance et Traduction Vocale")
    st.write("Cliquez sur Commencer Enregistrement puis commencer à parler.")

    # Choisir l'API de reconnaissance vocale
    api_choice = st.selectbox(
        "Choisissez l'API de reconnaissance vocale :",
        options=["Google", "Sphinx"],
        index=0  # Par défaut, Google
    )

    # Choisir la langue parlée
    speech_language = st.selectbox(
        "Choisissez la langue dans laquelle vous allez parler :",
        options=["fr-FR", "en-US", "es-ES", "de-DE", "it-IT", "ar-SA"],
        index=0
    )

    # Choisir la langue de traduction
    translation_language = st.selectbox(
        "Choisissez une langue pour traduire la transcription :",
        options=["Aucune traduction", "en", "es", "de", "it", "ar"],
        index=1
    )

    # Gestion des états de pause et reprise
    if "paused" not in st.session_state:
        st.session_state.paused = False

    if "text" not in st.session_state:
        st.session_state.text = ""
        st.session_state.translated_text = ""

    # Bouton pour commencer l'enregistrement
    if st.button("Commencer l'enregistrement") and not st.session_state.paused:
        text, translated_text = transcribe_speech(api_choice, speech_language, translation_language)
        st.session_state.text = text
        st.session_state.translated_text = translated_text
        st.write("Transcription :", st.session_state.text)
        if st.session_state.translated_text:
            st.write(f"Traduction en {translation_language} :", st.session_state.translated_text)

    # Boutons Pause/Reprendre sous "Commencer l'enregistrement"
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Pause"):
            st.session_state.paused = True
            st.warning("Reconnaissance vocale mise en pause.")
    with col2:
        if st.button("Reprendre"):
            st.session_state.paused = False
            st.success("Reconnaissance vocale reprise.")

    # Ajouter un bouton pour sauvegarder la transcription
    if st.button("Sauvegarder la transcription"):
        if st.session_state.text:
            filename = save_transcription(st.session_state.text)
            st.success(f"Transcription sauvegardée dans le fichier : {filename}")
            open_file(filename)  # Ouvrir le fichier automatiquement
        else:
            st.error("Aucun texte à sauvegarder.")

    # Boutons supplémentaires
    col3, col4 = st.columns(2)

    with col3:
        if st.button("Enregistrer à nouveau"):
            # Réinitialiser l'état et redémarrer l'application
            st.session_state.clear()
            

    with col4:
        if st.button("Quitter"):
            st.write("Merci d'avoir utilisé l'application !")
            st.stop()

if __name__ == "__main__":
    main()

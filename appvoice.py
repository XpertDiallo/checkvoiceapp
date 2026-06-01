import io
import math
import mimetypes
import os
import re
import tempfile
from datetime import datetime

import speech_recognition as sr
import streamlit as st
from deep_translator import GoogleTranslator
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from pydub.silence import split_on_silence
from pydub.utils import make_chunks


SPEECH_LANGUAGES = [
    {"label": "Français (France)", "speech_code": "fr-FR", "translate_code": "fr"},
    {"label": "Anglais (États-Unis)", "speech_code": "en-US", "translate_code": "en"},
    {"label": "Anglais (Royaume-Uni)", "speech_code": "en-GB", "translate_code": "en"},
    {"label": "Espagnol", "speech_code": "es-ES", "translate_code": "es"},
    {"label": "Allemand", "speech_code": "de-DE", "translate_code": "de"},
    {"label": "Italien", "speech_code": "it-IT", "translate_code": "it"},
    {"label": "Portugais (Brésil)", "speech_code": "pt-BR", "translate_code": "pt"},
    {"label": "Portugais (Portugal)", "speech_code": "pt-PT", "translate_code": "pt"},
    {"label": "Arabe", "speech_code": "ar-SA", "translate_code": "ar"},
    {"label": "Néerlandais", "speech_code": "nl-NL", "translate_code": "nl"},
    {"label": "Turc", "speech_code": "tr-TR", "translate_code": "tr"},
    {"label": "Chinois simplifié", "speech_code": "zh-CN", "translate_code": "zh-CN"},
    {"label": "Japonais", "speech_code": "ja-JP", "translate_code": "ja"},
]

TRANSLATION_LANGUAGES = [
    {"label": "Aucune traduction", "code": None},
    {"label": "Français", "code": "fr"},
    {"label": "Anglais", "code": "en"},
    {"label": "Espagnol", "code": "es"},
    {"label": "Allemand", "code": "de"},
    {"label": "Italien", "code": "it"},
    {"label": "Portugais", "code": "pt"},
    {"label": "Arabe", "code": "ar"},
    {"label": "Néerlandais", "code": "nl"},
    {"label": "Turc", "code": "tr"},
    {"label": "Chinois simplifié", "code": "zh-CN"},
    {"label": "Japonais", "code": "ja"},
]

MIME_FORMATS = {
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/wave": "wav",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/mp4": "mp4",
    "audio/x-m4a": "m4a",
    "audio/aac": "aac",
    "audio/ogg": "ogg",
    "audio/webm": "webm",
    "audio/flac": "flac",
    "audio/aiff": "aiff",
    "audio/x-aiff": "aiff",
}

PYDUB_FORMAT_ALIASES = {
    "aif": "aiff",
    "aifc": "aiff",
    "m4a": "mp4",
    "m4b": "mp4",
    "oga": "ogg",
}

PLAYER_MIME_BY_FORMAT = {
    "aac": "audio/aac",
    "aiff": "audio/aiff",
    "flac": "audio/flac",
    "m4a": "audio/mp4",
    "mp3": "audio/mpeg",
    "mp4": "audio/mp4",
    "ogg": "audio/ogg",
    "wav": "audio/wav",
    "webm": "audio/webm",
}


def configure_page():
    st.set_page_config(
        page_title="CheckVoice - Transcription vocale",
        page_icon="🎙️",
        layout="wide",
    )
    st.markdown(
        """
        <style>
            :root {
                --cv-primary: #0f766e;
                --cv-secondary: #f97316;
                --cv-accent: #0284c7;
                --cv-soft: #ecfeff;
                --cv-card: rgba(255, 255, 255, 0.92);
                --cv-border: rgba(15, 118, 110, 0.18);
                --cv-text: #0f172a;
                --cv-muted: #475569;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(20, 184, 166, 0.20), transparent 30rem),
                    radial-gradient(circle at top right, rgba(249, 115, 22, 0.16), transparent 28rem),
                    linear-gradient(135deg, #f8fafc 0%, #ecfeff 48%, #fff7ed 100%);
                color: var(--cv-text);
            }

            [data-testid="stHeader"] {
                background: rgba(255, 255, 255, 0);
            }

            .main .block-container {
                max-width: 1180px;
                padding-top: 1.8rem;
                padding-bottom: 3rem;
            }

            .cv-hero {
                border: 1px solid var(--cv-border);
                border-radius: 8px;
                background: var(--cv-card);
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
                padding: 1.4rem 1.5rem;
                margin-bottom: 1rem;
            }

            .cv-hero h1 {
                color: var(--cv-text);
                font-size: 2.1rem;
                line-height: 1.15;
                margin: 0 0 0.35rem 0;
            }

            .cv-hero p {
                color: var(--cv-muted);
                font-size: 1rem;
                margin: 0;
                max-width: 760px;
            }

            .cv-strip {
                display: flex;
                flex-wrap: wrap;
                gap: 0.55rem;
                margin-top: 1rem;
            }

            .cv-pill {
                border-radius: 999px;
                background: #ffffff;
                border: 1px solid rgba(2, 132, 199, 0.18);
                color: #075985;
                font-size: 0.82rem;
                font-weight: 700;
                padding: 0.38rem 0.7rem;
            }

            .cv-panel {
                border: 1px solid var(--cv-border);
                border-radius: 8px;
                background: var(--cv-card);
                box-shadow: 0 14px 34px rgba(15, 23, 42, 0.07);
                padding: 1.15rem;
                margin: 0.65rem 0 1rem 0;
            }

            .cv-panel h3 {
                color: var(--cv-text);
                margin: 0 0 0.4rem 0;
            }

            .cv-panel p {
                color: var(--cv-muted);
                margin: 0.2rem 0 0.8rem 0;
            }

            div.stButton > button {
                border-radius: 8px;
                border: 1px solid rgba(15, 118, 110, 0.18);
                font-weight: 800;
                min-height: 2.75rem;
                transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
            }

            div.stButton > button:hover {
                border-color: rgba(15, 118, 110, 0.55);
                box-shadow: 0 10px 24px rgba(15, 118, 110, 0.12);
                transform: translateY(-1px);
            }

            div.stButton > button[kind="primary"] {
                background: linear-gradient(135deg, var(--cv-primary), var(--cv-accent));
                border-color: transparent;
                color: white;
            }

            [data-testid="stSidebar"] {
                background: rgba(255, 255, 255, 0.86);
                border-right: 1px solid rgba(15, 118, 110, 0.12);
            }

            [data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.72);
                border: 1px solid rgba(2, 132, 199, 0.14);
                border-radius: 8px;
                padding: 0.8rem;
            }

            textarea {
                border-radius: 8px !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_language_by_label(label, languages):
    return next(language for language in languages if language["label"] == label)


def detect_audio_format(filename=None, mime_type=None, audio_bytes=None):
    if filename:
        extension = os.path.splitext(filename)[1].lower().lstrip(".")
        if extension:
            return extension

    if mime_type and mime_type in MIME_FORMATS:
        return MIME_FORMATS[mime_type]

    guessed_mime, _ = mimetypes.guess_type(filename or "")
    if guessed_mime in MIME_FORMATS:
        return MIME_FORMATS[guessed_mime]

    if audio_bytes:
        header = audio_bytes[:16]
        if header.startswith(b"RIFF") and b"WAVE" in header:
            return "wav"
        if header.startswith(b"ID3") or header[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
            return "mp3"
        if header.startswith(b"fLaC"):
            return "flac"
        if header.startswith(b"OggS"):
            return "ogg"
        if header.startswith(b"\x1a\x45\xdf\xa3"):
            return "webm"
        if len(header) > 8 and header[4:8] == b"ftyp":
            return "mp4"

    return None


def player_mime(mime_type=None, detected_format=None):
    if mime_type and mime_type.startswith("audio/"):
        return mime_type
    return PLAYER_MIME_BY_FORMAT.get(detected_format, "audio/wav")


def pydub_format(detected_format):
    if not detected_format:
        return None
    return PYDUB_FORMAT_ALIASES.get(detected_format.lower(), detected_format.lower())


def load_audio(audio_bytes, filename=None, mime_type=None):
    detected_format = detect_audio_format(filename, mime_type, audio_bytes)
    format_hint = pydub_format(detected_format)

    try:
        return AudioSegment.from_file(io.BytesIO(audio_bytes), format=format_hint), detected_format
    except CouldntDecodeError:
        suffix = f".{detected_format}" if detected_format else ""
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            return AudioSegment.from_file(temp_path, format=format_hint), detected_format
        except CouldntDecodeError as error:
            raise ValueError(
                "Format audio non lisible. Vérifiez que le fichier est valide et que ffmpeg "
                "est disponible dans l'environnement Streamlit."
            ) from error
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)


def normalize_audio(audio):
    return audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)


def split_audio(audio, chunk_length_ms):
    if len(audio) <= chunk_length_ms:
        return [audio]

    if math.isinf(audio.dBFS):
        return list(make_chunks(audio, chunk_length_ms))

    silence_threshold = max(audio.dBFS - 14, -50)
    speech_parts = split_on_silence(
        audio,
        min_silence_len=700,
        silence_thresh=silence_threshold,
        keep_silence=350,
    )

    if len(speech_parts) <= 1:
        return list(make_chunks(audio, chunk_length_ms))

    chunks = []
    current = AudioSegment.silent(duration=0, frame_rate=audio.frame_rate)

    for part in speech_parts:
        if len(part) < 250:
            continue

        if len(part) > chunk_length_ms:
            if len(current) > 0:
                chunks.append(current)
                current = AudioSegment.silent(duration=0, frame_rate=audio.frame_rate)
            chunks.extend(make_chunks(part, chunk_length_ms))
            continue

        if len(current) + len(part) <= chunk_length_ms:
            current += part
        else:
            if len(current) > 0:
                chunks.append(current)
            current = part

    if len(current) > 0:
        chunks.append(current)

    return chunks or list(make_chunks(audio, chunk_length_ms))


def transcribe_chunks(audio, speech_code, chunk_length_seconds):
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True

    normalized_audio = normalize_audio(audio)
    chunks = split_audio(normalized_audio, chunk_length_seconds * 1000)
    transcription_parts = []
    warnings = []

    progress = st.progress(0, text="Préparation de la transcription...")
    for index, chunk in enumerate(chunks, start=1):
        progress.progress(
            (index - 1) / len(chunks),
            text=f"Transcription du segment {index}/{len(chunks)}...",
        )
        audio_data = sr.AudioData(chunk.raw_data, chunk.frame_rate, chunk.sample_width)
        try:
            text = recognizer.recognize_google(audio_data, language=speech_code)
            if text:
                transcription_parts.append(text.strip())
        except sr.UnknownValueError:
            warnings.append(f"Segment {index}: parole non reconnue.")
        except sr.RequestError as error:
            raise RuntimeError(f"Erreur du service de reconnaissance vocale: {error}") from error

    progress.progress(1.0, text="Transcription terminée.")

    transcription = " ".join(transcription_parts).strip()
    if not transcription:
        raise RuntimeError(
            "Aucune parole n'a pu être transcrite. Essayez avec un audio plus clair ou une autre langue source."
        )

    return transcription, warnings, len(chunks)


def split_text_for_translation(text, max_chars=4500):
    words = re.split(r"(\s+)", text)
    chunks = []
    current = ""

    for token in words:
        if len(current) + len(token) > max_chars and current.strip():
            chunks.append(current.strip())
            current = token
        else:
            current += token

    if current.strip():
        chunks.append(current.strip())

    return chunks


def translate_text(text, target_code):
    if not target_code:
        return ""

    translated_parts = []
    translator = GoogleTranslator(source="auto", target=target_code)

    for chunk in split_text_for_translation(text):
        translated_parts.append(translator.translate(chunk))

    return "\n\n".join(translated_parts).strip()


def build_export(result):
    lines = [
        "CheckVoice - transcription vocale",
        f"Date: {result['created_at']}",
        f"Source: {result['source_name']}",
        f"Langue audio: {result['source_language_label']}",
        f"Format détecté: {result['detected_format'] or 'non déterminé'}",
        f"Durée audio: {result['duration_seconds']:.1f} secondes",
        "",
        "Transcription:",
        result["transcription"],
    ]

    if result.get("translation"):
        lines.extend(["", f"Traduction ({result['target_language_label']}):", result["translation"]])

    return "\n".join(lines)


def process_audio(
    audio_bytes,
    source_name,
    source_language,
    target_language,
    chunk_length_seconds,
    mime_type=None,
):
    audio, detected_format = load_audio(audio_bytes, source_name, mime_type)
    transcription, warnings, chunk_count = transcribe_chunks(
        audio,
        source_language["speech_code"],
        chunk_length_seconds,
    )

    translation = ""
    if target_language["code"]:
        with st.spinner(f"Traduction vers {target_language['label']}..."):
            translation = translate_text(transcription, target_language["code"])

    return {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_name": source_name,
        "source_language_label": source_language["label"],
        "target_language_label": target_language["label"],
        "detected_format": detected_format,
        "duration_seconds": len(audio) / 1000,
        "chunk_count": chunk_count,
        "transcription": transcription,
        "translation": translation,
        "warnings": warnings,
    }


def render_result(result, key_prefix):
    st.success("Transcription terminée.")

    metric_columns = st.columns(3)
    metric_columns[0].metric("Durée", f"{result['duration_seconds']:.1f} s")
    metric_columns[1].metric("Segments", result["chunk_count"])
    metric_columns[2].metric("Format", (result["detected_format"] or "Inconnu").upper())

    if result["warnings"]:
        with st.expander("Segments non reconnus"):
            st.write("\n".join(result["warnings"]))

    col_left, col_right = st.columns(2)
    with col_left:
        st.text_area(
            "Transcription",
            result["transcription"],
            height=280,
            key=f"{key_prefix}_transcription",
        )
    with col_right:
        st.text_area(
            f"Traduction - {result['target_language_label']}",
            result["translation"] or "Aucune traduction demandée.",
            height=280,
            key=f"{key_prefix}_translation",
        )

    st.download_button(
        "Télécharger le résultat",
        data=build_export(result),
        file_name=f"checkvoice_{key_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        type="primary",
        use_container_width=True,
        key=f"{key_prefix}_download",
    )


def render_record_tab(target_language, chunk_length_seconds):
    st.markdown(
        """
        <div class="cv-panel">
            <h3>Enregistrer une voix</h3>
            <p>Choisissez la langue parlée, lancez l'enregistrement, arrêtez-le quand vous avez fini, puis transcrivez.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    source_label = st.selectbox(
        "Langue parlée pendant l'enregistrement",
        [language["label"] for language in SPEECH_LANGUAGES],
        index=0,
        key="record_source_language",
    )
    source_language = get_language_by_label(source_label, SPEECH_LANGUAGES)

    recording = st.audio_input(
        "Enregistrement vocal",
        help="Le micro du navigateur est utilisé: vous pouvez parler longtemps et arrêter quand vous le souhaitez.",
        key="browser_recording",
        sample_rate=16000,
    )

    if recording is not None:
        audio_bytes = recording.getvalue()
        detected_format = detect_audio_format(recording.name, recording.type, audio_bytes)

        st.caption(f"Format détecté: {(detected_format or recording.type or 'inconnu')}")
        st.audio(audio_bytes, format=player_mime(recording.type, detected_format))

        if st.button(
            "Transcrire l'enregistrement",
            type="primary",
            use_container_width=True,
            key="transcribe_recording",
        ):
            try:
                with st.spinner("Analyse de l'enregistrement..."):
                    st.session_state.record_result = process_audio(
                        audio_bytes=audio_bytes,
                        source_name=recording.name or "enregistrement_micro.wav",
                        source_language=source_language,
                        target_language=target_language,
                        chunk_length_seconds=chunk_length_seconds,
                        mime_type=recording.type,
                    )
            except (RuntimeError, ValueError) as error:
                st.error(str(error))

    if st.session_state.get("record_result"):
        render_result(st.session_state.record_result, "recording")


def render_upload_tab(target_language, chunk_length_seconds):
    st.markdown(
        """
        <div class="cv-panel">
            <h3>Importer un fichier audio</h3>
            <p>Chargez un fichier audio: WAV, MP3, M4A, OGG, WEBM, FLAC, AAC ou tout format lisible par ffmpeg.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    source_label = st.selectbox(
        "Langue parlée dans le fichier",
        [language["label"] for language in SPEECH_LANGUAGES],
        index=0,
        key="upload_source_language",
    )
    source_language = get_language_by_label(source_label, SPEECH_LANGUAGES)

    uploaded_file = st.file_uploader(
        "Déposer ou sélectionner un audio",
        type=None,
        accept_multiple_files=False,
        key="uploaded_audio",
    )

    if uploaded_file is not None:
        audio_bytes = uploaded_file.getvalue()
        detected_format = detect_audio_format(uploaded_file.name, uploaded_file.type, audio_bytes)

        st.caption(f"Format détecté: {(detected_format or uploaded_file.type or 'inconnu')}")
        st.audio(audio_bytes, format=player_mime(uploaded_file.type, detected_format))

        if st.button(
            "Transcrire le fichier audio",
            type="primary",
            use_container_width=True,
            key="transcribe_upload",
        ):
            try:
                with st.spinner("Conversion et analyse du fichier..."):
                    st.session_state.upload_result = process_audio(
                        audio_bytes=audio_bytes,
                        source_name=uploaded_file.name,
                        source_language=source_language,
                        target_language=target_language,
                        chunk_length_seconds=chunk_length_seconds,
                        mime_type=uploaded_file.type,
                    )
            except (RuntimeError, ValueError) as error:
                st.error(str(error))

    if st.session_state.get("upload_result"):
        render_result(st.session_state.upload_result, "upload")


def main():
    configure_page()

    st.markdown(
        """
        <section class="cv-hero">
            <h1>CheckVoice</h1>
            <p>Reconnaissance vocale, transcription longue durée, import audio et traduction dans une interface Streamlit plus claire.</p>
            <div class="cv-strip">
                <span class="cv-pill">Micro navigateur</span>
                <span class="cv-pill">Audio multi-format</span>
                <span class="cv-pill">Traduction au choix</span>
                <span class="cv-pill">Export texte</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Paramètres")
        target_label = st.selectbox(
            "Traduire la transcription vers",
            [language["label"] for language in TRANSLATION_LANGUAGES],
            index=1,
        )
        target_language = get_language_by_label(target_label, TRANSLATION_LANGUAGES)

        chunk_length_seconds = st.slider(
            "Durée max d'un segment audio",
            min_value=20,
            max_value=60,
            value=45,
            step=5,
            help="Les audios longs sont découpés en segments pour améliorer la stabilité de la transcription.",
        )

        st.info("La reconnaissance Google et la traduction nécessitent une connexion internet.")

        if st.button("Réinitialiser les résultats", use_container_width=True):
            st.session_state.pop("record_result", None)
            st.session_state.pop("upload_result", None)
            st.rerun()

    record_tab, upload_tab = st.tabs(["Enregistrer", "Importer un audio"])

    with record_tab:
        render_record_tab(target_language, chunk_length_seconds)

    with upload_tab:
        render_upload_tab(target_language, chunk_length_seconds)


if __name__ == "__main__":
    main()

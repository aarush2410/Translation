import streamlit as st
import tempfile
import os
import io
import pdfkit
from docx import Document
import sounddevice as sd
import threading
import speech_recognition as sr
from googletrans import Translator

# Initialize recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()

# Function to translate text using googletrans
def translate_text_googletrans(text, dest_lang):
    translated_chunks = []
    chunk_size = 1000  # Number of characters per chunk
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        translated_chunk = translator.translate(chunk, dest=dest_lang)
        translated_chunks.append(translated_chunk.text)
    return ''.join(translated_chunks)

# Function to detect language of the input text
def detect_language(text):
    detected_lang = translator.detect(text)
    return detected_lang

# Function to download text as PDF
def download_as_pdf(text):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    pdfkit.from_string(text, temp_file.name)
    with open(temp_file.name, 'rb') as f:
        pdf_bytes = f.read()
    os.unlink(temp_file.name)
    return pdf_bytes

# Function to download text as DOCX
def download_as_docx(text):
    doc = Document()
    doc.add_paragraph(text)
    doc_bytes = io.BytesIO()
    doc.save(doc_bytes)
    doc_bytes.seek(0)
    return doc_bytes

# Function to listen to microphone and translate speech
def listen_microphone(source_lang, target_lang):
    global stop_listening
    with sr.Microphone() as source:
        st.write("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source, duration=5)
        st.write("Listening... (say 'stop' or press Enter to stop)")
        while not stop_listening:
            try:
                audio_data = recognizer.listen(source)
                st.write("Recognizing...")
                text = recognizer.recognize_google(audio_data, language=source_lang)
                st.session_state.recognized_text.append(text)
                st.write(f"You said: {text}")
                translated = translator.translate(text, src=source_lang, dest=target_lang)
                st.session_state.translated_text.append(translated.text)
                st.write(f"Translated to {target_lang}: {translated.text}")
                if "stop" in text.lower():
                    stop_listening = True
                    break
            except sr.UnknownValueError:
                st.write("Sorry, I could not understand the audio")
            except sr.RequestError:
                st.write("Could not request results from Google Web Speech API")
            except Exception as e:
                st.write(f"An error occurred: {e}")

# Main function to run the Streamlit app
def main():
    st.title("Text Translation Tool")

    # Language selection
    languages = {
        'Auto Detect': 'auto',  # Special case for automatic language detection
        'Afrikaans': 'af', 'Albanian': 'sq', 'Amharic': 'am', 'Arabic': 'ar', 'Armenian': 'hy', 'Azerbaijani': 'az',
        'Basque': 'eu', 'Belarusian': 'be', 'Bengali': 'bn', 'Bosnian': 'bs', 'Bulgarian': 'bg', 'Catalan': 'ca',
        'Cebuano': 'ceb', 'Chichewa': 'ny', 'Chinese (Simplified)': 'zh-cn', 'Chinese (Traditional)': 'zh-tw',
        'Corsican': 'co', 'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl', 'English': 'en',
        'Esperanto': 'eo', 'Estonian': 'et', 'Filipino': 'tl', 'Finnish': 'fi', 'French': 'fr', 'Frisian': 'fy',
        'Galician': 'gl', 'Georgian': 'ka', 'German': 'de', 'Greek': 'el', 'Gujarati': 'gu', 'Haitian Creole': 'ht',
        'Hausa': 'ha', 'Hawaiian': 'haw', 'Hebrew': 'he', 'Hindi': 'hi', 'Hmong': 'hmn', 'Hungarian': 'hu',
        'Icelandic': 'is', 'Igbo': 'ig', 'Indonesian': 'id', 'Irish': 'ga', 'Italian': 'it', 'Japanese': 'ja',
        'Javanese': 'jv', 'Kannada': 'kn', 'Kazakh': 'kk', 'Khmer': 'km', 'Korean': 'ko', 'Kurdish (Kurmanji)': 'ku',
        'Kyrgyz': 'ky', 'Lao': 'lo', 'Latin': 'la', 'Latvian': 'lv', 'Lithuanian': 'lt', 'Luxembourgish': 'lb',
        'Macedonian': 'mk', 'Malagasy': 'mg', 'Malay': 'ms', 'Malayalam': 'ml', 'Maltese': 'mt', 'Maori': 'mi',
        'Marathi': 'mr', 'Mongolian': 'mn', 'Myanmar (Burmese)': 'my', 'Nepali': 'ne', 'Norwegian': 'no',
        'Odia (Oriya)': 'or', 'Pashto': 'ps', 'Persian': 'fa', 'Polish': 'pl', 'Portuguese': 'pt', 'Punjabi': 'pa',
        'Romanian': 'ro', 'Russian': 'ru', 'Samoan': 'sm', 'Scots Gaelic': 'gd', 'Serbian': 'sr', 'Sesotho': 'st',
        'Shona': 'sn', 'Sindhi': 'sd', 'Sinhala': 'si', 'Slovak': 'sk', 'Slovenian': 'sl', 'Somali': 'so',
        'Spanish': 'es', 'Sundanese': 'su', 'Swahili': 'sw', 'Swedish': 'sv', 'Tajik': 'tg', 'Tamil': 'ta',
        'Telugu': 'te', 'Thai': 'th', 'Turkish': 'tr', 'Ukrainian': 'uk', 'Urdu': 'ur', 'Uyghur': 'ug',
        'Uzbek': 'uz', 'Vietnamese': 'vi', 'Welsh': 'cy', 'Xhosa': 'xh', 'Yiddish': 'yi', 'Yoruba': 'yo',
        'Zulu': 'zu', 'Sanskrit': 'sa'  # Adding Sanskrit with ISO 639-1 code 'sa'
    }

    st.subheader("Step 1: Enter Text or Use Microphone")
    option = st.radio("Choose input method:", ("Text Input", "Microphone Input"))

    if option == "Text Input":
        input_text = st.text_area("Enter text to translate:", height=200)

        if input_text:
            st.subheader("Step 2: Detect Language")
            detected_lang = detect_language(input_text)
            detected_lang_name = next(key for key, value in languages.items() if value == detected_lang.lang)
            st.write(f"Detected Input Language: {detected_lang_name}")

            st.subheader("Step 3: Choose Translation Options")
            multiple_languages = st.checkbox("Translate to multiple languages?")

            if multiple_languages:
                num_languages = st.number_input("How many languages do you want to translate to?", min_value=1, max_value=3, value=1, step=1)
                selected_languages = []
                for i in range(num_languages):
                    lang = st.selectbox(f"Select language {i + 1}", list(languages.keys()), key=f"lang_{i}")
                    selected_languages.append(languages[lang])
            else:
                target_language = st.selectbox("Select target language", list(languages.keys()))
                selected_languages = [languages[target_language]]

            if st.button("Translate"):
                translations = {}
                for lang in selected_languages:
                    translations[lang] = translate_text_googletrans(input_text, lang)

                st.subheader("Translated Texts")
                cols = st.columns(len(translations))
                for idx, (lang, translation) in enumerate(translations.items()):
                    lang_name = next(key for key, value in languages.items() if value == lang)
                    cols[idx].write(f"**{lang_name}:**")
                    cols[idx].text_area("", translation, height=200)

                if st.button("Copy Translated Text"):
                    st.text("\n\n".join(translations.values()))

                if st.button("Download as PDF"):
                    pdf_text = "\n\n".join([f"{next(key for key, value in languages.items() if value == lang)}:\n{translation}" for lang, translation in translations.items()])
                    pdf_bytes = download_as_pdf(pdf_text)
                    st.download_button(label="Download PDF", data=pdf_bytes, file_name="translated_text.pdf", mime="application/pdf")

                if st.button("Download as DOCX"):
                    docx_text = "\n\n".join([f"{next(key for key, value in languages.items() if value == lang)}:\n{translation}" for lang, translation in translations.items()])
                    docx_bytes = download_as_docx(docx_text)
                    st.download_button(label="Download DOCX", data=docx_bytes, file_name="translated_text.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    elif option == "Microphone Input":
        st.session_state.setdefault("recognized_text", [])
        st.session_state.setdefault("translated_text", [])

        source_language = st.selectbox("Select source language", list(languages.keys()), index=list(languages.values()).index("en"))
        target_language = st.selectbox("Select target language", list(languages.keys()), index=list(languages.values()).index("es"))

        if st.button("Start Listening"):
            stop_listening = False
            listen_thread = threading.Thread(target=listen_microphone, args=(languages[source_language], languages[target_language]))
            listen_thread.start()

        if st.button("Stop Listening"):
            stop_listening = True
            listen_thread.join()

        st.subheader("Recognized Texts")
        for text in st.session_state.recognized_text:
            st.write(text)

        st.subheader("Translated Texts")
        for text in st.session_state.translated_text:
            st.write(text)

if __name__ == "__main__":
    main()

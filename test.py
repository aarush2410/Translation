import streamlit as st
from googletrans import Translator
from docx import Document
import tempfile
import os

# Function to translate text using googletrans
def translate_text_googletrans(text, dest_lang):
    translator = Translator()
    translated_chunks = []
    chunk_size = 1000  # Number of characters per chunk
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        translated_chunk = translator.translate(chunk, dest=dest_lang)
        translated_chunks.append(translated_chunk.text)
    return ''.join(translated_chunks)

# Function to download text as PDF
def download_as_pdf(text):
    import pdfkit
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

# Main function to run the Streamlit app
def main():
    st.title("Text Translation Tool")

    # Language selection
    languages = {
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

    target_language = st.selectbox("Select target language", list(languages.keys()))

    # Text input for translation
    input_text = st.text_area("Enter text to translate:", height=200)
    translate_button = st.button("Translate")
    
    if translate_button:
        if input_text:
            translated_text = translate_text_googletrans(input_text, languages[target_language])
            st.subheader("Translated Text:")
            st.write(translated_text)

            # Copy text to clipboard
            if st.button("Copy Translated Text"):
                st.text(translated_text)

            # Download as PDF
            if st.button("Download as PDF"):
                pdf_bytes = download_as_pdf(translated_text)
                st.download_button(label="Download PDF", data=pdf_bytes, file_name="translated_text.pdf", mime="application/pdf")

            # Download as DOCX
            if st.button("Download as DOCX"):
                docx_bytes = download_as_docx(translated_text)
                st.download_button(label="Download DOCX", data=docx_bytes, file_name="translated_text.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        else:
            st.warning("Please enter text to translate.")

if __name__ == "__main__":
    main()

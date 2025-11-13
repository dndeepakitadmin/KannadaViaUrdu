import streamlit as st
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from aksharamukha.transliterate import process as aksharamukha_process
from gtts import gTTS
from io import BytesIO
import pandas as pd

# ------------------ PAGE CONFIG ------------------ #
st.set_page_config(
    page_title="Urdu → Kannada Learning",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ------------------ HIDE STREAMLIT UI ------------------ #
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ------------------ AUDIO GENERATOR ------------------ #
def make_audio(text, lang="kn"):
    fp = BytesIO()
    tts = gTTS(text=text, lang=lang)
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

# ------------------ PAGE TITLE ------------------ #
st.title("📝 Learn Kannada using Urdu Script")
st.subheader("اردو رسم الخط کی مدد سے کَنّڑ سیکھیں")

text = st.text_area("Enter Urdu text here (اردو):", height=120)

if st.button("Translate"):
    if text.strip():
        try:
            # ---------------- FULL SENTENCE PROCESSING ---------------- #

            # Urdu → Kannada translation
            # Urdu language code = "ur"
            kannada = GoogleTranslator(source="ur", target="kn").translate(text)

            # Kannada → Urdu script (Arabic)
            # Aksharamukha uses "Urdu"
            kannada_in_urdu = aksharamukha_process("Kannada", "Urdu", kannada)

            # Kannada → English phonetics (Latin)
            kannada_english = transliterate(kannada, sanscript.KANNADA, sanscript.ITRANS)

            # Sentence audio (Kannada)
            audio_sentence = make_audio(kannada)

            # ---------------- DISPLAY OUTPUT ---------------- #
            st.markdown("## 🔹 Translation Results")

            st.markdown(f"**Urdu Input:**  \n:blue[{text}]")
            st.markdown(f"**Kannada Translation:**  \n:green[{kannada}]")
            st.markdown(f"**Kannada in Urdu Script:**  \n:orange[{kannada_in_urdu}]")
            st.markdown(f"**English Phonetics:**  \n`{kannada_english}`")

            st.markdown("### 🔊 Kannada Audio (Sentence)")
            st.audio(audio_sentence, format="audio/mp3")
            st.download_button("Download Sentence Audio", audio_sentence, "sentence.mp3")

            # ---------------- WORD-BY-WORD FLASHCARDS ---------------- #

            st.markdown("---")
            st.markdown("## 🃏 Flashcards (Word-by-Word)")

            urdu_words = text.split()
            kan_words = kannada.split()

            # Avoid crashes due to mismatch
            limit = min(len(urdu_words), len(kan_words))

            for i in range(limit):
                uw = urdu_words[i]
                kw = kan_words[i]

                # Kannada → Urdu script (word)
                kw_ur = aksharamukha_process("Kannada", "Urdu", kw)

                # Phonetics
                kw_ph = transliterate(kw, sanscript.KANNADA, sanscript.ITRANS)

                # Word audio
                kw_audio = make_audio(kw)

                with st.expander(f"Word {i+1}: {uw}", expanded=False):
                    st.write("**Urdu word:**", uw)
                    st.write("**Kannada word:**", kw)
                    st.write("**Kannada in Urdu script:**", kw_ur)
                    st.write("**Phonetics:**", kw_ph)

                    st.audio(kw_audio, format="audio/mp3")
                    st.download_button(
                        f"Download Audio (Word {i+1})",
                        kw_audio,
                        f"word_{i+1}.mp3"
                    )

        except Exception as e:
            st.error(f"Error: {e}")

    else:
        st.warning("Please enter Urdu text.")

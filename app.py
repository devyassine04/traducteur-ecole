import streamlit as st
import deepl
import os

API_KEY = "328293ea-f93c-4a68-9482-f254363a7a1e:fx"

st.set_page_config(page_title="Traducteur Scolaire", page_icon="🏫")
st.title("🌐 Traducteur de Cours & Examens")
st.write("Formats acceptés : Word (.docx, .pptx) et PDF (.pdf) avec conservation de la mise en page.")

langues_cibles = {
    "Allemand": "DE",
    "Anglais": "EN-US",
    "Arabe": "AR",
    "Espagnol": "ES"
}
langue_choisie = st.selectbox("Langue de destination :", list(langues_cibles.keys()))

fichier_upload = st.file_uploader("Uploadez votre fichier", type=["docx", "pptx", "pdf"])

if st.button("Traduire le document") and fichier_upload is not None:
    translator = deepl.Translator(API_KEY)
    
    chemin_entree = fichier_upload.name
    chemin_sortie = f"traduit_{fichier_upload.name}"
    
    with open(chemin_entree, "wb") as f: 
        f.write(fichier_upload.getbuffer())
    
    with st.spinner("Traduction en cours..."):
        try:
            translator.translate_document_from_filepath(
                chemin_entree, 
                chemin_sortie, 
                target_lang=langues_cibles[langue_choisie]
            )
            
            with open(chemin_sortie, "rb") as f:
                st.download_button(
                    label="⬇️ Télécharger le fichier traduit", 
                    data=f, 
                    file_name=chemin_sortie
                )
        except Exception as e:
            st.error(f"Erreur de l'API DeepL : {e}")
        finally:
            if os.path.exists(chemin_entree):
                os.remove(chemin_entree)
            if os.path.exists(chemin_sortie):
                os.remove(chemin_sortie)

import streamlit as st
import docx
import fitz  # PyMuPDF
from fpdf import FPDF
from deep_translator import GoogleTranslator
import io
import time

st.set_page_config(page_title="Traducteur Scolaire", page_icon="🏫")
st.title("🌐 Traducteur de Cours & Examens")
st.write("Formats acceptés : Word (.docx) avec conservation de la mise en page, et PDF (.pdf)")

langues_cibles = {"Allemand": "de", "Anglais": "en", "Arabe": "ar", "Espagnol": "es"}
langue_choisie = st.selectbox("Langue de destination :", list(langues_cibles.keys()))

fichier_upload = st.file_uploader("Uploadez votre fichier", type=["docx", "pdf"])

if st.button("Traduire le document") and fichier_upload is not None:
    extension = fichier_upload.name.split('.')[-1].lower()
    traducteur = GoogleTranslator(source='auto', target=langues_cibles[langue_choisie])
    erreur_affichee = False
    
    with st.spinner(f'Traduction en {langue_choisie} en cours... (Le processus est ralenti pour éviter les blocages)'):
        try:
            if extension == "docx":
                doc = docx.Document(fichier_upload)
                
                # Traduction des paragraphes
                for para in doc.paragraphs:
                    if para.text.strip():
                        try:
                            para.text = traducteur.translate(para.text)
                            time.sleep(0.3) # Pause anti-blocage de 0.3 seconde
                        except Exception as e:
                            if not erreur_affichee:
                                st.error(f"Blocage Google Translate : {e}")
                                erreur_affichee = True
                
                # Traduction des tableaux
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for para in cell.paragraphs:
                                if para.text.strip():
                                    try:
                                        para.text = traducteur.translate(para.text)
                                        time.sleep(0.3)
                                    except:
                                        pass

                doc_io = io.BytesIO()
                doc.save(doc_io)
                doc_io.seek(0)
                
                st.success("✅ Fichier Word traité !")
                st.download_button("⬇️ Télécharger le Word", data=doc_io, file_name=f"Traduit_{fichier_upload.name}", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

            elif extension == "pdf":
                pdf_original = fitz.open(stream=fichier_upload.read(), filetype="pdf")
                nouveau_pdf = FPDF()
                nouveau_pdf.set_auto_page_break(auto=True, margin=15)
                nouveau_pdf.add_page()
                nouveau_pdf.set_font("Arial", size=12)

                for num_page in range(pdf_original.page_count):
                    page = pdf_original.load_page(num_page)
                    texte_page = page.get_text("text")
                    
                    if texte_page.strip():
                        lignes = texte_page.split('\n')
                        texte_traduit = ""
                        for ligne in lignes:
                            if ligne.strip():
                                try:
                                    texte_traduit += traducteur.translate(ligne) + "\n"
                                    time.sleep(0.3)
                                except Exception as e:
                                    if not erreur_affichee:
                                        st.error(f"Blocage Google Translate : {e}")
                                        erreur_affichee = True
                                    texte_traduit += ligne + "\n"
                        
                        texte_traduit = texte_traduit.encode('latin-1', 'replace').decode('latin-1')
                        nouveau_pdf.multi_cell(0, 10, txt=texte_traduit)
                    
                    nouveau_pdf.add_page()

                pdf_io = io.BytesIO(nouveau_pdf.output(dest='S').encode('latin-1'))
                st.success("✅ Fichier PDF traité !")
                st.download_button("⬇️ Télécharger le PDF", data=pdf_io, file_name=f"Traduit_{fichier_upload.name}", mime="application/pdf")

        except Exception as e:
            st.error(f"Erreur technique globale : {e}")

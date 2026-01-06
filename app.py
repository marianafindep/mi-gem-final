import streamlit as st
import google.generative_ai as genai

st.set_page_config(page_title="Generador de Historias", page_icon="✨")

# --- ESTILOS ---
st.markdown("""<style>.stButton>button {width: 100%; background-color: #0068C9; color: white;}</style>""", unsafe_allow_html=True)

st.title("🚀 Generador de Historias de Usuario")

# --- LÓGICA ---
def generar_historia(prompt_usuario):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key: return "⚠️ Error: Configura tu GEMINI_API_KEY en los Secrets."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"ERES un Product Manager experto. Crea una historia de usuario INVEST basada en esto: {prompt_usuario}")
        return response.text
    except Exception as e: return f"Error: {str(e)}"

# --- UI ---
col1, col2 = st.columns(2)
rol = col1.text_input("Como...", placeholder="Ej: Cliente")
meta = col2.text_input("Quiero...", placeholder="Ej: Pagar con tarjeta")
beneficio = st.text_input("Para...", placeholder="Ej: No usar efectivo")

if st.button("Generar"):
    if rol and meta and beneficio:
        with st.spinner("Creando..."):
            st.markdown(generar_historia(f"Como {rol}, quiero {meta}, para {beneficio}"))
    else:
        st.warning("Completa los 3 campos.")

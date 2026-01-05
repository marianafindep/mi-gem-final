import streamlit as st
import subprocess
import sys

# --- BLOQUE MÁGICO DE AUTO-INSTALACIÓN ---
# Esto obliga al sistema a instalar la herramienta si no la encuentra
try:
    import google.generative_ai as genai
except ImportError:
    st.warning("Instalando herramientas de IA... espera unos segundos...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generative-ai"])
    import google.generative_ai as genai
    st.rerun() # Recarga la página automáticamente al terminar

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Generador de Historias", page_icon="✨")

# --- INTERFAZ SIMPLE ---
st.title("🚀 Generador de Historias de Usuario")
st.markdown("---")

# --- LÓGICA DE LA IA ---
def generar_historia(prompt_usuario):
    # Recuperamos la clave de los secretos
    api_key = st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        return "⚠️ Error: No encontré la GEMINI_API_KEY en los 'Secrets' de Streamlit."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Prompt del sistema resumido para no ocupar espacio
        system_instruction = """
        Actúa como experto en Product Management. 
        Recibirás una solicitud básica y debes generar una Historia de Usuario formato INVEST.
        Estructura: Título, Como/Quiero/Para, Criterios de Aceptación (Gherkin).
        """
        
        full_prompt = f"{system_instruction}\n\nSolicitud del usuario: {prompt_usuario}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Ocurrió un error: {str(e)}"

# --- FORMULARIO ---
col1, col2 = st.columns(2)
with col1:
    rol = st.text_input("Como...", placeholder="Ej: Vendedor")
with col2:
    meta = st.text_input("Quiero...", placeholder="Ej: ver mis ventas")
    
beneficio = st.text_input("Para...", placeholder="Ej: saber cuánto gané")

if st.button("Generar Historia Profesional"):
    if rol and meta and beneficio:
        with st.spinner("La IA está escribiendo..."):
            texto_final = generar_historia(f"Como {rol}, quiero {meta}, para {beneficio}")
            st.markdown(texto_final)
    else:
        st.warning("Por favor completa los 3 campos.")

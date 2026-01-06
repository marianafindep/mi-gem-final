import streamlit as st
import google.generative_ai as genai

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Generador de Historias", page_icon="✨")

st.markdown("""
    <style>
    .stButton>button {width: 100%; background-color: #0068C9; color: white;}
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Generador de Historias de Usuario")
st.markdown("Transforma una idea breve en una especificación técnica lista para desarrollo.")

# --- LÓGICA INTELIGENTE ---
def generar_historia(prompt_usuario):
    # Busca la clave en los secretos
    api_key = st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        return "⚠️ Error: No encontré la clave API. Configúrala en 'Secrets'."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Tu prompt experto resumido
        system_instruction = """
        ERES un experto Product Manager.
        Tu tarea: Convertir el input del usuario en una Historia de Usuario formato INVEST.
        Output esperado:
        1. Título
        2. "Como [Rol], Quiero [Acción], Para [Beneficio]"
        3. Criterios de Aceptación (Gherkin: Dado/Cuando/Entonces).
        4. Estimación de esfuerzo.
        """
        
        full_prompt = f"{system_instruction}\n\nRequerimiento del usuario: {prompt_usuario}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error de conexión con Google: {str(e)}"

# --- INTERFAZ ---
col1, col2 = st.columns(2)
with col1:
    rol = st.text_input("Como...", placeholder="Ej: Vendedor")
with col2:
    meta = st.text_input("Quiero...", placeholder="Ej: descargar reporte PDF")
    
beneficio = st.text_input("Para...", placeholder="Ej: enviarlo por correo")

if st.button("Generar Historia Profesional"):
    if rol and meta and beneficio:
        with st.spinner("Redactando criterios de aceptación..."):
            resultado = generar_historia(f"Como {rol}, quiero {meta}, para {beneficio}")
            st.markdown("---")
            st.markdown(resultado)
    else:
        st.warning("Completa los 3 campos por favor.")

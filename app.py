import streamlit as st
import google.generative_ai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Generador de Historias de Usuario",
    page_icon="🚀",
    layout="centered"
)

# --- ESTILOS VISUALES (CSS) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #0068C9;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stTextInput>div>div>input {
        background-color: #F0F2F6;
    }
    </style>
""", unsafe_allow_html=True)

# --- TU CEREBRO (EL PROMPT ORIGINAL) ---
SYSTEM_PROMPT = """
ERES un Entrenador de Producto/Asistente de Calidad extremadamente riguroso y conciso.
Tu objetivo es transformar una entrada mínima en una Historia de Usuario profesional (INVEST + Gherkin).

REGLAS CORE:
1. Si falta información (Rol, Qué, Para qué), asúmela o genérala lógicamente.
2. Si el 'Qué' es una solución técnica (ej: botón rojo), reformúlalo a necesidad funcional.
3. Genera entre 3 y 5 Criterios de Aceptación Gherkin (Dado/Cuando/Entonces), incluyendo casos de error.
4. Estima el esfuerzo (Fibonacci: 1, 2, 3, 5, 8, 13).

FORMATO DE SALIDA FINAL OBLIGATORIO:
### 📄 HISTORIA DE USUARIO LISTA

| Campo | Valor |
| :--- | :--- |
| **Prioridad** | [ALTA/MEDIA/BAJA] |
| **Esfuerzo** | [Fibonacci] Puntos |

#### 1. Título Conciso
[Título breve]

#### 2. Cuerpo de la Historia
Como **[Rol]**, quiero **[Meta]**, para **[Beneficio]**.

#### 3. Criterios de Aceptación (Gherkin)
* **[Criterio #1]**
    * **Dado** ...
    * **Cuando** ...
    * **Entonces** ...

(Genera más criterios aquí...)

#### 4. Requisito de Diseño
* **Estado:** [SÍ/PENDIENTE]
"""

# --- LÓGICA DE CONEXIÓN ---
def generar_historia(rol, meta, beneficio):
    # Intentamos obtener la clave secreta
    api_key = st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        return "⚠️ Error Crítico: No se encontró la API Key en los 'Secrets' de Streamlit."

    try:
        genai.configure(api_key=api_key)
        # Usamos flash porque es rápido y eficiente
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        # Construimos el mensaje del usuario
        user_msg = f"Rol: {rol}. Meta: {meta}. Beneficio: {beneficio}."
        
        response = model.generate_content(user_msg)
        return response.text
    except Exception as e:
        return f"❌ Ocurrió un error al conectar con Google: {str(e)}"

# --- INTERFAZ DE USUARIO (FRONTEND) ---
st.title("🚀 Fábrica de Historias de Usuario")
st.markdown("Completa los campos para generar una especificación técnica lista para desarrollo.")

col1, col2 = st.columns(2)
with col1:
    rol = st.text_input("Como...", placeholder="Ej: Administrador")
with col2:
    meta = st.text_input("Quiero...", placeholder="Ej: descargar reporte PDF")

beneficio = st.text_input("Para...", placeholder="Ej: tener respaldo mensual")

# Botón de acción
if st.button("Generar Historia Profesional"):
    if rol and meta and beneficio:
        with st.spinner("🧠 La IA está redactando los criterios Gherkin..."):
            resultado = generar_historia(rol, meta, beneficio)
            st.markdown("---")
            st.markdown(resultado)
            st.balloons() # ¡Un toque de celebración si sale bien!
    else:
        st.warning("⚠️ Por favor completa los 3 campos (Como, Quiero, Para).")

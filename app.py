import streamlit as st
import google.generative_ai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Generador de Historias de Usuario",
    page_icon="✅",
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
    div[data-testid="stMarkdownContainer"] h1 {
        font-size: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- TU PROMPT (EL CEREBRO) ---
SYSTEM_PROMPT = """
ERES un Entrenador de Producto/Asistente de Calidad **extremadamente riguroso y conciso**. Tu tarea es asegurar la claridad, especificidad y completitud de cada Historia de Usuario (HU).

Tu objetivo principal es **MINIMIZAR LA INTERACCIÓN DEL USUARIO** transformando la entrada mínima en una HU profesional, lista para desarrollo, aplicando todas las heurísticas de calidad (INVEST, Gherkin, Puntos de Historia) de forma autónoma. Solo pide intervención si falta información crítica o la historia viola una regla INVEST esencial.

## I. ESTRUCTURA DE ENTRADA PREFERIDA
La entrada ideal es la estructura: "Como [Rol], quiero [Meta/Qué], para [Beneficio/Por Qué]".

## II. REGLAS CORE Y PROCESAMIENTO (La Inteligencia de la GEM)

### A. Detección de Intención y Pre-validación
1.  **Detección:** Al inicio, determina si el usuario quiere (A) Crear una nueva HU o (B) Revisar/Mejorar una HU existente.
2.  **Estructura Crítica:** Si la entrada inicial carece de alguno de los tres componentes (Quién, Qué, Para Qué), **pregunta de vuelta solo por el componente faltante**. No procedas hasta tener la estructura completa.

### B. VALIDACIÓN AUTOMÁTICA (INVEST Riguroso)
Aplica los siguientes cheques **internamente** y solo genera una pregunta de usuario si la falla es crítica:
1.  **V (Valiosa):** Si el 'Para Qué' es una repetición vaga del 'Qué', activa un *flag* interno y corrige o refuerza el valor de negocio antes de la salida.
2.  **N (Negociable):** Si el 'Qué' describe una solución de diseño específica (ej: "un botón de color rojo", "un pop-up"), **automáticamente** reformúlalo para que se centre en la necesidad funcional.
3.  **I/S (Independiente/Pequeña):** Si el 'Qué' contiene más de dos verbos de acción fuertes (ej: crear, editar, eliminar) o usa conectores de dependencia ("después de", "antes de"), **sugiere la división** y asigna una puntuación alta (8 o 13) en Esfuerzo Sugerido.

### C. GENERACIÓN AVANZADA DE REQUISITOS
1.  **Criterios de Aceptación (Gherkin):** Genera un **mínimo de 3 y un máximo de 5 Criterios de Aceptación** usando la sintaxis **Gherkin (Dado/Cuando/Entonces)**.
    * **Obligatorio:** Los criterios deben cubrir el **Caso Positivo (Happy Path)** y al menos **un Caso Negativo o de Error/Límite** (datos inválidos, permisos, límites del sistema).
    * **Mejora de CAs Existentes (Flujo B):** Si el usuario proporciona CAs genéricos (ej: "Funciona bien"), la GEM los reemplaza automáticamente por la estructura Gherkin generada, manteniendo la intención original.
2.  **Esfuerzo y Prioridad:**
    * **Puntos de Historia (Esfuerzo):** Asigna una sugerencia de Esfuerzo usando la Secuencia de Fibonacci: **1, 2, 3, 5, 8, 13**. (1-3 simple, 5-8 complejo, 13 es Épica/División).
    * **Prioridad:** Asigna la Prioridad (**ALTA/MEDIA/BAJA**) basada en la importancia del 'Beneficio/Para Qué'.

### D. Requisito de Diseño (Punto de Control)
1.  **Boceto:** Antes de la salida final, verifica si se ha adjuntado o mencionado un diseño/boceto. Si no, genera la pregunta: "¿Existe un boceto o diseño para esta historia?".

## III. FORMATO DE SALIDA FINAL

Tu respuesta final, ya sea para una HU nueva o mejorada, debe ser un único bloque de texto, usando este formato **ESTRICTO** y completando cada sección con la información obtenida y generada.

---
### 📄 HISTORIA DE USUARIO LISTA

| Campo | Valor |
| :--- | :--- |
| **ID Sugerido** | [HU-XXX] (ID aleatorio o basado en el sistema) |
| **Prioridad Sugerida** | [ALTA/MEDIA/BAJA] |
| **Esfuerzo Sugerido** | [1/2/3/5/8/13] Puntos |

#### 1. Título Conciso
[Título breve y accionable generado (Ej. Restablecimiento de contraseña)]

#### 2. Cuerpo de la Historia
Como **[Rol reformulado si fue necesario]**, quiero **[Meta/Qué reformulado si fue necesario]**, para **[Valor/Beneficio]**.

#### 3. Criterios de Aceptación (Gherkin)
(Generados automáticamente. Mínimo 3, Máximo 5)

* **[Criterio #1: Caso Positivo]**
    * **Dado** [Contexto],
    * **Cuando** [Acción],
    * **Entonces** [Resultado esperado].

* **[Criterio #2: Caso Negativo/Error]**
    * **Dado** [Contexto],
    * **Cuando** [Acción de error],
    * **Entonces** [Mensaje o respuesta de sistema esperado].

* ... (Continúa con el resto de los criterios generados)

#### 4. Requisito de Diseño/Boceto
| Confirmación | Comentarios/Descripción |
| :--- | :--- |
| **[SÍ/PENDIENTE]** | [Descripción breve de los elementos clave si no se adjuntó, o simple confirmación.] |

---

**CONFIRMACIÓN DE LA GEM:**
[Si todas las reglas fueron validadas y la HU está completa, añade: "✅ Esta historia de usuario está lista para ser aprobada y enviada a desarrollo."]

## IV. FRASES DE INTERACCIÓN INICIAL Y DE SEGUIMIENTO
... (Omitido para brevedad en el prompt, el sistema lo manejará) ...
Cuando la historia de usuario esté lista, genera una sección final llamada 'CONTENIDO PARA WORD'.
REGLAS CRUCIALES:
NO uses bloques de código.
Usa Encabezados de Markdown.
Usa Tablas de Markdown reales.
"""

# --- LÓGICA PRINCIPAL ---

def get_gemini_response(prompt_input):
    # Intentamos obtener la clave de los secretos de Streamlit
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        st.error("⚠️ Falta la API Key en los 'Secrets' de la configuración.")
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    try:
        response = model.generate_content(prompt_input)
        return response.text
    except Exception as e:
        return f"Error en Gemini: {str(e)}"

# --- INTERFAZ (FRONTEND) ---

st.title("Asistente de Historias de Usuario")
st.markdown("Genera historias profesionales (formato INVEST + Gherkin) en segundos.")

# Usamos pestañas para organizar
tab1, tab2 = st.tabs(["✨ Crear Nueva", "🛠️ Mejorar Existente"])

# PESTAÑA 1: CREAR
with tab1:
    st.info("Ingresa los 3 componentes clave. La IA hará el resto.")
    
    col_rol, col_meta = st.columns(2)
    with col_rol:
        rol = st.text_input("Como...", placeholder="Ej: Vendedor")
    with col_meta:
        meta = st.text_input("Quiero...", placeholder="Ej: ver mis comisiones")
        
    beneficio = st.text_input("Para...", placeholder="Ej: saber cuánto cobraré a fin de mes")
    
    if st.button("Generar Historia Profesional", key="btn_new"):
        if rol and meta and beneficio:
            with st.spinner("Redactando criterios Gherkin y calculando esfuerzo..."):
                full_prompt = f"Como {rol}, quiero {meta}, para {beneficio}"
                resultado = get_gemini_response(full_prompt)
                if resultado:
                    st.markdown("---")
                    st.markdown(resultado)
        else:
            st.warning("Por favor completa los 3 campos.")

# PESTAÑA 2: MEJORAR
with tab2:
    st.write("Pega un requerimiento mal escrito o incompleto:")
    bad_story = st.text_area("Texto original", height=100, placeholder="Ej: El cliente quiere que el logo sea más grande y azul.")
    
    if st.button("Analizar y Mejorar", key="btn_fix"):
        if bad_story:
            with st.spinner("Aplicando reglas de calidad..."):
                full_prompt = f"Mejora esta historia o requerimiento: {bad_story}"
                resultado = get_gemini_response(full_prompt)
                if resultado:
                    st.markdown("---")
                    st.markdown(resultado)
        else:
            st.warning("Escribe algo para mejorar.")

# Footer
st.markdown("---")
st.caption("Herramienta interna de Calidad | Powered by Gemini AI")

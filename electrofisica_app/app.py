import streamlit as st
import numpy as np
import random
import socket
import base64
import io
from physics_engine import (
    Charge, 
    find_zero_field_point_1d,
    calculate_force_on_charge, 
    calculate_electric_field_at_point,
    calculate_potential_at_point,
    simulate_test_charge_trajectory
)
from visualizer import plot_force_only_2d, plot_2d_field_and_potential

# Configuración de página
st.set_page_config(
    page_title="ElectroLab 3D - Edición Completa",
    page_icon="⚡",
    layout="wide"
)

# --- FUNCIÓN: obtener IP local de la red Wi-Fi ---
@st.cache_data
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# --- FUNCIÓN: generar QR como imagen PNG en base64 ---
@st.cache_data
def generate_qr_base64(url: str) -> str:
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except ImportError:
        return None

# --- SIDEBAR: QR para abrir en el celular ---
with st.sidebar:
    st.markdown("### 📱 Abrir en tu Celular")

    cloud_url = st.text_input(
        "🌐 URL Pública (Streamlit Cloud):",
        placeholder="https://tu-app.streamlit.app",
        help="Pegá acá tu link de Streamlit Cloud para que el QR funcione desde cualquier red (ej: la Safa, la casa de un amigo, etc.)"
    )

    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:8501"

    if cloud_url and cloud_url.startswith("http"):
        qr_url = cloud_url
        qr_mode = "🌐 PÚBLICO"
    else:
        qr_url = local_url
        qr_mode = "🏠 LOCAL (misma Wi-Fi)"

    qr_b64 = generate_qr_base64(qr_url)
    if qr_b64:
        st.markdown(
            f'<div style="text-align:center;background:white;padding:10px;border-radius:12px;">'
            f'<img src="data:image/png;base64,{qr_b64}" width="200"/>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.caption(f"📷 Escaneá con la cámara — Modo: **{qr_mode}**")

    st.code(qr_url, language=None)

    if cloud_url and cloud_url.startswith("http"):
        st.success("✅ **Link público activo**: funciona desde CUALQUIER red y celular del mundo.")
    else:
        st.info("☝️ Modo local: el celular debe estar en la **misma red Wi-Fi** que esta PC.")
        st.caption("💡 Subí la app a Streamlit Cloud y pegá el link arriba para que funcione desde cualquier lugar.")

    st.markdown("---")

# Estilos CSS Avanzados
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2.3rem;
        font-weight: 800;
        color: #00FFCC;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        font-size: 1.05rem;
        color: #A0AAB8;
        margin-bottom: 20px;
    }
    .info-box {
        background-color: #1E222D;
        border-left: 5px solid #00FFCC;
        padding: 15px;
        border-radius: 8px;
        font-size: 1.1rem;
        margin-bottom: 15px;
    }
    .quiz-card {
        background: linear-gradient(135deg, #192033 0%, #111625 100%);
        border: 2px solid #00FFCC;
        border-radius: 15px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(0, 255, 204, 0.15);
        margin-bottom: 20px;
    }
    .quiz-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .step-badge {
        background-color: #00FFCC;
        color: #000000;
        font-weight: bold;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 1.1rem;
    }
    .diff-badge {
        background-color: #3B82F6;
        color: #FFFFFF;
        font-weight: bold;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.95rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: #191C24;
        border-radius: 8px;
        font-size: 1.05rem;
        font-weight: bold;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00FFCC !important;
        color: #111 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚡ ElectroLab: Edición Definitiva con Glosario</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Laboratorio Electrostático, Glosario Completo de Definiciones & Juego de 8 Escalones</div>', unsafe_allow_html=True)

def render_qr_expander():
    with st.expander("📱 **Escaneá el Código QR para abrir la App en tu Celular**", expanded=False):
        c_qr1, c_qr2 = st.columns([1, 2])
        with c_qr1:
            if qr_b64:
                st.markdown(
                    f'<div style="text-align:center;background:white;padding:10px;border-radius:10px;max-width:180px;">'
                    f'<img src="data:image/png;base64,{qr_b64}" width="160"/>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        with c_qr2:
            st.markdown(f"**Dirección**: `{qr_url}` ({qr_mode})")
            st.caption("📷 Escaneá con la cámara de tu teléfono para abrir esta app en tu pantalla.")

# ---------------------------------------------------------
# BANCO EXTENDIDO Y AUDITADO DE PREGUNTAS (SIN NÚMEROS REPETIDOS)
# ---------------------------------------------------------
PREGUNTAS_JUEGO = {
    "Fácil": [
        {"q": "¿Qué ocurre electrostáticamente entre dos cargas del MISMO signo?", "opts": ["Se repelen mutuamente", "Se atraen mutuamente", "No interactúan", "Se anulan liberando calor"], "ans": 0, "exp": "Cargas de igual signo (+ con + o - con -) generan fuerzas repulsivas."},
        {"q": "¿Cuál es la unidad del Sistema Internacional (SI) para la carga eléctrica?", "opts": ["Coulomb (C)", "Newton (N)", "Voltio (V)", "Joule (J)"], "ans": 0, "exp": "La unidad fundamental de carga eléctrica es el Coulomb (C)."},
        {"q": "¿Qué establece el principio de CUANTIZACIÓN de la carga eléctrica?", "opts": ["Toda carga libre es un múltiplo entero de e (q = n·e)", "La carga puede tomar cualquier valor continuo", "La carga varía según la temperatura del cuerpo", "La carga depende únicamente del volumen"], "ans": 0, "exp": "La carga eléctrica existe en paquetes discretos múltiplos enteros de e = 1.602x10⁻¹⁹ C."},
        {"q": "Si la distancia entre dos cargas puntuales se DUPLICA (x2), ¿qué ocurre con la fuerza electrostática?", "opts": ["Se reduce a la cuarta parte (F / 4)", "Se reduce a la mitad (F / 2)", "Se duplica (F x 2)", "Se cuadruplica (F x 4)"], "ans": 0, "exp": "Según la Ley de Coulomb, la fuerza es inversamente proporcional al cuadrado de la distancia (1/r²)."},
        {"q": "¿Cuál es la dirección radial de las líneas de campo eléctrico generadas por una carga POSITIVA?", "opts": ["Hacia afuera (salientes de la carga)", "Hacia adentro (entrantes a la carga)", "En espiral cerrada continua", "Paralelas al plano neutro"], "ans": 0, "exp": "Por convención, las líneas de campo eléctrico nacen en las cargas positivas y salen radialmente."},
        {"q": "¿Qué partícula subatómica posee carga eléctrica de signo NEGATIVO?", "opts": ["Electrón", "Protón", "Neutrón", "Fotón"], "ans": 0, "exp": "El electrón lleva la carga elemental negativa (-1.602x10⁻¹⁹ C)."},
        {"q": "¿Qué partícula subatómica posee carga eléctrica de signo POSITIVO?", "opts": ["Protón", "Electrón", "Neutrón", "Gluón"], "ans": 0, "exp": "El protón lleva la carga elemental positiva (+1.602x10⁻¹⁹ C)."},
        {"q": "¿Qué tipo de fuerza ocurre entre dos cargas eléctricas de SIGNOS OPUESTOS?", "opts": ["Fuerza de atracción", "Fuerza de repulsión", "Fuerza nula", "Fuerza tangencial pura"], "ans": 0, "exp": "Cargas de distinto signo (+ y -) se atraen mutuamente."},
        {"q": "¿Cómo se comparan los módulos de carga del protón y del electrón?", "opts": ["Son exactamente iguales en módulo (|e|)", "El protón es 1836 veces mayor", "El electrón es mayor en módulo", "Depende del medio material"], "ans": 0, "exp": "Ambos tienen exactamente el mismo valor absoluto (|e| ≈ 1.602x10⁻¹⁹ C), cambiando solo el signo."},
        {"q": "¿Cuál es la notación estándar de la Constante Electrostática de Coulomb?", "opts": ["k_e", "G", "c", "h"], "ans": 0, "exp": "La constante electrostática se representa simbólicamente como k_e o simplemente k."},
        {"q": "¿Qué instrumento clásico de laboratorio detecta la presencia de carga eléctrica por separación de láminas?", "opts": ["Electroscopio", "Voltímetro", "Amperímetro", "Manómetro"], "ans": 0, "exp": "El electroscopio utiliza el principio de repulsión entre láminas delgadas para detectar carga."},
        {"q": "Si el valor de una de las cargas se DUPLICA (x2) manteniendo la distancia constante, ¿qué le sucede a la fuerza?", "opts": ["Se duplica (F x 2)", "Se cuadruplica (F x 4)", "Se reduce a la mitad (F / 2)", "Permanece sin cambios"], "ans": 0, "exp": "La fuerza de Coulomb es directamente proporcional al producto de las cargas (F ∝ q1·q2)."},
        {"q": "¿Puede existir una carga libre aislada cuyo valor sea exactamente 1.5 e?", "opts": ["No, porque la carga libre está estrictamente cuantizada en enteros (n ∈ ℤ)", "Sí, en cualquier material conductor", "Sí, si se calienta el objeto", "Solo en gases ionizados"], "ans": 0, "exp": "La cuantización prohíbe fracciones de la carga elemental en estado libre."},
        {"q": "¿Qué establece la Ley de Conservación de la Carga Eléctrica en un sistema aislado?", "opts": ["La carga neta total se mantiene constante", "La carga siempre tiende a cero", "Las cargas negativas se convierten en positivas", "La carga total aumenta con el movimiento"], "ans": 0, "exp": "En todo proceso físico cerrado, la suma algebraica de las cargas no cambia."},
        {"q": "¿Qué combinación de unidades en el SI equivale a 1 Voltio (V)?", "opts": ["1 Joule por Coulomb (1 J/C)", "1 Newton por Metro (1 N·m)", "1 Watt por Segundo (1 W/s)", "1 Coulomb por Segundo (1 C/s)"], "ans": 0, "exp": "Por definición, 1 Voltio es 1 Joule de energía por cada Coulomb de carga (1 V = 1 J/C)."},
        {"q": "¿Qué significa que un cuerpo macroscópico esté en estado NEUTRO?", "opts": ["Posee igual cantidad de protones que de electrones", "No contiene electrones ni protones", "Solo contiene neutrones en su estructura", "Tiene energía potencial cero"], "ans": 0, "exp": "Estar neutro significa equilibrio numérico exacto entre cargas positivas y negativas."},
        {"q": "¿Cómo se denomina al proceso de electrizar un objeto neutro acercándole otro cargado SIN tocarlo?", "opts": ["Inducción electrostática", "Conducción o contacto", "Fricción o rozamiento", "Polarización magnética"], "ans": 0, "exp": "La inducción produce redistribución de carga a distancia sin transferencia directa."},
        {"q": "¿Cómo se denomina al proceso de electrizar dos objetos neutros frotándolos entre sí?", "opts": ["Fricción o rozamiento", "Inducción electrostática", "Conducción directa", "Radiación iónica"], "ans": 0, "exp": "Al frotar dos cuerpos de distinta afinidad electrónica, uno cede electrones al otro."},
        {"q": "¿A cuánto equivale la unidad 1 microcoulomb (1 µC) en Coulombs?", "opts": ["10⁻⁶ C", "10⁻³ C", "10⁻⁹ C", "10⁻¹² C"], "ans": 0, "exp": "El prefijo micro (µ) representa una millonésima parte (10⁻⁶)."},
        {"q": "¿El Campo Eléctrico es una magnitud de tipo Escalar o Vectorial?", "opts": ["Vectorial (posee magnitud, dirección y sentido)", "Escalar (solo requiere un número)", "Adimensional pura", "Tensor de segundo orden"], "ans": 0, "exp": "El campo eléctrico E se define con dirección y sentido en el espacio."}
    ],
    "Medio": [
        {"q": "¿Cuál es el valor numérico aproximado de la Constante de Coulomb (k_e) en el vacío?", "opts": ["8.99 x 10⁹ N·m²/C²", "6.67 x 10⁻¹¹ N·m²/kg²", "3.00 x 10⁸ m/s", "1.60 x 10⁻¹⁹ C"], "ans": 0, "exp": "k_e ≈ 8.98755 x 10⁹ N·m²/C² en el Sistema Internacional."},
        {"q": "Si en un punto del espacio el campo eléctrico neto es CERO (E = 0), ¿cuál es la fuerza sobre una carga q situada allí?", "opts": ["Exactamente 0 Newtons", "Una fuerza infinita", "Fuerza igual a k_e·q", "Depende de la masa de la carga"], "ans": 0, "exp": "Dado que F = q·E, si E = 0 N/C la fuerza resultante es 0 N."},
        {"q": "¿Cómo se define formalmente una Superficie Equipotencial?", "opts": ["Un lugar geométrico donde el potencial escalar V es constante en todos sus puntos", "Una superficie donde el campo E es nulo", "Una región de fuerza máxima", "Una zona sin cargas libres"], "ans": 0, "exp": "En cualquier punto de una superficie equipotencial, V toma el mismo valor numérico."},
        {"q": "Entre dos cargas puntuales de IGUAL signo y magnitud, ¿dónde se ubica el punto de campo cero (E = 0)?", "opts": ["En el punto medio exacto del segmento que las une", "En el infinito exclusivamente", "Sobre la superficie de la primera carga", "No existe punto de campo cero"], "ans": 0, "exp": "Por simetría, los dos vectores de campo de igual magnitud y sentidos opuestos se anulan en el centro."},
        {"q": "¿Con qué ángulo cortan las líneas de Campo Eléctrico a las Superficies Equipotenciales?", "opts": ["Perpendicularmente a 90°", "Paralelamente a 0°", "A 45° exactos", "Depende del signo de la carga"], "ans": 0, "exp": "Las líneas de campo E siempre son ortogonales (90°) a las equipotenciales."},
        {"q": "¿Cuál es el valor aproximado de la Permitividad del Vacío (ε_0)?", "opts": ["8.854 x 10⁻¹² C²/N·m²", "8.988 x 10⁹ N·m²/C²", "1.602 x 10⁻¹⁹ C", "9.806 m/s²"], "ans": 0, "exp": "ε_0 es la constante fundamental de permitividad electrostática del vacío."},
        {"q": "Si la distancia entre dos cargas se reduce a la MITAD (r / 2), ¿qué le sucede a la fuerza electrostática?", "opts": ["Se CUADRUPLICA (F x 4)", "Se duplica (F x 2)", "Se reduce a la mitad (F / 2)", "Se reduce a la cuarta parte"], "ans": 0, "exp": "F ∝ 1/(1/2)² = 4. Al reducir la distancia a la mitad, la fuerza aumenta 4 veces."},
        {"q": "¿El Potencial Eléctrico (V) es una magnitud de tipo Escalar o Vectorial?", "opts": ["Escalar (se define mediante un valor numérico y su signo)", "Vectorial (requiere dirección y sentido)", "Matricial", "Adimensional"], "ans": 0, "exp": "El potencial eléctrico V mide energía por unidad de carga (J/C = V), siendo un escalar."},
        {"q": "¿Qué relación matemática conecta la constante k_e con la permitividad ε_0?", "opts": ["k_e = 1 / (4 · π · ε_0)", "k_e = 4 · π · ε_0", "k_e = ε_0 / (4 · π)", "k_e = (4 · π) / ε_0"], "ans": 0, "exp": "k_e se define exactamente como 1 / (4π ε_0)."},
        {"q": "¿Qué trabajo realiza la fuerza electrostática al desplazar una carga sobre una MISMA superficie equipotencial?", "opts": ["Cero Joules (0 J)", "Trabajo igual a q·V", "Trabajo máximo posible", "Depende del camino recorrido"], "ans": 0, "exp": "Como ΔV = 0 en la misma equipotencial, el trabajo es W = -q·ΔV = 0 J."},
        {"q": "¿A cuánto equivale la unidad 1 nanocoulomb (1 nC) en Coulombs?", "opts": ["10⁻⁹ C", "10⁻⁶ C", "10⁻¹² C", "10⁻³ C"], "ans": 0, "exp": "El prefijo nano (n) representa una milmillonésima parte (10⁻⁹)."},
        {"q": "En equilibrio electrostático, ¿cuánto vale el campo eléctrico en el INTERIOR de un conductor sólido?", "opts": ["Cero (E = 0 N/C)", "Un valor uniforme infinito", "Depende del volumen total", "Igual al campo exterior"], "ans": 0, "exp": "Las cargas libres se desplazan a la superficie exterior hasta que el campo interno es 0 (Jaula de Faraday)."},
        {"q": "¿Hacia dónde acelera espontáneamente una carga POSITIVA libre dentro de un campo eléctrico?", "opts": ["Hacia regiones de MENOR potencial eléctrico V", "Hacia regiones de mayor potencial eléctrico V", "En dirección perpendicular al campo", "Permanece en reposo"], "ans": 0, "exp": "Las cargas positivas sienten fuerza en la misma dirección de E, moviéndose de alto a bajo potencial."},
        {"q": "¿Hacia dónde acelera espontáneamente una carga NEGATIVA libre dentro de un campo eléctrico?", "opts": ["Hacia regiones de MAYOR potencial eléctrico V", "Hacia regiones de menor potencial eléctrico V", "En trayectoria circular uniforme", "Hacia el infinito"], "ans": 0, "exp": "Las cargas negativas sienten fuerza opuesta a E, moviéndose de bajo a alto potencial."},
        {"q": "En la Ley de Coulomb vectorial, ¿cuál es la función del vector unitario r_hat?", "opts": ["Indicar únicamente la dirección y sentido de la línea de acción", "Multiplicar la magnitud por la distancia", "Convertir el resultado en escalar", "Representar la masa de la partícula"], "ans": 0, "exp": "El vector unitario r_hat tiene módulo 1 y otorga carácter vectorial a la fuerza."},
        {"q": "Para dos cargas del mismo signo donde |q1| < |q2|, ¿de cuál carga estará más cerca el punto E = 0?", "opts": ["De la carga de MENOR magnitud (|q1|)", "De la carga de mayor magnitud (|q2|)", "En el punto medio exacto", "Fuera de la línea que las une"], "ans": 0, "exp": "Para equilibrar intensidades de campo, el punto nulo debe estar más próximo a la carga más pequeña."},
        {"q": "¿Cuál es la expresión para la aceleración (a) de una partícula cargada q con masa m en un campo E?", "opts": ["a = (q · E) / m", "a = (m · E) / q", "a = q · m · E", "a = E / (q · m)"], "ans": 0, "exp": "De F = m·a y F = q·E se despeja a = (q·E)/m."},
        {"q": "¿Qué es un Dipolo Eléctrico puntual?", "opts": ["Un par de cargas de igual magnitud y signos opuestos separadas una distancia d", "Dos cargas positivas en contacto", "Una carga aislada en movimiento", "Tres cargas en triángulo"], "ans": 0, "exp": "Un dipolo consta de +q y -q separadas por una pequeña distancia d."},
        {"q": "¿Cómo se define el módulo del momento dipolar eléctrico (p) para cargas +q y -q separadas d?", "opts": ["p = q · d", "p = q / d", "p = q² · d", "p = k_e · q / d²"], "ans": 0, "exp": "El momento dipolar se define como el producto p = q·d."},
        {"q": "¿El potencial eléctrico V creado por una carga puntual POSITIVA aislada en el espacio es positivo o negativo?", "opts": ["Es positivo en todo el espacio (V > 0)", "Es negativo en todo el espacio (V < 0)", "Es cero en todos lados", "Cambia de signo con la distancia"], "ans": 0, "exp": "V = k_e·q/r. Como q > 0 y r > 0, el potencial es siempre positivo."}
    ],
    "Difícil": [
        {"q": "¿En qué consiste formalmente el Principio de SUPERPOSICIÓN de Fuerzas Eléctricas?", "opts": ["La fuerza total sobre una carga es la SUMA VECTORIAL de las fuerzas individuales ejercidas por las demás", "La fuerza total es la suma escalar de los módulos", "Las fuerzas se multiplican algebraicamente", "La carga de mayor magnitud anula a las demás"], "ans": 0, "exp": "El principio permite calcular F_total = ∑ F_i mediante adición vectorial de componentes."},
        {"q": "Entre dos cargas de SIGNOS OPUESTOS de distinta magnitud (|q1| < |q2|), ¿dónde se ubica el punto E = 0?", "opts": ["Fuera del segmento, del lado de la carga de MENOR magnitud (|q1|)", "En el punto medio del segmento", "Fuera del segmento, del lado de la carga mayor", "En ningún punto del espacio continuo"], "ans": 0, "exp": "Fuera del segmento las componentes tienen sentidos opuestos y se igualan cerca de la carga menor."},
        {"q": "¿Qué ecuación conecta el trabajo electrostático conservativo (W) con la diferencia de potencial (ΔV)?", "opts": ["W = -q · ΔV", "W = q · E²", "W = k_e · q / r", "W = F · r²"], "ans": 0, "exp": "El trabajo realizado por el campo es W = -ΔU = -q·ΔV = q(V_inicial - V_final)."},
        {"q": "Tres cargas positivas iguales +q están en los vértices de un triángulo equilátero. ¿Cuánto vale E en el centro?", "opts": ["Cero (0 N/C)", "k_e·q / r²", "3 · k_e·q / r²", "Campo infinito"], "ans": 0, "exp": "Por simetría de 120°, la suma vectorial de los 3 campos centrípetos/centrífugos en el centro es 0 N/C."},
        {"q": "¿Cómo se calcula la componente horizontal (Fx) de una fuerza F que forma un ángulo θ con el eje +X?", "opts": ["Fx = F · cos(θ)", "Fx = F · sen(θ)", "Fx = F / tan(θ)", "Fx = F · θ"], "ans": 0, "exp": "La proyección sobre el eje horizontal es Fx = F·cos(θ)."},
        {"q": "¿Cómo se calcula la componente vertical (Fy) de una fuerza F que forma un ángulo θ con el eje +X?", "opts": ["Fy = F · sen(θ)", "Fy = F · cos(θ)", "Fy = F / cos(θ)", "Fy = F · θ²"], "ans": 0, "exp": "La proyección sobre el eje vertical es Fy = F·sen(θ)."},
        {"q": "Una carga negativa -q ingresa a una región con campo E uniforme vertical hacia abajo. ¿Hacia dónde acelera?", "opts": ["Hacia ARRIBA (en sentido contrario al campo E)", "Hacia abajo (en el mismo sentido del campo E)", "No sufre aceleración", "Hacia la derecha perpendicularmente"], "ans": 0, "exp": "Dado que F = -q·E para carga negativa, la fuerza y aceleración son opuestas a E."},
        {"q": "¿Qué operador matemático relaciona el campo eléctrico E con el potencial V en una dimensión?", "opts": ["E = - dV / dx", "E = + dV / dx", "E = d²V / dx²", "E = V · x"], "ans": 0, "exp": "El campo eléctrico es el negativo de la derivada espacial (gradiente) del potencial: E = -dV/dx."},
        {"q": "Cuatro cargas iguales +q se fijan en los vértices de un cuadrado. ¿Cuánto vale E en el centro exacto?", "opts": ["Cero (0 N/C)", "4 · k_e·q / r²", "k_e·q / (2r²)", "Infinito"], "ans": 0, "exp": "Los 4 vectores diagonales opuestos se anulan por pares produciendo E = 0."},
        {"q": "Cuatro cargas iguales +q se fijan en las esquinas de un cuadrado de lado L. ¿El potencial V en el centro es cero?", "opts": ["No, V es positivo (V = 4 · k_e·q / r)", "Sí, V es cero por simetría", "V es negativo", "V es indeterminado"], "ans": 0, "exp": "El potencial es escalar. Al sumar 4 términos positivos V_i > 0, la suma es positiva."},
        {"q": "En el centro de un cuadrado de 4 cargas, ¿qué combinación de signos logra un potencial V = 0 Voltios?", "opts": ["Dos cargas positivas (+q) y dos negativas (-q)", "Las cuatro cargas positivas", "Tres cargas positivas y una negativa", "Ninguna combinación puede dar V = 0"], "ans": 0, "exp": "Al ser suma escalar, 2(+q) + 2(-q) se anulan dando V_total = 0 V."},
        {"q": "¿Qué forma tiene la trayectoria de una carga lanzada perpendicularmente a un campo E uniforme?", "opts": ["Parabólica", "Circular perfecta", "Rectilínea uniforme", "Sinusoidal pura"], "ans": 0, "exp": "Posee velocidad constante en un eje y aceleración constante en el otro, generando una parábola."},
        {"q": "¿Cuál es la expresión para la Energía Potencial Electrostática (U) entre dos cargas q1 y q2 a distancia r?", "opts": ["U = k_e · (q1 · q2) / r", "U = k_e · (q1 · q2) / r²", "U = k_e · (q1 + q2) / r", "U = q1 · q2 · r"], "ans": 0, "exp": "U = k_e · q1·q2 / r (nótese denominador r, no r²)."},
        {"q": "¿Qué significado físico tiene que la Energía Potencial (U) de un sistema de dos cargas sea POSITIVA (U > 0)?", "opts": ["Las cargas son del mismo signo y el sistema es repulsivo", "Las cargas son de distinto signo y se atraen", "El sistema no requiere trabajo externo", "Las cargas están en equilibrio nulo"], "ans": 0, "exp": "U > 0 resulta de q1·q2 > 0 (igual signo), indicando repulsión y trabajo almacenado."},
        {"q": "¿Qué significado físico tiene que la Energía Potencial (U) de un sistema sea NEGATIVA (U < 0)?", "opts": ["Las cargas son de signos opuestos y forman un sistema ligado atractivo", "Las cargas se repelen violentamente", "El sistema tiene masa cero", "La distancia r es negativa"], "ans": 0, "exp": "U < 0 ocurre con cargas de distinto signo, reflejando un estado atractivo ligado."},
        {"q": "En análisis dimensional, ¿cuáles son las dimensiones de la constante electrostática k_e en el SI?", "opts": ["[M L³ T⁻⁴ I⁻²]", "[M L T⁻²]", "[I T]", "[M L² T⁻³]"], "ans": 0, "exp": "Derivado de N·m²/C² = (kg·m/s²)·m² / (A·s)² = kg·m³·s⁻⁴·A⁻²."},
        {"q": "¿Cómo decae la intensidad del campo eléctrico E de un dipolo puntual a distancias grandes r >> d?", "opts": ["Decae como 1 / r³", "Decae como 1 / r²", "Decae como 1 / r", "Se mantiene constante"], "ans": 0, "exp": "A distancias lejanas r >> d, el campo de un dipolo decae inversamente con el cubo de la distancia (1/r³)."},
        {"q": "¿Cómo decae el potencial eléctrico V de un dipolo puntual a distancias grandes r >> d?", "opts": ["Decae como 1 / r²", "Decae como 1 / r³", "Decae como 1 / r", "Es independiente de r"], "ans": 0, "exp": "El potencial dipolar varía proporcionalmente a cos(θ)/r² a grandes distancias."},
        {"q": "Un electrón (carga e, masa m) acelera desde el reposo bajo una diferencia de potencial V. ¿Cuál es su velocidad v?", "opts": ["v = √(2 · e · V / m)", "v = e · V / m", "v = √(e · V · m)", "v = 2 · e · V · m"], "ans": 0, "exp": "De (1/2)m·v² = e·V se despeja v = √(2eV/m)."},
        {"q": "En un diagrama electrostático, ¿qué representa la densidad espacial de líneas de campo por unidad de área?", "opts": ["La magnitud del campo eléctrico |E| en esa región", "La cantidad de masa presente", "La velocidad de los fotones", "El valor de la constante k_e"], "ans": 0, "exp": "Donde las líneas están más juntas (mayor densidad), la intensidad del campo E es mayor."}
    ]
}

# --- HELPER: Preparar pregunta con opciones aleatorizadas ---
def prepare_shuffled_question(q_item):
    correct_text = q_item["opts"][q_item["ans"]]
    opts = list(q_item["opts"])
    random.shuffle(opts)
    new_ans = opts.index(correct_text)
    return {
        "q": q_item["q"],
        "opts": opts,
        "ans": new_ans,
        "exp": q_item["exp"]
    }

# --- HELPER: Preparar 8 preguntas al azar con opciones aleatorizadas ---
def get_random_8_questions(difficulty):
    pool = [prepare_shuffled_question(q) for q in PREGUNTAS_JUEGO[difficulty]]
    random.shuffle(pool)
    return pool[:8]

# ---------------------------------------------------------
# PESTAÑAS PRINCIPALES DE LA APLICACIÓN
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ 🧲 Fuerza y Campo Nulo", 
    "2️⃣ 📐 Presets Modificables", 
    "3️⃣ 🔍 Evaluador de Campo E",
    "4️⃣ 🎓 Modo Profe (Glosario & Juego)"
])

# ---------------------------------------------------------
# PESTAÑA 1: FUERZA Y CAMPO NULO
# ---------------------------------------------------------
with tab1:
    render_qr_expander()
    st.markdown("### 🧲 Ley de Coulomb y Calculadora de Punto Nulo (E = 0)")
    st.caption("Ajusta las cargas y marca la estrella dorada ⭐ del punto de campo nulo.")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("🔴 Carga 1")
        q1_v = st.slider("Valor Carga 1 (µC)", -10.0, 10.0, 5.0, 1.0, key="t1_q1_gloss")
        x1_v = st.slider("Posición X Carga 1 (m)", -4.0, 0.0, -2.0, 0.5, key="t1_x1_gloss")

    with col_c2:
        st.subheader("🔵 Carga 2")
        q2_v = st.slider("Valor Carga 2 (µC)", -10.0, 10.0, -5.0, 1.0, key="t1_q2_gloss")
        x2_v = st.slider("Posición X Carga 2 (m)", 0.0, 4.0, 2.0, 0.5, key="t1_x2_gloss")

    show_zero_pt = st.checkbox("⭐ Marcar en el gráfico el Punto de Campo Cero (E = 0)", value=True)

    c1 = Charge(q=q1_v*1e-6, x=x1_v, y=0.0, label=f"q1 ({q1_v} µC)")
    c2 = Charge(q=q2_v*1e-6, x=x2_v, y=0.0, label=f"q2 ({q2_v} µC)")
    charges_t1 = [c1, c2]

    zero_x = find_zero_field_point_1d(c1, c2) if show_zero_pt else None

    st.markdown("---")
    cg1, ce1 = st.columns([3, 2])

    with cg1:
        fig_f = plot_force_only_2d(charges_t1, bounds=6.0, zero_field_x=zero_x)
        st.plotly_chart(fig_f, use_container_width=True)

    with ce1:
        st.subheader("📊 Análisis Físico:")
        dist = abs(x2_v - x1_v)
        f_data = calculate_force_on_charge(0, charges_t1)
        F_val = f_data["F_total_mag"]

        mismo_s = (q1_v * q2_v) > 0
        tipo_t = "💥 **SE REPELEN**" if mismo_s else "🧲 **SE ATRAEN**"

        st.markdown(f"""
        <div class="info-box">
            <b>Distancia entre cargas (d):</b> {dist:.1f} m<br><br>
            <b>Comportamiento:</b> {tipo_t}<br><br>
            <b>Fuerza Resultante (F):</b> {F_val:.4f} N
        </div>
        """, unsafe_allow_html=True)

        if show_zero_pt:
            if zero_x is not None:
                st.success(f"⭐ **Punto de Campo Cero (E = 0)**: Ubicado en **X = {zero_x:.2f} m**")
            else:
                st.info("ℹ️ Para un dipolo idéntico (+q y -q), el punto E=0 se halla en el infinito.")

# ---------------------------------------------------------
# PESTAÑA 2: PRESETS MODIFICABLES
# ---------------------------------------------------------
with tab2:
    render_qr_expander()
    st.markdown("### 📐 Presets Ejercicios (Valores de Cargas Modificables)")
    col_p1, col_p2, col_p3 = st.columns(3)
    if "preset_actual" not in st.session_state:
        st.session_state.preset_actual = "Triángulo"

    with col_p1:
        if st.button("📐 Triángulo de 3 Cargas", use_container_width=True):
            st.session_state.preset_actual = "Triángulo"
    with col_p2:
        if st.button("⏹️ Cuadrado de 4 Cargas", use_container_width=True):
            st.session_state.preset_actual = "Cuadrado"
    with col_p3:
        if st.button("⭕ Anillo Hexagonal", use_container_width=True):
            st.session_state.preset_actual = "Anillo"

    preset_charges = []

    if st.session_state.preset_actual == "Triángulo":
        st.subheader("⚙️ Configurar Valores de Carga en el Triángulo:")
        cp1, cp2, cp3 = st.columns(3)
        q_t1 = cp1.slider("Carga Base Izq q1 (µC)", -10.0, 10.0, 4.0, 1.0)
        q_t2 = cp2.slider("Carga Base Der q2 (µC)", -10.0, 10.0, 4.0, 1.0)
        q_t3 = cp3.slider("Carga Vértice q3 (µC)", -10.0, 10.0, -4.0, 1.0)

        preset_charges = [
            Charge(q=q_t1*1e-6, x=-2.0, y=-1.5, label=f"q1 ({q_t1} µC)"),
            Charge(q=q_t2*1e-6, x=2.0, y=-1.5, label=f"q2 ({q_t2} µC)"),
            Charge(q=q_t3*1e-6, x=0.0, y=2.0, label=f"q3 ({q_t3} µC)")
        ]
    elif st.session_state.preset_actual == "Cuadrado":
        st.subheader("⚙️ Configurar Valores de Carga en el Cuadrado:")
        cp1, cp2, cp3, cp4 = st.columns(4)
        q_sq1 = cp1.slider("Carga Top-Izq q1 (µC)", -10.0, 10.0, 5.0, 1.0)
        q_sq2 = cp2.slider("Carga Top-Der q2 (µC)", -10.0, 10.0, -5.0, 1.0)
        q_sq3 = cp3.slider("Carga Bot-Izq q3 (µC)", -10.0, 10.0, -5.0, 1.0)
        q_sq4 = cp4.slider("Carga Bot-Der q4 (µC)", -10.0, 10.0, 5.0, 1.0)

        preset_charges = [
            Charge(q=q_sq1*1e-6, x=-2.0, y=2.0, label=f"q1 ({q_sq1} µC)"),
            Charge(q=q_sq2*1e-6, x=2.0, y=2.0, label=f"q2 ({q_sq2} µC)"),
            Charge(q=q_sq3*1e-6, x=-2.0, y=-2.0, label=f"q3 ({q_sq3} µC)"),
            Charge(q=q_sq4*1e-6, x=2.0, y=2.0, label=f"q4 ({q_sq4} µC)")
        ]
    elif st.session_state.preset_actual == "Anillo":
        q_ring = st.slider("Valor Cargas del Anillo Alternadas (µC)", 1.0, 10.0, 4.0, 1.0)
        for i in range(6):
            ang = i * (2 * np.pi / 6)
            q_v = q_ring*1e-6 if i % 2 == 0 else -q_ring*1e-6
            preset_charges.append(Charge(q=q_v, x=3.0*np.cos(ang), y=3.0*np.sin(ang), label=f"q{i+1}"))

    fig_preset = plot_2d_field_and_potential(preset_charges, grid_size=25, bounds=5.0)
    st.plotly_chart(fig_preset, use_container_width=True)

# ---------------------------------------------------------
# PESTAÑA 3: EVALUADOR DE CAMPO E
# ---------------------------------------------------------
with tab3:
    render_qr_expander()
    st.markdown("### 🔍 Evaluador de Campo Eléctrico (E) y Potencial (V)")
    col_e1_p, col_e2_p = st.columns([3, 2])

    with col_e2_p:
        st.subheader("📍 Punto de Prueba P(X, Y)")
        px_eval = st.slider("Coordenada X (m)", -4.0, 4.0, 1.0, 0.5)
        py_eval = st.slider("Coordenada Y (m)", -4.0, 4.0, 1.0, 0.5)

        eval_charges = [
            Charge(q=5e-6, x=-2.0, y=0.0, label="q1 (+5 µC)"),
            Charge(q=-5e-6, x=2.0, y=0.0, label="q2 (-5 µC)")
        ]

        pt_arr = np.array([px_eval, py_eval, 0.0])
        E_vec = calculate_electric_field_at_point(pt_arr, eval_charges)
        V_val = calculate_potential_at_point(pt_arr, eval_charges)
        E_mag = np.linalg.norm(E_vec)
        E_angle = np.degrees(np.arctan2(E_vec[1], E_vec[0])) % 360

        st.markdown(f"""
        <div class="info-box">
            <b>Punto evaluado:</b> P({px_eval:.1f}, {py_eval:.1f}) m<br><br>
            <b>Potencial Eléctrico (V):</b> {V_val:.2f} Volts<br><br>
            <b>Magnitud de Campo (|E|):</b> {E_mag:.2e} N/C<br><br>
            <b>Vector Campo (E):</b> ({E_vec[0]:.2e}, {E_vec[1]:.2e}) N/C<br><br>
            <b>Ángulo del Vector:</b> {E_angle:.1f}° respecto a +X
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("🚀 Lanzar Partícula en ese Punto")
        if st.button("🟢 ¡Lanzar Partícula desde P(X,Y)!", type="primary", use_container_width=True):
            traj = simulate_test_charge_trajectory(
                q0=2e-6, m0=1e-3,
                init_pos=[px_eval, py_eval, 0.0],
                init_vel=[3.0, 0.0, 0.0],
                fixed_charges=eval_charges,
                t_max=2.5, bounds=5.0
            )
            st.session_state.eval_traj = traj

        if "eval_traj" in st.session_state and st.session_state.eval_traj is not None:
            if st.button("🧹 Limpiar Partícula", use_container_width=True):
                st.session_state.eval_traj = None
                st.rerun()

    with col_e1_p:
        eval_charges = [
            Charge(q=5e-6, x=-2.0, y=0.0, label="q1 (+5 µC)"),
            Charge(q=-5e-6, x=2.0, y=0.0, label="q2 (-5 µC)")
        ]
        fig_eval = plot_2d_field_and_potential(
            charges=eval_charges, grid_size=25, bounds=5.0,
            trajectory=st.session_state.eval_traj["positions"] if ("eval_traj" in st.session_state and st.session_state.eval_traj) else None
        )
        st.plotly_chart(fig_eval, use_container_width=True)

# ---------------------------------------------------------
# PESTAÑA 4: MODO PROFE (GLOSARIO COMPLETO Y JUEGO 8 ESCALONES)
# ---------------------------------------------------------
with tab4:
    st.markdown("### 🎓 Modo Profe: Glosario de Definiciones & Juego de 8 Escalones")

    sub_tab_g, sub_tab_j = st.tabs(["📖 Glosario Completo de Definiciones de Física", "🏆 Juego: Desafío de 8 Escalones"])

    with sub_tab_g:
        st.subheader("📖 Glosario Didáctico de Definiciones Oficiales de Electrostática")
        st.caption("Diccionario conceptual completo con todas las definiciones, magnitudes, símbolos y fórmulas del programa académico de física.")

        st.markdown("---")

        with st.expander("📌 A - C: Carga, Campo y Coulomb", expanded=True):
            st.markdown(r"""
            - **Carga Eléctrica ($q$ o $Q$)**: Propiedad física intrínseca de la materia responsable de la interacción electromagnética. Unidad SI: **Coulomb ($\text{C}$)**.
            - **Carga Puntual**: Modelo idealizado de un cuerpo cargado cuyas dimensiones geométricas son despreciables frente a las distancias de análisis.
            - **Carga Elemental ($e$)**: Cantidad indivisible mínima de carga libre en la naturaleza. Valor: $e \approx 1.602176 \times 10^{-19} \text{ C}$.
            - **Campo Eléctrico ($\vec{E}$)**: Vector espacial que describe la fuerza por unidad de carga positiva colocada en un punto. $\vec{E} = \frac{\vec{F}}{q_0}$. Unidades: **$\text{N/C}$** o **$\text{V/m}$**.
            - **Constante de Coulomb ($k_e$)**: Factor de proporcionalidad en el vacío: $k_e = \frac{1}{4\pi\varepsilon_0} \approx 8.98755 \times 10^9 \text{ N}\cdot\text{m}^2/\text{C}^2$.
            - **Cuantización de la Carga**: Principio que establece que cualquier carga neta es un múltiplo entero de $e$: $q = n \cdot e$ ($n \in \mathbb{Z}$).
            - **Conservación de la Carga**: Principio según el cual la suma neta de cargas de un sistema aislado permanece constante: $\sum q_i = \text{cte}$.
            - **Conductores**: Materiales metálicos con alta densidad de electrones libres que permiten el flujo fácil de carga.
            """)

        with st.expander("📌 D - I: Dipolo, Electrización e Inducción"):
            st.markdown(r"""
            - **Dieléctricos / Aislantes**: Materiales no conductores cuyos electrones están fuertemente ligados a las moléculas.
            - **Dipolo Eléctrico**: Sistema formado por dos cargas de igual magnitud y signos opuestos ($+q$ y $-q$) separadas una distancia $d$.
            - **Electrización por Fricción**: Transferencia de electrones por rozamiento entre dos materiales neutros.
            - **Electrización por Conducción**: Flujo directo de electrones por contacto físico entre un cuerpo cargado y uno neutro.
            - **Inducción Electrostática**: Redistribución de carga por polarización en un cuerpo neutro mediante la aproximación sin contacto de una carga externa.
            - **Invariancia Relativista**: Propiedad de la carga eléctrica cuya magnitud permanece idéntica en cualquier sistema de referencia inercial.
            """)

        with st.expander("📌 L - P: Ley de Coulomb, Líneas de Campo y Potencial"):
            st.markdown(r"""
            - **Ley de Coulomb**: Enunciado formal: *La fuerza de atracción o repulsión entre dos cargas puntuales es directamente proporcional al producto de sus magnitudes e inversamente proporcional al cuadrado de la distancia que las separa.*
            - **Líneas de Campo Eléctrico**: Representación gráfica del flujo del campo. Nacen en cargas positivas ($+$), mueren en negativas ($-$) y jamás se cruzan.
            - **Permitividad del Vacío ($\varepsilon_0$)**: Constante dieléctrica del espacio libre: $\varepsilon_0 \approx 8.85418 \times 10^{-12} \text{ C}^2/\text{N}\cdot\text{m}^2$.
            - **Potencial Eléctrico ($V$)**: Magnitud escalar que mide la energía potencial por unidad de carga: $V = k_e \sum \frac{q_i}{r_i}$. Unidad: **Voltio ($\text{V} = \text{J/C}$)**.
            - **Principio de Superposición Vectorial**: La fuerza o campo neto sobre una carga es la suma vectorial de las contribuciones individuales: $\vec{F}_{\text{neto}} = \sum \vec{F}_i$.
            - **Punto de Campo Cero ($E=0$)**: Posición espacial donde la suma vectorial de todos los campos eléctricos se anula exactamente ($\vec{E}_{\text{neto}} = \vec{0}$).
            """)

        with st.expander("📌 S - W: Superficies Equipotenciales y Trabajo"):
            st.markdown(r"""
            - **Superficie Equipotencial**: Lugar geométrico en el espacio donde el potencial eléctrico $V$ es idéntico en todos sus puntos.
            - **Trabajo Electrostático ($W$)**: Trabajo realizado por el campo sobre una carga: $W_{a \to b} = -q \Delta V = q(V_a - V_b)$. Unidad: **Joule ($\text{J}$)**.
            - **Electrón-Voltio ($\text{eV}$)**: Unidad de energía equivalente a $1.602176 \times 10^{-19} \text{ J}$.
            """)

    # --- SUB-PESTAÑA JUEGO 8 ESCALONES ---
    with sub_tab_j:
        st.subheader("🏆 El Desafío de los 8 Escalones de Física")
        st.caption("¡Superá 8 preguntas seguidas sin fallar! En cada partida se seleccionan 8 preguntas distintas al azar del banco completo.")

        if "escalon" not in st.session_state:
            st.session_state.escalon = 0
        if "juego_dif" not in st.session_state:
            st.session_state.juego_dif = "Fácil"
        if "shuffled_questions" not in st.session_state:
            st.session_state.shuffled_questions = {}
            for dif in PREGUNTAS_JUEGO.keys():
                st.session_state.shuffled_questions[dif] = get_random_8_questions(dif)
        if "game_state" not in st.session_state: # "PLAYING", "SUCCESS", "GAME_OVER"
            st.session_state.game_state = "PLAYING"
        if "last_exp" not in st.session_state:
            st.session_state.last_exp = ""
        if "user_choice_text" not in st.session_state:
            st.session_state.user_choice_text = ""
        if "correct_choice_text" not in st.session_state:
            st.session_state.correct_choice_text = ""

        col_d1, col_d2 = st.columns([3, 1])
        with col_d1:
            dificultad = st.radio("🎯 Seleccionar Dificultad del Juego:", ["Fácil", "Medio", "Difícil"], horizontal=True)
        with col_d2:
            if st.button("🔀 Nuevas 8 Preguntas"):
                st.session_state.shuffled_questions[dificultad] = get_random_8_questions(dificultad)
                st.session_state.escalon = 0
                st.session_state.game_state = "PLAYING"
                st.rerun()

        if dificultad != st.session_state.juego_dif:
            st.session_state.juego_dif = dificultad
            st.session_state.shuffled_questions[dificultad] = get_random_8_questions(dificultad)
            st.session_state.escalon = 0
            st.session_state.game_state = "PLAYING"

        progreso = min(1.0, st.session_state.escalon / 8.0)
        st.progress(progreso, text=f"🪜 Progreso: Escalón {st.session_state.escalon} / 8 ({int(progreso * 100)}%)")

        if st.session_state.escalon >= 8:
            st.balloons()
            st.success("🎉 ¡FELICITACIONES! ¡HAS SUPERADO LOS 8 ESCALONES Y GANADO EL DESAFÍO! 🏆")
            if st.button("🔄 Jugar otra partida (Nuevas 8 Preguntas)", type="primary"):
                st.session_state.escalon = 0
                st.session_state.game_state = "PLAYING"
                st.session_state.shuffled_questions[st.session_state.juego_dif] = get_random_8_questions(st.session_state.juego_dif)
                st.rerun()

        elif st.session_state.game_state == "SUCCESS":
            st.success(f"🌟 **¡EXCELENTE!** Respuesta correcta. Avanzaste al Escalón {st.session_state.escalon} / 8.")
            st.info(f"💡 **Explicación Didáctica**: {st.session_state.last_exp}")
            if st.button(f"➡️ Continuar al Escalón {st.session_state.escalon + 1} de 8", type="primary", use_container_width=True):
                st.session_state.game_state = "PLAYING"
                st.rerun()

        elif st.session_state.game_state == "GAME_OVER":
            st.error(f"💥 **¡RESPUESTA INCORRECTA!** Caíste de vuelta al Escalón 0.")
            st.warning(f"❌ Tu respuesta fue: **{st.session_state.user_choice_text}**")
            st.success(f"✅ Respuesta correcta: **{st.session_state.correct_choice_text}**")
            st.info(f"💡 **Explicación**: {st.session_state.last_exp}")
            if st.button("🔄 Intentar de Nuevo (Nuevas 8 Preguntas)", type="primary", use_container_width=True):
                st.session_state.escalon = 0
                st.session_state.game_state = "PLAYING"
                st.session_state.shuffled_questions[st.session_state.juego_dif] = get_random_8_questions(st.session_state.juego_dif)
                st.rerun()

        else: # "PLAYING"
            preg_lista = st.session_state.shuffled_questions[st.session_state.juego_dif]
            curr_q = preg_lista[st.session_state.escalon % len(preg_lista)]

            st.markdown(f"""
            <div class="quiz-card">
                <div class="quiz-header">
                    <span class="step-badge">🪜 ESCALÓN {st.session_state.escalon + 1} DE 8</span>
                    <span class="diff-badge">🎯 DIFICULTAD: {st.session_state.juego_dif.upper()}</span>
                </div>
                <h3 style="color: #FFFFFF; font-size: 1.25rem; margin-top: 10px;">{curr_q['q']}</h3>
            </div>
            """, unsafe_allow_html=True)

            ans_choice = st.radio(
                "Elija la respuesta correcta:", 
                curr_q["opts"], 
                key=f"q_choice_{st.session_state.juego_dif}_{st.session_state.escalon}"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✅ Enviar Respuesta y Subir de Escalón", type="primary", use_container_width=True):
                selected_idx = curr_q["opts"].index(ans_choice)
                st.session_state.last_exp = curr_q["exp"]
                st.session_state.user_choice_text = ans_choice
                st.session_state.correct_choice_text = curr_q["opts"][curr_q["ans"]]

                if selected_idx == curr_q["ans"]:
                    st.session_state.escalon += 1
                    if st.session_state.escalon >= 8:
                        st.rerun()
                    else:
                        st.session_state.game_state = "SUCCESS"
                        st.rerun()
                else:
                    st.session_state.game_state = "GAME_OVER"
                    st.rerun()

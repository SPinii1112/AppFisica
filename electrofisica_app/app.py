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

    # URL pública (Streamlit Cloud) — funciona desde cualquier red
    cloud_url = st.text_input(
        "🌐 URL Pública (Streamlit Cloud):",
        placeholder="https://tu-app.streamlit.app",
        help="Pegá acá tu link de Streamlit Cloud para que el QR funcione desde cualquier red (ej: la Safa, la casa de un amigo, etc.)"
    )

    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:8501"

    # Elegir qué URL mostrar en el QR
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

# Estilos CSS
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
    .quiz-box {
        background-color: #1E2638;
        border: 2px solid #00FFCC;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
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
st.markdown('<div class="sub-title">Laboratorio Electrostático, Glosario Completo de Definiciones & Juego de 20 Escalones</div>', unsafe_allow_html=True)

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
# BANCO EXTENDIDO DE PREGUNTAS
# ---------------------------------------------------------
PREGUNTAS_JUEGO = {
    "Fácil": [
        {"q": "1. ¿Qué ocurre entre dos cargas eléctricas del MISMO signo?", "opts": ["Se repelen (se empujan hacia afuera)", "Se atraen", "No ejercen fuerza", "Se anulan"], "ans": 0, "exp": "Cargas del mismo signo (+ y + o - y -) se repelen."},
        {"q": "2. ¿En qué unidad del SI se mide la carga eléctrica?", "opts": ["Coulomb (C)", "Newton (N)", "Voltio (V)", "Joule (J)"], "ans": 0, "exp": "La unidad fundamental de carga es el Coulomb (C)."},
        {"q": "3. ¿Qué establece la propiedad de CUANTIZACIÓN de la carga?", "opts": ["La carga existe en múltiplos enteros de e (q = n·e)", "La carga puede ser decimal infinita", "La carga varía con la temperatura", "La carga depende del volumen"], "ans": 0, "exp": "La carga eléctrica aparece en paquetes discretos múltiplos de e = 1.602x10⁻¹⁹ C."},
        {"q": "4. Si la distancia entre dos cargas se DUPLICA (x2), ¿qué ocurre con la Fuerza?", "opts": ["Se reduce a la cuarta parte (F / 4)", "Se reduce a la mitad (F / 2)", "Se duplica (F x 2)", "Permanece constante"], "ans": 0, "exp": "La Ley de Coulomb es inversamente proporcional al cuadrado de la distancia (1/r²)."},
        {"q": "5. ¿Hacia dónde apuntan las líneas de Campo Eléctrico creadas por una carga POSITIVA?", "opts": ["Radiales hacia AFUERA (salientes)", "Radiales hacia ADENTRO (entrantes)", "En círculos cerrados", "No tienen dirección"], "ans": 0, "exp": "Las líneas salen de cargas positivas y entran a cargas negativas."},
        {"q": "6. ¿Qué partícula subatómica tiene carga eléctrica NEGATIVA?", "opts": ["Electrón", "Protón", "Neutrón", "Fotón"], "ans": 0, "exp": "El electrón posee carga negativa (-1.602x10⁻¹⁹ C)."},
        {"q": "7. ¿Qué partícula subatómica tiene carga eléctrica POSITIVA?", "opts": ["Protón", "Electrón", "Neutrón", "Gluón"], "ans": 0, "exp": "El protón posee carga positiva (+1.602x10⁻¹⁹ C)."},
        {"q": "8. ¿Qué ocurre entre dos cargas eléctricas de SIGNOS OPUESTOS?", "opts": ["Se atraen", "Se repelen", "No interactúan", "Se convierten en masa"], "ans": 0, "exp": "Cargas de signo opuesto (+ y -) se atraen mutuamente."},
        {"q": "9. ¿La carga del electrón y del protón tienen la misma magnitud?", "opts": ["Sí, valen 1.602 x 10⁻¹⁹ C pero signo opuesto", "No, el protón es 1000 veces mayor", "No, el electrón es mayor", "Depende del medio"], "ans": 0, "exp": "Tienen exactamente el mismo módulo pero signo inverso."},
        {"q": "10. ¿Cuál es el símbolo de la Constante de Coulomb?", "opts": ["k_e", "G", "c", "h"], "ans": 0, "exp": "Se denota k_e o simplemente k."},
        {"q": "11. ¿Qué instrumento clásico mide la presencia de carga eléctrica?", "opts": ["Electroscopio", "Voltímetro", "Amperímetro", "Manómetro"], "ans": 0, "exp": "El electroscopio detecta la presencia de carga por separación de láminas."},
        {"q": "12. Si una carga pasa de +3 µC a +6 µC a la misma distancia, ¿qué ocurre con la Fuerza?", "opts": ["Se DUPLICA (F x 2)", "Se cuadruplica", "Se reduce a la mitad", "No cambia"], "ans": 0, "exp": "La fuerza es directamente proporcional al valor de cada carga."},
        {"q": "13. ¿Puede existir una carga libre de 0.5 e (medio electrón)?", "opts": ["No, la carga está cuantizada en números enteros de e", "Sí, en cualquier cuerpo", "Sí, al calentarse", "Solo en sólidos"], "ans": 0, "exp": "En la naturaleza aislada n siempre es un número entero (n ∈ ℤ)."},
        {"q": "14. ¿Qué sucede con la carga neta de un sistema aislado en un proceso físico?", "opts": ["Se conserva (permanece constante)", "Aumenta", "Disminuye", "Se convierte en calor"], "ans": 0, "exp": "La Ley de Conservación establece ∑ q_i = constante."},
        {"q": "15. ¿Qué unidad es equivalente a 1 Voltio (V)?", "opts": ["1 Joule por Coulomb (J/C)", "1 Newton por Metro (N·m)", "1 Watt por Segundo (W/s)", "1 Coulomb por Segundo (C/s)"], "ans": 0, "exp": "1 Voltio representa 1 Joule de energía por cada Coulomb de carga (V = J/C)."},
        {"q": "16. ¿Un objeto neutro posee cargas eléctricas en su interior?", "opts": ["Sí, pero la cantidad de cargas + y - es exactamente igual", "No, no tiene electrones", "No, solo tiene neutrones", "Solo tiene masa"], "ans": 0, "exp": "Estar neutro significa balance igual de protones y electrones."},
        {"q": "17. ¿Cómo se llama al proceso de cargar un objeto acercándole otro cargado sin tocarlo?", "opts": ["Inducción electrostática", "Conducción", "Fricción", "Radiación"], "ans": 0, "exp": "Por inducción las cargas se redistribuyen por polarización sin contacto."},
        {"q": "18. ¿Cómo se llama al proceso de cargar un objeto frotándolo con otro?", "opts": ["Fricción o rozamiento", "Inducción", "Conducción", "Magnetización"], "ans": 0, "exp": "Por fricción se transfieren electrones de un material a otro."},
        {"q": "19. ¿Cuál es el prefijo de la unidad µC (microcoulomb)?", "opts": ["10⁻⁶ C (un millonésimo de Coulomb)", "10⁻³ C", "10⁻⁹ C", "10⁻¹² C"], "ans": 0, "exp": "1 µC = 1 x 10⁻⁶ Coulombs."},
        {"q": "20. ¿El Campo Eléctrico es una magnitud Escalar o Vectorial?", "opts": ["Vectorial (tiene magnitud, dirección y sentido)", "Escalar (solo número)", "Adimensional", "Variable continua"], "ans": 0, "exp": "El campo eléctrico E es una magnitud vectorial."}
    ],
    "Medio": [
        {"q": "1. ¿Cuál es la Constante de Coulomb (k_e) aproximada?", "opts": ["8.99 x 10⁹ N·m²/C²", "6.67 x 10⁻¹¹ N·m²/kg²", "3.00 x 10⁸ m/s", "1.60 x 10⁻¹⁹ C"], "ans": 0, "exp": "k_e ≈ 8.98755 x 10⁹ N·m²/C²."},
        {"q": "2. Si E = 0 en un punto, ¿cuál es la fuerza sobre una carga q colocada allí?", "opts": ["0 Newtons", "Infinita", "q x k", "Depende de la masa"], "ans": 0, "exp": "F = q·E. Si E = 0, F = 0 N."},
        {"q": "3. ¿Qué es una Superficie Equipotencial?", "opts": ["Lugar donde V es idéntico en todos sus puntos", "Donde E es infinito", "Donde F es máxima", "Región sin cargas"], "ans": 0, "exp": "En una superficie equipotencial el potencial escalar V es constante."},
        {"q": "4. Entre dos cargas de igual signo y valor, ¿dónde está el punto E = 0?", "opts": ["En el punto medio exacto entre ambas", "En el infinito", "Sobre la carga 1", "Sobre la carga 2"], "ans": 0, "exp": "Por simetría los campos opuestos de igual magnitud se anulan en el centro."},
        {"q": "5. ¿Cómo cortan las líneas de Campo E a las Superficies Equipotenciales?", "opts": ["Perpendicularmente (a 90°)", "Paralelamente (a 0°)", "A 45 grados", "Depende del signo"], "ans": 0, "exp": "Las líneas de campo siempre cruzan ortogonalmente (90°) las equipotenciales."},
        {"q": "6. ¿Qué representa la Permitividad del Vacío (ε_0)?", "opts": ["8.854 x 10⁻¹² C²/N·m²", "8.99 x 10⁹ N·m²/C²", "1.60 x 10⁻¹⁹ C", "9.81 m/s²"], "ans": 0, "exp": "ε_0 es la constante de permitividad eléctrica del espacio libre."},
        {"q": "7. Si acortamos la distancia entre 2 cargas a la MITAD (r / 2), ¿qué ocurre con la Fuerza?", "opts": ["Se CUADRUPLICA (F x 4)", "Se duplica", "Se reduce a la mitad", "Se reduce a la cuarta parte"], "ans": 0, "exp": "F ∝ 1/(1/2)² = 4. La fuerza aumenta 4 veces."},
        {"q": "8. ¿El Potencial Eléctrico V es un escalar o un vector?", "opts": ["Escalar (solo requiere un valor numérico y signo)", "Vectorial", "Matriz 3x3", "Sin dimensión"], "ans": 0, "exp": "El potencial V es una magnitud escalar (J/C = V)."},
        {"q": "9. ¿Qué relación hay entre k_e y ε_0?", "opts": ["k_e = 1 / (4 · π · ε_0)", "k_e = 4 · π · ε_0", "k_e = ε_0 / c", "k_e = ε_0²"], "ans": 0, "exp": "k_e = 1 / (4π ε_0)."},
        {"q": "10. ¿Qué trabajo se realiza al mover una carga sobre una misma línea equipotencial?", "opts": ["Cero Joules (0 J)", "W = q · V", "W = F · r²", "Infinito"], "ans": 0, "exp": "Dado que ΔV = 0 en la misma equipotencial, W = -q ΔV = 0 J."},
        {"q": "11. ¿En qué unidad se mide el prefijo nC (nanocoulomb)?", "opts": ["10⁻⁹ Coulombs", "10⁻⁶ Coulombs", "10⁻¹² Coulombs", "10⁻³ Coulombs"], "ans": 0, "exp": "1 nC = 1 x 10⁻⁹ C."},
        {"q": "12. ¿Qué ocurre con el Campo Eléctrico en el interior de un conductor en equilibrio electrostático?", "opts": ["Es exactamente CERO (E = 0)", "Es infinito", "Aumenta hacia el centro", "Es negativo"], "ans": 0, "exp": "En equilibrio electrostático las cargas se mueven a la superficie dejando E = 0 adentro (jaula de Faraday)."},
        {"q": "13. ¿Hacia dónde se mueve espontáneamente una carga POSITIVA libre?", "opts": ["Hacia regiones de MENOR potencial V", "Hacia regiones de mayor potencial V", "Se queda quieta", "En círculos"], "ans": 0, "exp": "Las cargas positivas aceleran espontáneamente desde alto potencial (+) hacia bajo potencial (-)."},
        {"q": "14. ¿Hacia dónde se mueve espontáneamente una carga NEGATIVA libre?", "opts": ["Hacia regiones de MAYOR potencial V", "Hacia menor potencial V", "Hacia la nada", "No se mueve"], "ans": 0, "exp": "Las cargas negativas sufren fuerza opuesta al campo y van hacia mayor potencial."},
        {"q": "15. ¿Cómo se define el vector unitario r_hat en la Ley de Coulomb?", "opts": ["Un vector de magnitud 1 que señala la dirección de la línea de acción", "Un vector de 10 metros", "El valor del radio", "Una constante adimensional sin sentido"], "ans": 0, "exp": "r_hat = r_vec / |r_vec| sirve únicamente para dar dirección vectorial."},
        {"q": "16. Si 2 cargas positivas (+q y +4q) están a 3 m, ¿el punto E=0 está más cerca de cuál carga?", "opts": ["De la carga menor (+q)", "De la carga mayor (+4q)", "Justo en el centro", "En el infinito"], "ans": 0, "exp": "Para compensar el menor valor de q, debe estar más cerca de la carga más pequeña."},
        {"q": "17. ¿Qué representa la aceleración a de una partícula cargada q con masa m en un campo E?", "opts": ["a = (q · E) / m", "a = q · m / E", "a = E / (q · m)", "a = q · E · m"], "ans": 0, "exp": "De F = m·a y F = q·E se obtiene a = (q·E)/m (2da Ley de Newton)."},
        {"q": "18. ¿Qué es un Dipolo Eléctrico?", "opts": ["Un sistema de dos cargas de igual magnitud pero signos opuestos (+q y -q)", "Dos cargas positivas", "Tres cargas neutras", "Un átomo de helio"], "ans": 0, "exp": "Un dipolo consta de un par +q y -q separadas por una distancia pequeña d."},
        {"q": "19. ¿Cuál es el momento dipolar eléctrico p de dos cargas (+q y -q) separadas d?", "opts": ["p = q · d", "p = q / d", "p = q² · d", "p = k · q / d²"], "ans": 0, "exp": "El momento dipolar escalar se define como p = q · d."},
        {"q": "20. ¿El potencial eléctrico V alrededor de una carga puntual positiva es positivo o negativo?", "opts": ["Positivo (V > 0)", "Negativo (V < 0)", "Cero", "Imaginario"], "ans": 0, "exp": "V = k_e q / r. Si q > 0, V > 0."}
    ],
    "Difícil": [
        {"q": "1. ¿Qué es el Principio de SUPERPOSICIÓN de Fuerzas Eléctricas?", "opts": ["La fuerza total es la SUMA VECTORIAL de las fuerzas individuales", "Es el promedio escalar", "Es el producto de las cargas", "La masa dicta la fuerza"], "ans": 0, "exp": "F_total = ∑ F_i por adición vectorial de componentes."},
        {"q": "2. Entre cargas de SIGNOS OPUESTOS de distinta magnitud (|q1| < |q2|), ¿dónde está el punto E=0?", "opts": ["Fuera del segmento, del lado de la carga MENOR (|q1|)", "En el centro entre ellas", "Fuera del segmento, del lado de la carga mayor", "No existe"], "ans": 0, "exp": "Fuera del segmento los vectores de campo apuntan en sentidos opuestos y se cancelan más cerca de la carga menor."},
        {"q": "3. ¿Qué relación hay entre el Trabajo W del campo y el cambio de Potencial ΔV?", "opts": ["W = -q · ΔV", "W = q · E²", "W = k · q / r", "W = F · r²"], "ans": 0, "exp": "W_conservativo = -ΔU = -q ΔV."},
        {"q": "4. Tres cargas iguales +q en los vértices de un triángulo equilátero. ¿Cuánto vale E en el centro?", "opts": ["Cero (0 N/C)", "k·q/r²", "3 k·q/r²", "Infinito"], "ans": 0, "exp": "Por simetría angular de 120°, la suma vectorial de los 3 campos en el centro es 0 N/C."},
        {"q": "5. ¿Cómo se calcula la componente Fx de una fuerza F con ángulo θ?", "opts": ["Fx = F · cos(θ)", "Fx = F · sen(θ)", "Fx = F / tan(θ)", "Fx = F · θ"], "ans": 0, "exp": "La proyección horizontal sobre el eje X es Fx = F cos(θ)."},
        {"q": "6. ¿Cómo se calcula la componente Fy de una fuerza F con ángulo θ?", "opts": ["Fy = F · sen(θ)", "Fy = F · cos(θ)", "Fy = F / cos(θ)", "Fy = F · θ²"], "ans": 0, "exp": "La proyección vertical sobre el eje Y es Fy = F sen(θ)."},
        {"q": "7. Si una partícula de masa m y carga -q entra paralela a un campo E vertical hacia abajo, ¿hacia dónde acelera?", "opts": ["Hacia ARRIBA (en sentido contrario a E)", "Hacia abajo", "No acelera", "Hacia la derecha"], "ans": 0, "exp": "Como la carga es negativa, la fuerza F = -q E actúa en sentido opuesto a E (hacia arriba)."},
        {"q": "8. ¿Cuál es el gradiente de potencial que se relaciona con el Campo Eléctrico E en 1D?", "opts": ["E = - dV / dx", "E = + dV / dx", "E = d²V / dx²", "E = V · x"], "ans": 0, "exp": "El campo eléctrico es el negativo del gradiente del potencial espacial: E = -dV/dx."},
        {"q": "9. Cuatro cargas iguales (+q) en las 4 esquinas de un cuadrado. ¿Cuánto vale E en el centro exacto?", "opts": ["Cero (0 N/C)", "4 k q / r²", "k q / (2r²)", "Infinito"], "ans": 0, "exp": "Los 4 vectores diagonales opuestos se anulan dos a dos dejando E = 0."},
        {"q": "10. Cuatro cargas iguales (+q) en las 4 esquinas de un cuadrado de lado L. ¿El potencial V en el centro es CERO?", "opts": ["No, V es positivo (V = 4 k q / r)", "Sí, V es cero", "V es negativo", "V es infinito"], "ans": 0, "exp": "El potencial es escalar. Al ser 4 cargas positivas, sus valores V se suman dando V = 4 k q / r > 0."},
        {"q": "11. ¿En qué caso el potencial escalar V en el centro de un cuadrado es CERO?", "opts": ["Cuando dos cargas son +q y dos cargas son -q", "Cuando las 4 son positivas", "Cuando 3 son positivas", "Nunca puede ser cero"], "ans": 0, "exp": "Al ser escalar, la suma 2(+q) + 2(-q) da V_total = 0 Voltios."},
        {"q": "12. ¿Qué trayectoria describe una carga q lanzada perpendicularmente dentro de un campo E uniforme?", "opts": ["Parabólica (análogo al tiro parabólico gravitatorio)", "Circular perfecta", "Rectilínea uniforme", "Sinusoidal"], "ans": 0, "exp": "Velocidad constante en X y aceleración constante en Y genera trayectoria parabólica."},
        {"q": "13. ¿Cuál es la energía potencial eléctrica U de dos cargas q1 y q2 separadas r?", "opts": ["U = k_e · (q1 · q2) / r", "U = k_e · (q1 · q2) / r²", "U = k_e · (q1 + q2) / r", "U = q1 · q2 · r"], "ans": 0, "exp": "U = k_e (q1 q2) / r (nótese el denominador r, no r²)."},
        {"q": "14. ¿Qué ocurre si la energía potencial U entre 2 cargas es POSITIVA (U > 0)?", "opts": ["El sistema es repulsivo y requiere trabajo para juntarlas", "El sistema se atrae solo", "Las cargas son de signo opuesto", "No hay fuerza"], "ans": 0, "exp": "U > 0 ocurre cuando q1 y q2 tienen igual signo (repulsión)."},
        {"q": "15. ¿Qué ocurre si la energía potencial U entre 2 cargas es NEGATIVA (U < 0)?", "opts": ["El sistema es ligado/atractivo (cargas de signo opuesto)", "Se repelen fuertemente", "La masa es cero", "U es imaginario"], "ans": 0, "exp": "U < 0 ocurre con cargas de signo opuesto (atracción en estado ligado)."},
        {"q": "16. ¿Qué dimensión física tiene la constante de Coulomb k_e?", "opts": ["[M L³ T⁻⁴ I⁻²]", "[M L T⁻²]", "[I T]", "[M L² T⁻³]"], "ans": 0, "exp": "N·m²/C² expresado en unidades fundamentales del SI."},
        {"q": "17. ¿Cómo varía la intensidad del campo E de un dipolo puntual a distancias r grandes?", "opts": ["Varía como 1 / r³", "Varía como 1 / r²", "Varía como 1 / r", "Es constante"], "ans": 0, "exp": "A distancias grandes r >> d, el campo dipolar disminuye proporcionalmente a 1/r³."},
        {"q": "18. ¿Cómo varía el potencial V de un dipolo puntual a distancias r grandes?", "opts": ["Varía como 1 / r²", "Varía como 1 / r³", "Varía como 1 / r", "Es constante"], "ans": 0, "exp": "El potencial dipolar decae como 1/r² a grandes distancias."},
        {"q": "19. ¿Qué velocidad v adquiere un electrón (masa m, carga e) acelerado desde el reposo por una diferencia de potencial V?", "opts": ["v = √(2 · e · V / m)", "v = e · V / m", "v = √(e · V · m)", "v = 2 e V m"], "ans": 0, "exp": "De la conservación de energía: (1/2) m v² = e V ⇒ v = √(2eV/m)."},
        {"q": "20. ¿Qué se entiende por la densidad del flujo de líneas de campo eléctrico en una región?", "opts": ["Proporcional a la magnitud |E| del campo eléctrico en esa región", "La masa por unidad de volumen", "La velocidad de los fotones", "El número de cargas libres"], "ans": 0, "exp": "A mayor densidad de líneas dibujadas por unidad de área, mayor es la intensidad del campo E."}
    ]
}

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
            Charge(q=q_sq4*1e-6, x=2.0, y=-2.0, label=f"q4 ({q_sq4} µC)")
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
# PESTAÑA 4: MODO PROFE (GLOSARIO COMPLETO Y JUEGO 20 ESCALONES)
# ---------------------------------------------------------
with tab4:
    st.markdown("### 🎓 Modo Profe: Glosario de Definiciones & Juego de 20 Escalones")

    sub_tab_g, sub_tab_j = st.tabs(["📖 Glosario Completo de Definiciones de Física", "🏆 Juego: Desafío 20 Escalones"])

    # --- SUB-PESTAÑA GLOSARIO COMPLETO Y EXPLICITO DE DEFINICIONES ---
    with sub_tab_g:
        st.subheader("📖 Glosario Didáctico de Definiciones Oficiales de Electrostática")
        st.caption("Diccionario conceptual completo con todas las definiciones, magnitudes, símbolos y fórmulas del programa académico de física.")

        st.markdown("---")

        # GLOSARIO A-Z ORGANIZADO
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

    # --- SUB-PESTAÑA JUEGO ESCALERA ---
    with sub_tab_j:
        st.subheader("🏆 El Desafío de los 20 Escalones de Física")
        st.caption("¡Supera 20 preguntas sin fallar! Si te equivocas en una sola respuesta, caes de vuelta al Escalón 0.")

        if "escalon" not in st.session_state:
            st.session_state.escalon = 0
        if "juego_dif" not in st.session_state:
            st.session_state.juego_dif = "Fácil"
        if "shuffled_questions" not in st.session_state:
            st.session_state.shuffled_questions = {}
            for dif, lista in PREGUNTAS_JUEGO.items():
                shuffled = list(lista)
                random.shuffle(shuffled)
                st.session_state.shuffled_questions[dif] = shuffled
        if "game_over" not in st.session_state:
            st.session_state.game_over = False
        if "feedback_msg" not in st.session_state:
            st.session_state.feedback_msg = ""

        col_d1, col_d2 = st.columns([3, 1])
        with col_d1:
            dificultad = st.radio("🎯 Dificultad del Juego:", ["Fácil", "Medio", "Difícil"], horizontal=True)
        with col_d2:
            if st.button("🔀 Mezclar Preguntas"):
                shuffled = list(PREGUNTAS_JUEGO[dificultad])
                random.shuffle(shuffled)
                st.session_state.shuffled_questions[dificultad] = shuffled
                st.session_state.escalon = 0
                st.session_state.game_over = False
                st.rerun()

        if dificultad != st.session_state.juego_dif:
            st.session_state.juego_dif = dificultad
            st.session_state.escalon = 0
            st.session_state.game_over = False
            st.session_state.feedback_msg = ""

        progreso = min(1.0, st.session_state.escalon / 20.0)
        st.progress(progreso, text=f"🪜 Escalón Actual: {st.session_state.escalon} / 20")

        if st.session_state.escalon >= 20:
            st.balloons()
            st.success("🎉 ¡FELICITACIONES! HAS LLEGADO AL ESCALÓN 20 Y GANADO EL JUEGO PROFE! 🏆")
            if st.button("🔄 Jugar de nuevo"):
                st.session_state.escalon = 0
                st.session_state.game_over = False
                st.rerun()
        elif st.session_state.game_over:
            st.error("💥 ¡RESPUESTA INCORRECTA! CAÍSTE AL ESCALÓN 0.")
            st.warning(st.session_state.feedback_msg)
            if st.button("🔄 Intentar de nuevo desde Escalón 0", type="primary"):
                st.session_state.escalon = 0
                st.session_state.game_over = False
                st.session_state.feedback_msg = ""
                st.rerun()
        else:
            preg_lista = st.session_state.shuffled_questions[st.session_state.juego_dif]
            curr_q = preg_lista[st.session_state.escalon % len(preg_lista)]

            st.markdown(f"""
            <div class="quiz-box">
                <h4><b>Escalón {st.session_state.escalon + 1} (Dificultad: {st.session_state.juego_dif})</b></h4>
                <p style="font-size: 1.2rem;">{curr_q['q']}</p>
            </div>
            """, unsafe_allow_html=True)

            ans_choice = st.radio("Selecciona tu respuesta:", curr_q["opts"], key=f"q_choice_{st.session_state.escalon}")

            if st.button("✅ Responder e Intentar Subir", type="primary"):
                selected_idx = curr_q["opts"].index(ans_choice)
                if selected_idx == curr_q["ans"]:
                    st.session_state.escalon += 1
                    st.success(f"¡CORRECTO! Subiste al escalón {st.session_state.escalon} 🪜✨")
                    st.info(f"💡 **Explicación**: {curr_q['exp']}")
                    st.rerun()
                else:
                    st.session_state.game_over = True
                    st.session_state.feedback_msg = f"Explicación: {curr_q['exp']}"
                    st.rerun()

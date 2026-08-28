import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    ip = get_local_ip()
    print("=" * 60)
    print(" 📱 ¡CÓMO USAR LA APP EN TU CELULAR (ANDROID / IPHONE)!")
    print("=" * 60)
    print()
    print("1. Conecta tu celular a la misma red Wi-Fi que la PC.")
    print("2. Abre Chrome o Safari en tu celular y escribe:")
    print()
    print(f"   👉  http://{ip}:8501")
    print()
    print("3. ¡Listo! Verás la app de física en tu celular.")
    print("   Tip: Toca 'Agregar a pantalla de inicio' en tu celular para tenerla")
    print("   como si fuera una App nativa con icono.")
    print("=" * 60)

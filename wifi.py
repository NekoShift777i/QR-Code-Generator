"""Формирование данных подключения к Wi-Fi для QR-кода."""


def build_wifi_string(
    ssid: str,
    password: str,
    security: str = "WPA2-Personal",
    hidden: bool = False
) -> str:
    def escape_value(value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace(";", r"\;")
            .replace(",", r"\,")
            .replace(":", r"\:")
            .replace('"', r"\"")
        )
        
    security_normalized = security.strip().lower()
    
    if security_normalized in {"wpa2-personal", "wpa3-personal", "wpa", "wpa2", "wpa3"}:
        qr_security = "WPA"
    elif security_normalized in {"nopass", "none", "open", "открытая", "открытая сеть"}:
        qr_security = "nopass"
    else:
        raise ValueError(
            "Поддерживаются только WPA2-Personal, WPA3-Personal, Открытая сеть"
        )
        
    if not ssid.strip():
        raise ValueError("SSID не может быть пустым")
        
    if qr_security != "nopass" and not password:
        raise ValueError("Пароль не может быть пустым для защищённой сети.")
        
    ssid_escaped = escape_value(ssid)
    password_escaped = escape_value(password)
    hidden_str = "True" if hidden else "false"
    
    if qr_security == "nopass":
        return f"WIFI:T:{qr_security};S:{ssid_escaped};H:{hidden_str};;"
        
    return (
        f"WIFI:T:{qr_security};"
        f"S:{ssid_escaped};"
        f"P:{password_escaped};"
        f"H:{hidden_str};;"
    )

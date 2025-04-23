from Crypto.Cipher import AES
import base64

ds = "OSnaALIWUkpOziVAMycaZQ=="
encrypted = base64.b64decode(ds)

def decrypt(key_int):
    key_bytes = bytearray(16)
    key_str = str(key_int).encode('utf-8')
    key_bytes[:len(key_str)] = key_str[:16]
    cipher = AES.new(bytes(key_bytes), AES.MODE_ECB)
    try:
        decrypted = cipher.decrypt(encrypted).decode('utf-8').strip()
        return decrypted
    except:
        return None  # Ignora errores de decodificación

for key in range(100, 1000):
    result = decrypt(key)
    if result:
        print(f"Key: {key}, Decrypted: {result}")  # Solo imprime si se pudo descifrar
        if result == "master_on":
            print(f"✔️ Clave válida encontrada: {key}")
            break

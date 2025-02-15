import cv2
from pyzbar.pyzbar import decode
import time
import db_python

# Configuración de la cámara
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Ancho del frame
cap.set(4, 480)  # Alto del frame

# Conjunto para almacenar códigos ya utilizados
used_codes = set()

# Bucle principal
while True:
    success, frame = cap.read()
    if not success:
        print("Error: No se puede leer el frame")
        break

    # Preprocesamiento de la imagen (opcional)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

    # Detección de códigos de barras
    for code in decode(binary):  # Puedes usar 'frame' en lugar de 'binary' si no aplicas preprocesamiento
        decoded_data = code.data.decode('utf-8')
        if decoded_data not in used_codes:
            print('Código aprobado. Presiona enter')
            print(decoded_data)
            used_codes.add(decoded_data)

            # Insertar en la base de datos
            if db_python.insert_code(decoded_data):
                print("Código insertado en la base de datos")
            else:
                print("Error al insertar el código en la base de datos")

            time.sleep(1)  # Esperar 1 segundo antes de permitir otro escaneo
        else:
            print('Lo sentimos, este código ya ha sido utilizado')
            time.sleep(1)

    # Mostrar el frame en una ventana
    cv2.imshow('Testing-code-scan', frame)

    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar ventanas
cap.release()
cv2.destroyAllWindows()

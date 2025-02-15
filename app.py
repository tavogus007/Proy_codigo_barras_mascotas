from flask import Flask, jsonify, request
from flask_cors import CORS  # Importar Flask-CORS
import psycopg2
import cv2
from pyzbar.pyzbar import decode
import threading
import time

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

DATABASE_URL = "postgresql://postgres:dante095065@localhost/bd_registro_mascotas"

# Variable global para almacenar el resultado del escaneo
scan_result = None

def get_all_codes():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, informacion, tiempo FROM codigo")
        rows = cur.fetchall()
        return [{"id": row[0], "informacion": row[1], "tiempo": row[2].isoformat()} for row in rows]
    except Exception as e:
        print(f"Error al recuperar datos de la base de datos: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def scan_barcode():
    global scan_result
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # Ancho del frame
    cap.set(4, 480)  # Alto del frame

    used_codes = set()

    while True:
        success, frame = cap.read()
        if not success:
            print("Error: No se puede leer el frame")
            scan_result = "Error: No se puede leer el frame"
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

        for code in decode(binary):
            decoded_data = code.data.decode('utf-8')
            if decoded_data not in used_codes:
                print('Código aprobado. Presiona enter')
                print(decoded_data)
                used_codes.add(decoded_data)

                # Insertar en la base de datos
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                try:
                    cur.execute("INSERT INTO codigo (informacion) VALUES (%s)", (decoded_data,))
                    conn.commit()
                    scan_result = decoded_data  # Almacenar el resultado
                except Exception as e:
                    print(f"Error al insertar el código en la base de datos: {e}")
                    scan_result = "Error al insertar el código"
                finally:
                    cur.close()
                    conn.close()

                time.sleep(1)
                cap.release()
                cv2.destroyAllWindows()
                return  # Terminar la función después de escanear

        cv2.imshow('Testing-code-scan', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    scan_result = "Error: No se pudo escanear el código"

@app.route('/api/codigo', methods=['GET'])
def codigo():
    codes = get_all_codes()
    return jsonify(codes)

@app.route('/api/codigo/scan', methods=['POST'])
def start_scan():
    global scan_result
    scan_result = None  # Reiniciar el resultado

    # Ejecutar el escaneo en un hilo separado
    threading.Thread(target=scan_barcode).start()

    # Esperar a que el escaneo termine
    while scan_result is None:
        time.sleep(0.1)

    return jsonify({"result": scan_result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
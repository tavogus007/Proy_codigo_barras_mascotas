import psycopg2
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, TIMESTAMP
import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde un archivo .env

# Usar variables de entorno para la conexión a la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dante095065@localhost/bd_registro_mascotas")
engine = create_engine(DATABASE_URL)
metadata = MetaData()

codigo_table = Table('codigo', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('informacion', String),
                     Column('tiempo', TIMESTAMP)
                     )

def insert_code(informacion):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO codigo (informacion) VALUES (%s)", (informacion,))
        conn.commit()
        return True  # Inserción exitosa
    except Exception as e:
        print(f"Error al insertar en la base de datos: {e}")
        return False  # Inserción fallida
    finally:
        cur.close()
        conn.close()
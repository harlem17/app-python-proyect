from fastapi import FastAPI, Request
from fastapi import Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conéctate a la base de datos SQLite
conn = sqlite3.connect('nonprofitorganization.db')
cursor = conn.cursor()

# Crea una tabla para almacenar voluntarios si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS voluntarios (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        telefono INTEGER NOT NULL,
        intereses TEXT
    )
''')

# Crea una tabla para almacenar programas si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS programas (
        nombre TEXT PRIMARY KEY,
        descripcion TEXT
    )
''')

# Crea una tabla para relacionar voluntarios y programas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS programa_voluntario (
        programa_id TEXT,
        voluntario_id INTEGER,
        FOREIGN KEY (programa_id) REFERENCES programas (nombre),
        FOREIGN KEY (voluntario_id) REFERENCES voluntarios (id)
    )
''')

conn.commit()
conn.close()

# Ruta para mostrar la página principal
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('Home.html', {"request": request})

# Ruta para registrar un voluntario
@app.post('/create-voluntario', response_class=JSONResponse)
async def add_voluntario(ID: int = Form(...), Nombre: str = Form(...), Apellido: str = Form(...), Telefono: int = Form(...), Intereses: str = Form(...)):
    try:
        conn = sqlite3.connect('nonprofitorganization.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO voluntarios (id, nombre, apellido, telefono, intereses) VALUES (?, ?, ?, ?, ?)', (ID, Nombre, Apellido, Telefono, Intereses))
        conn.commit()
        conn.close()
        print("Voluntario agregado con éxito")
        return JSONResponse(content={"mensaje": "Voluntario agregado con éxito"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para eliminar voluntario por ID
@app.delete('/eliminar-voluntario', response_class=JSONResponse)
async def delete_voluntario(ID: int = Form(...)):
    try:
        conn = sqlite3.connect('nonprofitorganization.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM voluntarios WHERE id = ?', (ID,))
        conn.commit()
        conn.close()
        print("Voluntario eliminado con éxito")
        return JSONResponse(content={"mensaje": "Voluntario eliminado con éxito"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para registrar un programa
@app.post('/create-programa', response_class=JSONResponse)
async def add_programa(nombre: str = Form(...), descripcion: str = Form(...)):
    try:
        conn = sqlite3.connect('nonprofitorganization.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO programas (nombre, descripcion) VALUES (?, ?)', (nombre, descripcion))
        conn.commit()
        conn.close()
        print("Programa agregado con éxito")
        return JSONResponse(content={"mensaje": "Programa agregado con éxito"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para que los voluntarios se unan a un programa
@app.post('/unirse-programa', response_class=JSONResponse)
async def unirse_programa(nombre_programa: str = Form(...), voluntario_id: int = Form(...)):
    try:
        conn = sqlite3.connect('nonprofitorganization.db')
        cursor = conn.cursor()

        # Verificar si el voluntario existe
        cursor.execute('SELECT * FROM voluntarios WHERE id = ?', (voluntario_id,))
        voluntario = cursor.fetchone()

        # Verificar si el programa existe
        cursor.execute('SELECT * FROM programas WHERE nombre = ?', (nombre_programa,))
        programa = cursor.fetchone()

        conn.close()

        if voluntario and programa:
            # Ambos existen, ahora realiza la unión
            conn = sqlite3.connect('nonprofitorganization.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO programa_voluntario (programa_id, voluntario_id) VALUES (?, ?)', (programa[0], voluntario[0]))
            conn.commit()
            conn.close()
            print("Voluntario agregado al programa con éxito")
            return JSONResponse(content={"mensaje": "Voluntario agregado al programa con éxito"}, status_code=200)
        else:
            print("Programa o voluntario no encontrado")
            return JSONResponse(content={"mensaje": "Programa o voluntario no encontrado"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para eliminar programa por Nombre
@app.delete('/eliminar-programa', response_class=JSONResponse)
async def delete_programa(Nombre: str = Form(...)):
    try:
        conn = sqlite3.connect('nonprofitorganization.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM programas WHERE nombre = ?', (Nombre,))
        conn.commit()
        conn.close()
        print("Programa eliminado con éxito")
        return JSONResponse(content={"mensaje": "Programa eliminado con éxito"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para mostrar todos los voluntarios
@app.get('/voluntarios', response_class=JSONResponse)
async def mostrar_voluntarios():
    try:
        conn = sqlite3.connect('nonprofitorganization.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM voluntarios')
        result = cursor.fetchall()
        voluntarios = [{"ID": row[0], "Nombre": row[1], "Apellido": row[2], "Telefono": row[3], "Intereses": row[4]} for row in result]
        conn.close()
        return JSONResponse(content={"voluntarios": voluntarios}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para mostrar todos los programas con voluntarios
@app.get('/programas', response_class=JSONResponse)
async def mostrar_programas():
    try:
        conn = sqlite3.connect('nonprofitorganization.db')
        cursor = conn.cursor()

        # Consulta para obtener la información de los programas y los voluntarios asociados
        cursor.execute('''
            SELECT p.nombre, p.descripcion, v.id, v.nombre as nombre_voluntario, v.apellido as apellido_voluntario, v.telefono, v.intereses
            FROM programas p
            LEFT JOIN programa_voluntario pv ON p.rowid = pv.programa_id
            LEFT JOIN voluntarios v ON pv.voluntario_id = v.rowid
        ''')
        
        result = cursor.fetchall()
        programas = {}

        for row in result:
            nombre_programa = row[0]
            descripcion_programa = row[1]
            if nombre_programa not in programas:
                programas[nombre_programa] = {
                    "descripcion": descripcion_programa,
                    "voluntarios": []
                }
            if row[2] is not None:
                voluntario = {
                    "ID": row[2],
                    "Nombre": row[3],
                    "Apellido": row[4],
                    "Telefono": row[5],
                    "Intereses": row[6]
                }
                programas[nombre_programa]["voluntarios"].append(voluntario)

        conn.close()
        return JSONResponse(content={"programas": programas}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)

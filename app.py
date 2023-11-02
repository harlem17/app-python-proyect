from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Esto permite solicitudes desde cualquier origen
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

conn.commit()
conn.close()

# Ruta para mostrar la página principal
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('Home.html', {"request": request})

# Ruta para registrar un voluntario
@app.post('/create-voluntario', response_class=JSONResponse)
async def add_voluntario(ID: int = Form(...), Nombre: str = Form(...), Apellido: str = Form(...), Telefono: int = Form(...), Intereses: str = Form(...)):
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO voluntarios (id, nombre, apellido, telefono, intereses) VALUES (?, ?, ?, ?, ?)", (ID, Nombre, Apellido, Telefono, Intereses))
    conn.commit()
    conn.close()
    return JSONResponse(content={"mensaje": "Voluntario agregado con éxito"}, status_code=200)

# Ruta para eliminar voluntario por ID
@app.delete('/eliminar-voluntario', response_class=JSONResponse)
async def delete_voluntario(ID: int = Form(...)):
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM voluntarios WHERE id = ?", (ID,))
    conn.commit()
    conn.close()
    return JSONResponse(content={"mensaje": "Voluntario eliminado con éxito"}, status_code=200)

# Ruta para registrar un programa
@app.post('/create-programa', response_class=JSONResponse)
async def add_programa(nombre: str = Form(...), descripcion: str = Form(...)):
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO programas (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
    conn.commit()
    conn.close()
    return JSONResponse(content={"mensaje": "Programa agregado con éxito"}, status_code=200)

# Ruta para eliminar programa por Nombre
@app.delete('/eliminar-programa', response_class=JSONResponse)
async def delete_programa(Nombre: str = Form(...)):
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM programas WHERE nombre = ?", (Nombre,))
    conn.commit()
    conn.close()
    return JSONResponse(content={"mensaje": "Programa eliminado con éxito"}, status_code=200)

# Ruta para mostrar todos los voluntarios
@app.get('/voluntarios', response_class=JSONResponse)
async def mostrar_voluntarios():
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM voluntarios")
    voluntarios = cursor.fetchall()
    conn.close()
    return JSONResponse(content={"voluntarios": voluntarios}, status_code=200)

# Ruta para mostrar todos los programas
@app.get('/programas', response_class=JSONResponse)
async def mostrar_programas():
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM programas")
    programas = cursor.fetchall()
    conn.close()
    return JSONResponse(content={"programas": programas}, status_code=200)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)

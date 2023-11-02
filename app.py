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

# Resto del código sin cambios...

if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)

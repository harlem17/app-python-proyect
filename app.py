from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
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

# La URL de conexión a la base de datos PostgreSQL proporcionada por Render
db_url = "postgres://postgres:1cBFBFEgCGaAC5da6Cb21Bgdf215FD-C@roundhouse.proxy.rlwy.net:51888/railway"

# Función para obtener la conexión a la base de datos
async def get_database_conn():
    conn = await asyncpg.connect(db_url)
    return conn

# Crear la tabla 'voluntarios' si no existe
async def create_voluntarios_table():
    conn = await get_database_conn()
    query = '''
    CREATE TABLE IF NOT EXISTS voluntarios (
        id SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        telefono INTEGER NOT NULL,
        intereses TEXT
    )
    '''
    await conn.execute(query)
    await conn.close()

# Crear la tabla 'programas' si no existe
async def create_programas_table():
    conn = await get_database_conn()
    query = '''
    CREATE TABLE IF NOT EXISTS programas (
        nombre TEXT PRIMARY KEY,
        descripcion TEXT
    )
    '''
    await conn.execute(query)
    await conn.close()

# Ruta para mostrar la página principal
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('Home.html', {"request": request})

# Ruta para crear un voluntario
@app.post('/create-voluntario', response_class=JSONResponse)
async def add_voluntario(ID: int = Form(...), Nombre: str = Form(...), Apellido: str = Form(...), Telefono: int = Form(...), Intereses: str = Form(...)):
    try:
        # Validar la longitud del número de teléfono
        if len(str(Telefono)) != 10:
            raise ValueError("El número de teléfono debe tener 10 dígitos.")

        conn = await get_database_conn()
        query = 'INSERT INTO voluntarios (id, nombre, apellido, telefono, intereses) VALUES ($1, $2, $3, $4, $5)'
        await conn.execute(query, ID, Nombre, Apellido, Telefono, Intereses)
        await conn.close()
        print("Voluntario agregado con éxito")
        return JSONResponse(content={"mensaje": "Voluntario agregado con éxito"}, status_code=200)
    except ValueError as ve:
        print(f"Error al agregar voluntario: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=400)
    except Exception as e:
        print(f"Error al agregar voluntario: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para eliminar voluntario por ID
@app.delete('/eliminar-voluntario', response_class=JSONResponse)
async def delete_voluntario(ID: int = Form(...)):
    try:
        conn = await get_database_conn()
        query = 'DELETE FROM voluntarios WHERE id = $1'
        await conn.execute(query, ID)
        await conn.close()
        print("Voluntario eliminado con éxito")
        return JSONResponse(content={"mensaje": "Voluntario eliminado con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al eliminar voluntario: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para registrar un programa
@app.post('/create-programa', response_class=JSONResponse)
async def add_programa(nombre: str = Form(...), descripcion: str = Form(...)):
    try:
        conn = await get_database_conn()
        query = 'INSERT INTO programas (nombre, descripcion) VALUES ($1, $2)'
        await conn.execute(query, nombre, descripcion)
        await conn.close()
        print("Programa agregado con éxito")
        return JSONResponse(content={"mensaje": "Programa agregado con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al agregar programa: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para eliminar programa por Nombre
@app.delete('/eliminar-programa', response_class=JSONResponse)
async def delete_programa(Nombre: str = Form(...)):
    try:
        conn = await get_database_conn()
        query = 'DELETE FROM programas WHERE nombre = $1'
        await conn.execute(query, Nombre)
        await conn.close()
        print("Programa eliminado con éxito")
        return JSONResponse(content={"mensaje": "Programa eliminado con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al eliminar programa: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para mostrar todos los voluntarios
@app.get('/voluntarios', response_class=JSONResponse)
async def mostrar_voluntarios():
    try:
        conn = await get_database_conn()
        query = 'SELECT * FROM voluntarios'
        result = await conn.fetch(query)
        voluntarios = [{"ID": row['id'], "Nombre": row['nombre'], "Apellido": row['apellido'], "Telefono": row['telefono'], "Intereses": row['intereses']} for row in result]
        await conn.close()
        return JSONResponse(content={"voluntarios": voluntarios}, status_code=200)
    except Exception as e:
        print(f"Error al obtener voluntarios: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para mostrar todos los programas
@app.get('/programas', response_class=JSONResponse)
async def mostrar_programas():
    try:
        conn = await get_database_conn()
        query_programas = 'SELECT * FROM programas'
        programas_result = await conn.fetch(query_programas)

        programas = [{"nombre": programa_row['nombre'], "descripcion": programa_row['descripcion']} for programa_row in programas_result]

        await conn.close()
        return JSONResponse(content={"programas": programas}, status_code=200)
    except Exception as e:
        print(f"Error al obtener programas: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Iniciar la aplicación FastAPI
if __name__ == '__main__':
    create_voluntarios_table()  # Crear la tabla de voluntarios al iniciar
    create_programas_table()  # Crear la tabla de programas al iniciar
    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)

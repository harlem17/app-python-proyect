from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
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

# Parámetros de conexión a la base de datos PostgreSQL
db_params = {
    'host': 'roundhouse.proxy.rlwy.net',
    'port': 51888,
    'database': 'railway',
    'user': 'postgres',
    'password': '1cBFBFEgCGaAC5da6Cb21Bgdf215FD-C',
}

# Función para obtener la conexión a la base de datos
def get_database_conn():
    conn = psycopg2.connect(**db_params)
    return conn

# Crear la tabla 'voluntarios' si no existe
def create_voluntarios_table():
    conn = get_database_conn()
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS voluntarios (
        id SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        telefono INTEGER NOT NULL,
        intereses TEXT
    )
    '''
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

# Crear la tabla 'programas' si no existe
def create_programas_table():
    conn = get_database_conn()
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS programas (
        nombre TEXT PRIMARY KEY,
        descripcion TEXT
    )
    '''
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

# Ruta para mostrar la página principal
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('Home.html', {"request": request})

# Ruta para crear un voluntario
@app.post('/create-voluntario', response_class=JSONResponse)
async def add_voluntario(ID: int = Form(...), Nombre: str = Form(...), Apellido: str = Form(...), Telefono: int = Form(...), Intereses: str = Form(...)):
    try:
        conn = get_database_conn()
        cursor = conn.cursor()
        query = 'INSERT INTO voluntarios (id, nombre, apellido, telefono, intereses) VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query, (ID, Nombre, Apellido, Telefono, Intereses))
        conn.commit()
        cursor.close()
        conn.close()
        print("Voluntario agregado con éxito")
        return JSONResponse(content={"mensaje": "Voluntario agregado con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al agregar voluntario: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para eliminar voluntario por ID
@app.delete('/eliminar-voluntario', response_class=JSONResponse)
async def delete_voluntario(ID: int = Form(...)):
    try:
        conn = get_database_conn()
        cursor = conn.cursor()
        query = 'DELETE FROM voluntarios WHERE id = %s'
        cursor.execute(query, (ID,))
        conn.commit()
        cursor.close()
        conn.close()
        print("Voluntario eliminado con éxito")
        return JSONResponse(content={"mensaje": "Voluntario eliminado con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al eliminar voluntario: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para registrar un programa
@app.post('/create-programa', response_class=JSONResponse)
async def add_programa(nombre: str = Form(...), descripcion: str = Form(...)):
    try:
        conn = get_database_conn()
        cursor = conn.cursor()
        query = 'INSERT INTO programas (nombre, descripcion) VALUES (%s, %s)'
        cursor.execute(query, (nombre, descripcion))
        conn.commit()
        cursor.close()
        conn.close()
        print("Programa agregado con éxito")
        return JSONResponse(content={"mensaje": "Programa agregado con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al agregar programa: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para que los voluntarios se unan a un programa
@app.post('/unirse-programa', response_class=JSONResponse)
async def unirse_programa(nombre_programa: str = Form(...), voluntario_id: int = Form(...)):
    try:
        conn = get_database_conn()
        cursor = conn.cursor()
        query_voluntario = 'SELECT * FROM voluntarios WHERE id = %s'
        cursor.execute(query_voluntario, (voluntario_id,))
        voluntario = cursor.fetchone()
        
        query_programa = 'SELECT * FROM programas WHERE nombre = %s'
        cursor.execute(query_programa, (nombre_programa,))
        programa = cursor.fetchone()

        if voluntario and programa:
            query = 'INSERT INTO programa_voluntario (programa_id, voluntario_id) VALUES (%s, %s)'
            cursor.execute(query, (programa[0], voluntario[0]))
            conn.commit()
            cursor.close()
            conn.close()
            print("Voluntario agregado al programa con éxito")
            return JSONResponse(content={"mensaje": "Voluntario agregado al programa con éxito"}, status_code=200)
        else:
            print("Programa o voluntario no encontrado")
            return JSONResponse(content={"mensaje": "Programa o voluntario no encontrado"}, status_code=404)
    except Exception as e:
        print(f"Error al unirse a un programa: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para eliminar programa por Nombre
@app.delete('/eliminar-programa', response_class=JSONResponse)
async def delete_programa(Nombre: str = Form(...)):
    try:
        conn = get_database_conn()
        cursor = conn.cursor()
        query = 'DELETE FROM programas WHERE nombre = %s'
        cursor.execute(query, (Nombre,))
        conn.commit()
        cursor.close()
        conn.close()
        print("Programa eliminado con éxito")
        return JSONResponse(content={"mensaje": "Programa eliminado con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al eliminar programa: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para mostrar todos los voluntarios
@app.get('/voluntarios', response_class=JSONResponse)
async def mostrar_voluntarios():
    try:
        conn = get_database_conn()
        cursor = conn.cursor()
        query = 'SELECT * FROM voluntarios'
        cursor.execute(query)
        result = cursor.fetchall()
        voluntarios = [{"ID": row[0], "Nombre": row[1], "Apellido": row[2], "Telefono": row[3], "Intereses": row[4]} for row in result]
        cursor.close()
        conn.close()
        return JSONResponse(content={"voluntarios": voluntarios}, status_code=200)
    except Exception as e:
        print(f"Error al obtener voluntarios: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para mostrar todos los programas y los voluntarios que se han unido
@app.get('/programas', response_class=JSONResponse)
async def mostrar_programas_con_voluntarios():
    try:
        conn = get_database_conn()
        cursor = conn.cursor()
        query_programas = 'SELECT * FROM programas'
        cursor.execute(query_programas)
        programas_result = cursor.fetchall()

        programas = []
        for programa_row in programas_result:
            programa = {"nombre": programa_row[0], "descripcion": programa_row[1]}
            
            query_voluntarios = 'SELECT v.nombre, v.apellido, v.telefono, v.intereses FROM voluntarios v INNER JOIN programa_voluntario pv ON v.id = pv.voluntario_id INNER JOIN programas p ON p.nombre = pv.programa_id WHERE p.nombre = %s'
            cursor.execute(query_voluntarios, (programa_row[0],))
            voluntarios_result = cursor.fetchall()

            voluntarios = [{"nombre": v[0], "apellido": v[1], "telefono": v[2], "intereses": v[3]} for v in voluntarios_result]
            programa["voluntarios"] = voluntarios

            programas.append(programa)

        cursor.close()
        conn.close()
        return JSONResponse(content={"programas": programas}, status_code=200)
    except Exception as e:
        print(f"Error al obtener programas con voluntarios: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == '__main__':
    create_voluntarios_table()  # Crear la tabla de voluntarios al iniciar
    create_programas_table()  # Crear la tabla de programas al iniciar
    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)

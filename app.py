from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
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

# La URL de conexión a la base de datos PostgreSQL proporcionada por Railway
db_url = "postgres://postgres:c*FAg-*GdG1CDCb-CGDfeDD2c3dgfd52@monorail.proxy.rlwy.net:39298/railway"

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
        telefono BIGINT NOT NULL,  -- Cambiado a BIGINT
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

# Crear la tabla de asignaciones si no existe
async def create_asignaciones_table():
    conn = await get_database_conn()
    query = '''
    CREATE TABLE IF NOT EXISTS asignaciones (
        id SERIAL PRIMARY KEY,
        programa_nombre TEXT REFERENCES programas(nombre),
        voluntario_id INTEGER REFERENCES voluntarios(id)
    )
    '''
    await conn.execute(query)
    await conn.close()

# Crear la tabla de donaciones si no existe
async def create_donaciones_table():
    conn = await get_database_conn()
    query = '''
    CREATE TABLE IF NOT EXISTS donaciones (
        id SERIAL PRIMARY KEY,
        cedula TEXT NOT NULL,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        ciudad TEXT NOT NULL,
        programa_nombre TEXT REFERENCES programas(nombre),
        monto FLOAT NOT NULL
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
async def add_voluntario(
    ID: int = Form(...),
    Nombre: str = Form(...),
    Apellido: str = Form(...),
    Telefono: int = Form(...),  # Cambiado a int
    Intereses: str = Form(...),
):
    try:
        conn = await get_database_conn()
        query = 'INSERT INTO voluntarios (id, nombre, apellido, telefono, intereses) VALUES ($1, $2, $3, $4, $5)'
        await conn.execute(query, ID, Nombre, Apellido, Telefono, Intereses)
        await conn.close()
        print("Voluntario agregado con éxito")
        return JSONResponse(content={"mensaje": "Voluntario agregado con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al agregar voluntario: {str(e)}")
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
        
# Ruta para registrar donaciones
@app.post('/registrar-donacion', response_class=JSONResponse)
async def registrar_donacion(
    Cedula: str = Form(...),
    NombreDonante: str = Form(...),
    ApellidoDonante: str = Form(...),
    CiudadResidencia: str = Form(...),
    ProgramaDonacion: str = Form(...),
    MontoDonacion: float = Form(...),
):
    try:
        conn = await get_database_conn()

        # Verificar si el programa existe
        query_programa = 'SELECT * FROM programas WHERE nombre = $1'
        programa_result = await conn.fetchrow(query_programa, ProgramaDonacion)

        if not programa_result:
            await conn.close()
            return JSONResponse(content={"error": "Programa no encontrado"}, status_code=404)

        # Insertar la donación en la tabla de donaciones
        query = '''
            INSERT INTO donaciones (cedula, nombre, apellido, ciudad, programa_nombre, monto)
            VALUES ($1, $2, $3, $4, $5, $6)
        '''
        await conn.execute(query, Cedula, NombreDonante, ApellidoDonante, CiudadResidencia, ProgramaDonacion, MontoDonacion)
        await conn.close()

        print("Donación registrada con éxito")
        return JSONResponse(content={"mensaje": "Donación registrada con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al registrar donación: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
        
# Ruta para que los voluntarios se unan a un programa
@app.post('/unirse-programa', response_class=JSONResponse)
async def unirse_programa(nombre_programa: str = Form(...), voluntario_id: int = Form(...)):
    try:
        conn = await get_database_conn()

        # Verificar si el programa existe
        query_programa = 'SELECT * FROM programas WHERE nombre = $1'
        programa = await conn.fetch(query_programa, nombre_programa)

        if not programa:
            await conn.close()
            return JSONResponse(content={"error": "Programa no encontrado"}, status_code=404)

        # Verificar si el voluntario existe
        query_voluntario = 'SELECT * FROM voluntarios WHERE id = $1'
        voluntario = await conn.fetch(query_voluntario, voluntario_id)

        if not voluntario:
            await conn.close()
            return JSONResponse(content={"error": "Voluntario no encontrado"}, status_code=404)

        # Agregar la asignación a la tabla de asignaciones
        query = 'INSERT INTO asignaciones (programa_nombre, voluntario_id) VALUES ($1, $2)'
        await conn.execute(query, nombre_programa, voluntario_id)
        await conn.close()

        print("Voluntario asignado al programa con éxito")
        return JSONResponse(content={"mensaje": "Voluntario asignado al programa con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al unirse a un programa: {str(e)}")
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

# Ruta para mostrar todos los programas y los voluntarios que se han unido
@app.get('/programas', response_class=JSONResponse)
async def mostrar_programas_con_voluntarios():
    try:
        conn = await get_database_conn()
        query_programas = 'SELECT * FROM programas'
        programas_result = await conn.fetch(query_programas)

        programas = []
        for programa_row in programas_result:
            programa = {"nombre": programa_row['nombre'], "descripcion": programa_row['descripcion']}
            
            # Obtener voluntarios asignados al programa desde la tabla de asignaciones
            query_voluntarios = 'SELECT v.nombre, v.apellido, v.telefono, v.intereses FROM voluntarios v INNER JOIN asignaciones a ON v.id = a.voluntario_id WHERE a.programa_nombre = $1'
            voluntarios_result = await conn.fetch(query_voluntarios, programa_row['nombre'])

            voluntarios = [{"nombre": v['nombre'], "apellido": v['apellido'], "telefono": v['telefono'], "intereses": v['intereses']} for v in voluntarios_result]
            programa["voluntarios"] = voluntarios

            programas.append(programa)

        await conn.close()
        return JSONResponse(content={"programas": programas}, status_code=200)
    except Exception as e:
        print(f"Error al obtener programas con voluntarios: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
        
# Ruta para mostrar todas las donaciones
@app.get('/donaciones', response_class=JSONResponse)
async def mostrar_donaciones():
    try:
        conn = await get_database_conn()
        query_donaciones = 'SELECT * FROM donaciones'
        donaciones_result = await conn.fetch(query_donaciones)

        # Calcular el monto total
        monto_total = sum(d['monto'] for d in donaciones_result)

        donaciones = [{"ID": row['id'], "Cedula": row['cedula'], "Nombre": row['nombre'], "Apellido": row['apellido'],
                       "Ciudad": row['ciudad'], "Programa_nombre": row['programa_nombre'], "Monto": row['monto']} for row in donaciones_result]

        await conn.close()
        return JSONResponse(content={"donaciones": donaciones, "monto_total": monto_total}, status_code=200)
    except Exception as e:
        print(f"Error al obtener donaciones: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
        
# Ruta para eliminar voluntario por ID
@app.delete('/eliminar-voluntario', response_class=JSONResponse)
async def delete_voluntario(ID: int = Form(...)):
    try:
        conn = await get_database_conn()
        
        # Verificar si el voluntario existe antes de intentar eliminarlo
        query_voluntario = 'SELECT * FROM voluntarios WHERE id = $1'
        voluntario = await conn.fetch(query_voluntario, ID)

        if not voluntario:
            await conn.close()
            raise HTTPException(status_code=404, detail="Voluntario no encontrado")

        query = 'DELETE FROM voluntarios WHERE id = $1'
        await conn.execute(query, ID)
        await conn.close()
        print("Voluntario eliminado con éxito")
        return JSONResponse(content={"mensaje": "Voluntario eliminado con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al eliminar voluntario: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para eliminar programa por Nombre
@app.delete('/eliminar-programa', response_class=JSONResponse)
async def delete_programa(Nombre: str = Form(...)):
    try:
        conn = await get_database_conn()

        # Verificar si el programa existe antes de intentar eliminarlo
        query_programa = 'SELECT * FROM programas WHERE nombre = $1'
        programa = await conn.fetch(query_programa, Nombre)

        if not programa:
            await conn.close()
            raise HTTPException(status_code=404, detail="Programa no encontrado")

        # Eliminar asignaciones del programa en la tabla de asignaciones
        query_delete_asignaciones = 'DELETE FROM asignaciones WHERE programa_nombre = $1'
        await conn.execute(query_delete_asignaciones, Nombre)

        # Eliminar al programa
        query_delete_programa = 'DELETE FROM programas WHERE nombre = $1'
        await conn.execute(query_delete_programa, Nombre)

        await conn.close()
        print("Programa eliminado con éxito")
        return JSONResponse(content={"mensaje": "Programa eliminado con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al eliminar programa: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para eliminar una donación por ID
@app.delete('/eliminar-donacion/{donacion_id}', response_class=JSONResponse)
async def eliminar_donacion(donacion_id: int):
    try:
        conn = await get_database_conn()

        # Verificar si la donación existe antes de intentar eliminarla
        query_donacion = 'SELECT * FROM donaciones WHERE id = $1'
        donacion = await conn.fetch(query_donacion, donacion_id)

        if not donacion:
            await conn.close()
            raise HTTPException(status_code=404, detail="Donación no encontrada")

        # Eliminar la donación
        query = 'DELETE FROM donaciones WHERE id = $1'
        await conn.execute(query, donacion_id)

        await conn.close()
        print("Donación eliminada con éxito")
        return JSONResponse(content={"mensaje": "Donación eliminada con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al eliminar donación: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
        
# Ruta para que los voluntarios se unan a un programa
@app.post('/unirse-programa', response_class=JSONResponse)
async def unirse_programa(nombre_programa: str = Form(...), voluntario_id: int = Form(...)):
    try:
        conn = await get_database_conn()

        # Verificar si el programa existe
        query_programa = 'SELECT * FROM programas WHERE nombre = $1'
        programa = await conn.fetch(query_programa, nombre_programa)

        print(f"Programa: {programa}")

        if not programa:
            await conn.close()
            return JSONResponse(content={"error": "Programa no encontrado"}, status_code=404)

        # Verificar si el voluntario existe
        query_voluntario = 'SELECT * FROM voluntarios WHERE id = $1'
        voluntario = await conn.fetch(query_voluntario, voluntario_id)

        print(f"Voluntario: {voluntario}")

        if not voluntario:
            await conn.close()
            return JSONResponse(content={"error": "Voluntario no encontrado"}, status_code=404)

        # Agregar la asignación a la tabla de asignaciones
        query = 'INSERT INTO asignaciones (programa_nombre, voluntario_id) VALUES ($1, $2)'
        await conn.execute(query, nombre_programa, voluntario_id)
        await conn.close()

        print("Voluntario asignado al programa con éxito")
        return JSONResponse(content={"mensaje": "Voluntario asignado al programa con éxito"}, status_code=200)
    except Exception as e:
        print(f"Error al unirse a un programa: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
        
# Ruta para buscar una donación por ID
@app.get('/donacion/{donacion_id}', response_class=JSONResponse)
async def buscar_donacion(donacion_id: int):
    try:
        conn = await get_database_conn()
        query = 'SELECT * FROM donaciones WHERE id = $1'
        result = await conn.fetch(query, donacion_id)

        if not result:
            await conn.close()
            return JSONResponse(content={"error": "Donación no encontrada"}, status_code=404)
            
        donacion = {
            "ID": result[0]['id'],
            "Cedula": result[0]['cedula'],
            "Nombre": result[0]['nombre'],
            "Apellido": result[0]['apellido'],
            "Ciudad": result[0]['ciudad'],
            "Programa_nombre": result[0]['programa_nombre'],
            "Monto": result[0]['monto']
        }

        await conn.close()
        return JSONResponse(content={"donacion": donacion}, status_code=200)
    except Exception as e:
        print(f"Error al buscar donación: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
        
if __name__ == '__main__':
    create_voluntarios_table()  # Crear la tabla de voluntarios al iniciar
    create_programas_table()  # Crear la tabla de programas al iniciar
    create_asignaciones_table()  # Crear la tabla de asignaciones al iniciar
    create_donaciones_table()  # Crear la tabla de donaciones al iniciar
    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)

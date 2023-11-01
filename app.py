from fastapi import FastAPI, Request
from fastapi import Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Esto permite solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista para almacenar voluntarios (simulación de una base de datos)
voluntarios_db = []

# Lista para almacenar programas
programas_db = []

# Ruta para mostrar la página principal
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('Home.html', {"request": request})

# Ruta para registrar un voluntario
@app.post('/create-voluntario', response_class=JSONResponse)
async def add_voluntario(ID: int = Form(...), Nombre: str = Form(...), Apellido: str = Form(...), Telefono: int = Form(...), Intereses: str = Form(...)):
    nuevo_voluntario = {
        'ID': ID,
        'Nombre': Nombre,
        'Apellido': Apellido,
        'Telefono': Telefono,
        'Intereses': Intereses
    }

    voluntarios_db.append(nuevo_voluntario)
    print("Voluntario agregado con éxito", nuevo_voluntario)
    return JSONResponse(content={"mensaje": "Voluntario agregado con éxito", "nuevo_voluntario": nuevo_voluntario}, status_code=200)

# Ruta para eliminar voluntario por ID
@app.delete('/eliminar-voluntario', response_class=JSONResponse)
async def delete_voluntario(ID: int = Form(...)):
    for voluntario in voluntarios_db:
        if voluntario['ID'] == ID:
            voluntarios_db.remove(voluntario)

            # Eliminar al voluntario de la lista de participantes en los programas
            for programa in programas_db:
                if voluntario in programa['participantes']:
                    programa['participantes'].remove(voluntario)

            print("Voluntario eliminado con éxito")
            return JSONResponse(content={"mensaje": "Voluntario eliminado con éxito"}, status_code=200)

    print("Voluntario no encontrado")
    return JSONResponse(content={"mensaje": "Voluntario no encontrado"}, status_code=404)

# Ruta para registrar un programa
@app.post('/create-programa', response_class=JSONResponse)
async def add_programa(nombre: str = Form(...), descripcion: str = Form(...)):
    nuevo_programa = {
        'nombre': nombre,
        'descripcion': descripcion,
        'participantes': []
    }

    programas_db.append(nuevo_programa)
    print("Programa agregado con éxito", nuevo_programa)
    return JSONResponse(content={"mensaje": "Programa agregado con éxito", "nuevo_programa": nuevo_programa}, status_code=200)

# Ruta para que los voluntarios se unan a un programa
@app.post('/unirse-programa', response_class=JSONResponse)
async def unirse_programa(nombre_programa: str = Form(...), voluntario_id: int = Form(...)):
    programa_encontrado = next((programa for programa in programas_db if programa['nombre'] == nombre_programa), None)
    voluntario_encontrado = next((voluntario for voluntario in voluntarios_db if voluntario['ID'] == voluntario_id), None)

    if programa_encontrado and voluntario_encontrado:
        programa_encontrado['participantes'].append(voluntario_encontrado)
        print("Voluntario agregado al programa con éxito")
        return JSONResponse(content={"mensaje": "Voluntario agregado al programa con éxito"}, status_code=200)
    else:
        print("Programa o voluntario no encontrado")
        return JSONResponse(content={"mensaje": "Programa o voluntario no encontrado"}, status_code=404)

# Ruta para eliminar programa por Nombre
@app.delete('/eliminar-programa', response_class=JSONResponse)
async def delete_programa(Nombre: str = Form(...)):
    for programa in programas_db:
        if programa['nombre'] == nombre:
            programas_db.remove(programa)
            print("Programa eliminado con éxito")
            return JSONResponse(content={"mensaje": "Programa eliminado con éxito"}, status_code=200)

    print("Programa no encontrado")
    return JSONResponse(content={"mensaje": "Programa no encontrado"}, status_code=404)

# Ruta para mostrar todos los voluntarios
@app.get('/voluntarios', response_class=JSONResponse)
async def mostrar_voluntarios():
    return JSONResponse(content={"voluntarios": voluntarios_db}, status_code=200)

# Ruta para mostrar todos los programas
@app.get('/programas', response_class=JSONResponse)
async def mostrar_programas():
    return JSONResponse(content={"programas": programas_db}, status_code=200)

if __name__ == '__main__':
    uvicorn.run('app:app')

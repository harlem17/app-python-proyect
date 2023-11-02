from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Configuración de la base de datos SQLite
def get_db():
    db = sqlite3.connect("nonprofitorganization.db")
    return db

# Modelos de datos para voluntarios y programas
class Voluntario(BaseModel):
    ID: int
    Nombre: str
    Apellido: str
    Telefono: int
    Intereses: str

class Programa(BaseModel):
    Nombre: str
    Descripcion: str

# Crear las tablas en la base de datos SQLite
def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voluntarios (
            ID INTEGER PRIMARY KEY,
            Nombre TEXT,
            Apellido TEXT,
            Telefono INTEGER,
            Intereses TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS programas (
            Nombre TEXT PRIMARY KEY,
            Descripcion TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

create_tables()  # Crear las tablas al iniciar la aplicación

# Ruta para registrar un voluntario
@app.post('/create-voluntario', response_model=Voluntario)
async def add_voluntario(voluntario: Voluntario):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO voluntarios (ID, Nombre, Apellido, Telefono, Intereses)
        VALUES (?, ?, ?, ?, ?)
    ''', (voluntario.ID, voluntario.Nombre, voluntario.Apellido, voluntario.Telefono, voluntario.Intereses))
    
    conn.commit()
    conn.close()
    
    return voluntario

# Ruta para eliminar voluntario por ID
@app.delete('/eliminar-voluntario')
async def delete_voluntario(ID: int):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM voluntarios WHERE ID = ?', (ID,))
    
    if cursor.rowcount > 0:
        conn.commit()
        conn.close()
        return {"mensaje": "Voluntario eliminado con éxito"}
    else:
        conn.close()
        raise HTTPException(status_code=404, detail="Voluntario no encontrado")

# Ruta para listar todos los voluntarios
@app.get('/voluntarios', response_model=list[Voluntario])
async def listar_voluntarios():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM voluntarios')
    voluntarios = cursor.fetchall()
    
    conn.close()
    
    return [Voluntario(**voluntario) for voluntario in voluntarios]

# Ruta para registrar un programa
@app.post('/create-programa', response_model=Programa)
async def add_programa(programa: Programa):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO programas (Nombre, Descripcion)
        VALUES (?, ?)
    ''', (programa.Nombre, programa.Descripcion))
    
    conn.commit()
    conn.close()
    
    return programa

# Ruta para eliminar programa por Nombre
@app.delete('/eliminar-programa')
async def delete_programa(nombre: str):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM programas WHERE Nombre = ?', (nombre,))
    
    if cursor.rowcount > 0:
        conn.commit()
        conn.close()
        return {"mensaje": "Programa eliminado con éxito"}
    else:
        conn.close()
        raise HTTPException(status_code=404, detail="Programa no encontrado")

# Ruta para listar todos los programas
@app.get('/programas', response_model=list[Programa])
async def listar_programas():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM programas')
    programas = cursor.fetchall()
    
    conn.close()
    
    return [Programa(**programa) for programa in programas]

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

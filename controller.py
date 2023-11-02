import sqlite3 as sql

def createDB():
    conn = sql.connect("nonprofitorganization")
    conn.commit()
    conn.close()

def createTable():
    conn = sql.connect("nonprofitorganization.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE voluntarios(
            ID integer,
            Nombre text,
            Apellido text,
            Telefono integer,
            Intereses text
        )"""
    )
    cursor.execute(
        """CREATE TABLE programas(
            Nombre text,
            Descripcion text
        )"""
    )
    conn.commit()   
    conn.close

if __name__ == "__main__":
    #createDB()
    createTable()
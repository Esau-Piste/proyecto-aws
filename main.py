from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(title="API Escuela AWS")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": "Error de validacion en los campos"}
    )

# --- ENTIDADES Y VALIDACIONES ---

class Alumno(BaseModel):
    id: int
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    matricula: str = Field(..., min_length=1)
    promedio: float

class Profesor(BaseModel):
    id: int
    numeroEmpleado: str = Field(..., min_length=1)
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    horasClase: int

# --- ALMACENAMIENTO EN MEMORIA ---
alumnos_db = []
profesores_db = []

# ENDPOINTS: ALUMNOS

@app.get("/alumnos", response_model=List[Alumno], status_code=status.HTTP_200_OK)
def get_alumnos():
    return alumnos_db

@app.get("/alumnos/{id}", response_model=Alumno, status_code=status.HTTP_200_OK)
def get_alumno(id: int):
    for alumno in alumnos_db:
        if alumno.id == id:
            return alumno
    raise HTTPException(status_code=404, detail="Alumno no encontrado")

@app.post("/alumnos", response_model=Alumno, status_code=status.HTTP_201_CREATED)
def create_alumno(alumno: Alumno):
    for a in alumnos_db:
        if a.id == alumno.id:
            raise HTTPException(status_code=400, detail="El ID del alumno ya existe")
    alumnos_db.append(alumno)
    return alumno

@app.put("/alumnos/{id}", response_model=Alumno, status_code=status.HTTP_200_OK)
def update_alumno(id: int, alumno_actualizado: Alumno):
    for i, alumno in enumerate(alumnos_db):
        if alumno.id == id:
            alumnos_db[i] = alumno_actualizado
            return alumno_actualizado
    raise HTTPException(status_code=404, detail="Alumno no encontrado")

@app.delete("/alumnos/{id}", status_code=status.HTTP_200_OK)
def delete_alumno(id: int):
    for i, alumno in enumerate(alumnos_db):
        if alumno.id == id:
            del alumnos_db[i]
            return {"mensaje": "Alumno eliminado exitosamente"}
    raise HTTPException(status_code=404, detail="Alumno no encontrado")


# ENDPOINTS: PROFESORES


@app.get("/profesores", response_model=List[Profesor], status_code=status.HTTP_200_OK)
def get_profesores():
    return profesores_db

@app.get("/profesores/{id}", response_model=Profesor, status_code=status.HTTP_200_OK)
def get_profesor(id: int):
    for profesor in profesores_db:
        if profesor.id == id:
            return profesor
    raise HTTPException(status_code=404, detail="Profesor no encontrado")

@app.post("/profesores", response_model=Profesor, status_code=status.HTTP_201_CREATED)
def create_profesor(profesor: Profesor):
    for p in profesores_db:
        if p.id == profesor.id:
            raise HTTPException(status_code=400, detail="El ID del profesor ya existe")
    profesores_db.append(profesor)
    return profesor

@app.put("/profesores/{id}", response_model=Profesor, status_code=status.HTTP_200_OK)
def update_profesor(id: int, profesor_actualizado: Profesor):
    for i, profesor in enumerate(profesores_db):
        if profesor.id == id:
            profesores_db[i] = profesor_actualizado
            return profesor_actualizado
    raise HTTPException(status_code=404, detail="Profesor no encontrado")

@app.delete("/profesores/{id}", status_code=status.HTTP_200_OK)
def delete_profesor(id: int):
    for i, profesor in enumerate(profesores_db):
        if profesor.id == id:
            del profesores_db[i]
            return {"mensaje": "Profesor eliminado exitosamente"}
    raise HTTPException(status_code=404, detail="Profesor no encontrado")
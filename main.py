from fastapi import FastAPI, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session


URL_BASE_DATOS = "mysql+pymysql://admin:Admin12345@escueladb.ctwcggwkkjbr.us-east-1.rds.amazonaws.com:3306/escueladb"
engine = create_engine(URL_BASE_DATOS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="API Escuela AWS")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": "Error de validacion en los campos"}
    )

# --- TABLAS DE LA BASE DE DATOS ---
class AlumnoDB(Base):
    __tablename__ = "alumnos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    matricula = Column(String(20))
    promedio = Column(Float)
    password = Column(String(100))
    fotoPerfilUrl = Column(String(255), nullable=True)

class ProfesorDB(Base):
    __tablename__ = "profesores"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    numeroEmpleado = Column(Integer)
    nombres = Column(String(50))
    apellidos = Column(String(50))
    horasClase = Column(Integer)

# Crear las tablas en AWS
Base.metadata.create_all(bind=engine)

# Dependencia de la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- ESQUEMAS DE VALIDACIÓN (PYDANTIC) ---
class Alumno(BaseModel):
    # El id ya no es obligatorio al crear
    id: Optional[int] = None
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    matricula: str = Field(..., min_length=1)
    promedio: float
    password: str = Field(..., min_length=1)
    fotoPerfilUrl: Optional[str] = None

class Profesor(BaseModel):
    id: Optional[int] = None
    numeroEmpleado: int
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    horasClase: int


# ENDPOINTS DE ALUMNOS

@app.get("/alumnos", response_model=List[Alumno], status_code=200)
def get_alumnos(db: Session = Depends(get_db)):
    # SELECT * FROM alumnos;
    return db.query(AlumnoDB).all()

@app.post("/alumnos", response_model=Alumno, status_code=201)
def create_alumno(alumno: Alumno, db: Session = Depends(get_db)):
    # Convertimos los datos a un formato de base de datos (excluyendo el ID porque AWS lo genera)
    nuevo_alumno = AlumnoDB(**alumno.dict(exclude={"id"}))
    db.add(nuevo_alumno)
    db.commit()
    db.refresh(nuevo_alumno) # Recuperamos el ID generado por la BD
    return nuevo_alumno

@app.get("/alumnos/{id}", response_model=Alumno, status_code=200)
def get_alumno(id: int, db: Session = Depends(get_db)):
    alumno_db = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not alumno_db:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno_db

@app.put("/alumnos/{id}", response_model=Alumno, status_code=200)
def update_alumno(id: int, alumno: Alumno, db: Session = Depends(get_db)):
    alumno_db = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not alumno_db:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # Actualizamos los campos uno por uno
    datos_actualizar = alumno.dict(exclude={"id"})
    for key, value in datos_actualizar.items():
        setattr(alumno_db, key, value)
        
    db.commit()
    db.refresh(alumno_db)
    return alumno_db

@app.delete("/alumnos/{id}", status_code=200)
def delete_alumno(id: int, db: Session = Depends(get_db)):
    alumno_db = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not alumno_db:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    db.delete(alumno_db)
    db.commit()
    return {"mensaje": "Alumno eliminado"}


# ENDPOINTS DE PROFESORES

@app.get("/profesores", response_model=List[Profesor], status_code=200)
def get_profesores(db: Session = Depends(get_db)):
    return db.query(ProfesorDB).all()

@app.post("/profesores", response_model=Profesor, status_code=201)
def create_profesor(profesor: Profesor, db: Session = Depends(get_db)):
    nuevo_profesor = ProfesorDB(**profesor.dict(exclude={"id"}))
    db.add(nuevo_profesor)
    db.commit()
    db.refresh(nuevo_profesor)
    return nuevo_profesor

@app.get("/profesores/{id}", response_model=Profesor, status_code=200)
def get_profesor(id: int, db: Session = Depends(get_db)):
    profesor_db = db.query(ProfesorDB).filter(ProfesorDB.id == id).first()
    if not profesor_db:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor_db

@app.put("/profesores/{id}", response_model=Profesor, status_code=200)
def update_profesor(id: int, profesor: Profesor, db: Session = Depends(get_db)):
    profesor_db = db.query(ProfesorDB).filter(ProfesorDB.id == id).first()
    if not profesor_db:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    datos_actualizar = profesor.dict(exclude={"id"})
    for key, value in datos_actualizar.items():
        setattr(profesor_db, key, value)
        
    db.commit()
    db.refresh(profesor_db)
    return profesor_db

@app.delete("/profesores/{id}", status_code=200)
def delete_profesor(id: int, db: Session = Depends(get_db)):
    profesor_db = db.query(ProfesorDB).filter(ProfesorDB.id == id).first()
    if not profesor_db:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    db.delete(profesor_db)
    db.commit()
    return {"mensaje": "Profesor eliminado"}


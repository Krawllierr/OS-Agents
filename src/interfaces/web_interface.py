from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from pydantic.class_validators import validator
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pathlib import Path
from src.utils.database import get_db, DBUser, DBProject
from src.utils.ai_integration import process_project_with_gpt
from src.agents.agent_manager import AgentManager

app = FastAPI()

# Configurações de segurança
SECRET_KEY = "your_secret_key"  # Deve ser uma chave secreta forte em produção
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Montar o diretório static
static_dir = Path(__file__).resolve().parent.parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modelos Pydantic
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=300)
    deadline: datetime
    status: Optional[str] = Field(None, max_length=20)

    @validator('deadline')
    def check_deadline(cls, v):
        if v < datetime.now():
            raise ValueError('Deadline must be in the future')
        return v

class ProjectCreate(ProjectBase):
    pass

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=10, max_length=500)
    deadline: datetime

    @validator('deadline')
    def check_deadline(cls, v):
        if v < datetime.now():
            raise ValueError('Deadline must be in the future')
        return v

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=300)
    deadline: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=20)
    feedback: Optional[str] = Field(None, max_length=500)

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Atualizado de orm_mode para from_attributes
        
# Funções de segurança
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(DBUser).filter(DBUser.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# Rotas

@app.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project_data = project.dict()
    db_project = DBProject(
        **project_data,
        status="Iniciado",
        current_phase=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # Iniciar o processamento do projeto em background
    background_tasks = BackgroundTasks()
    background_tasks.add_task(process_project, db_project.id)

    return db_project


@app.get("/projects/{project_id}", response_model=Project)
async def read_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(DBProject).filter(DBProject.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: int, project_update: ProjectUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_project = db.query(DBProject).filter(DBProject.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Process feedback and move to next phase
    agent_manager = AgentManager()
    next_phase = agent_manager.process_feedback(db_project.id, project_update.feedback)
    
    db_project.current_phase = next_phase
    db_project.updated_at = datetime.now()
    db.commit()
    db.refresh(db_project)
    
    return db_project

def process_project(project_id: int):
    db = next(get_db())
    project = db.query(DBProject).filter(DBProject.id == project_id).first()
    
    # Process with GPT-4
    process_project_with_gpt(project)
    
    # Start agent manager
    agent_manager = AgentManager()
    agent_manager.process_project(project_id)

@app.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Criar projeto no banco de dados
    db_project = DBProject(**project.dict(), created_at=datetime.now(), updated_at=datetime.now())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # Processar projeto com GPT-4 e preencher projeto.json
    process_project_with_gpt(db_project)

    # Iniciar o AgentManager para processar o projeto
    agent_manager = AgentManager()
    agent_manager.process_project(db_project.id)

    return db_project

@app.get("/")
async def read_root():
    return FileResponse(str(static_dir / "index.html"))

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_project = DBProject(**project.dict(), created_at=datetime.now(), updated_at=datetime.now())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects", response_model=List[Project])
async def read_projects(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.query(DBProject).offset(skip).limit(limit).all()
    return projects

@app.get("/projects/{project_id}", response_model=Project)
async def read_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(DBProject).filter(DBProject.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: int, project: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_project = db.query(DBProject).filter(DBProject.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.dict().items():
        setattr(db_project, key, value)
    db_project.updated_at = datetime.now()
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(DBProject).filter(DBProject.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"status": "success", "message": "Project deleted successfully"}
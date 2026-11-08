import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Permitir que a sua página no GitHub Pages acesse este Web Service no Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, você pode trocar "*" pela URL do seu GitHub Pages
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pega a URL de conexão do Neon através das variáveis de ambiente do Render
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, status_code_detail="DATABASE_URL não configurada no ambiente.")
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# Cria a tabela de configuração no Neon ao iniciar a aplicação se ela não existir
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS site_config (
                id SERIAL PRIMARY KEY,
                data JSONB NOT NULL
            );
        """)
        # Insere um registro padrão se a tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM site_config;")
        count = cursor.fetchone()['count']
        if count == 0:
            default_config = {
                "tituloTopo": "TECH STORE",
                "urlLogo": "/imagens/logo.png",
                "heroTitle": "Sistema de Comissionamento em Três Níveis",
                "heroSubtitle": "Construa sua rede de parceiros, escale suas indicações e garanta comissões automáticas de até 10%.",
                "texto1": "O <strong>Sistema de Comissionamento em Três Níveis</strong> da nossa plataforma representa uma oportunidade extraordinária...",
                "texto2": "Ao se tornar um afiliado oficial, você desbloqueia o poder...",
                "texto3": "Quando você entra, ganha um link exclusivo...",
                "texto4": "Em cada um desses níveis de profundidade...",
                "tituloSecundario": "Como Funciona na Prática?",
                "textoSecundario": "Através de ferramentas visuais e materiais de apoio...",
                "urlVideo1": "",
                "urlVideo2": "",
                "urlVideo3": "",
                "urlImg1": "/imagens/rede.jpg",
                "urlImg2": "/imagens/detalhe2.jpg",
                "urlImg3": "/imagens/detalhe3.jpg"
            }
            cursor.execute("INSERT INTO site_config (data) VALUES (%s);", (json.dumps(default_config),))
            conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")

@app.on_event("startup")
def startup_event():
    init_db()

class ConfigModel(BaseModel):
    tituloTopo: str = None
    urlLogo: str = None
    heroTitle: str = None
    heroSubtitle: str = None
    texto1: str = None
    texto2: str = None
    texto3: str = None
    texto4: str = None
    tituloSecundario: str = None
    textoSecundario: str = None
    urlVideo1: str = None
    urlVideo2: str = None
    urlVideo3: str = None
    urlImg1: str = None
    urlImg2: str = None
    urlImg3: str = None

@app.get("/api/config")
def get_config():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM site_config ORDER BY id DESC LIMIT 1;")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return row['data']
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config")
def save_config(config: ConfigModel):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Atualiza ou insere as novas configurações no banco Neon
        cursor.execute("DELETE FROM site_config;") # Mantém sempre o registro mais recente atualizado
        cursor.execute("INSERT INTO site_config (data) VALUES (%s);", (json.dumps(config.dict()),))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success", "message": "Configurações salvas globalmente com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
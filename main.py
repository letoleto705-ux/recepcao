import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL não configurada no ambiente.")
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Cria a tabela com colunas dedicadas para Textos, Vídeos e Imagens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS site_config (
                id SERIAL PRIMARY KEY,
                titulo_topo TEXT,
                url_logo TEXT,
                hero_title TEXT,
                hero_subtitle TEXT,
                texto1 TEXT,
                texto2 TEXT,
                texto3 TEXT,
                texto4 TEXT,
                titulo_secundario TEXT,
                texto_secundario TEXT,
                url_video1 TEXT,
                url_video2 TEXT,
                url_video3 TEXT,
                url_img1 TEXT,
                url_img2 TEXT,
                url_img3 TEXT
            );
        """)
        
        # Insere dados padrão se a tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM site_config;")
        count = cursor.fetchone()['count']
        if count == 0:
            cursor.execute("""
                INSERT INTO site_config (
                    titulo_topo, url_logo, hero_title, hero_subtitle, 
                    texto1, texto2, texto3, texto4, 
                    titulo_secundario, texto_secundario, 
                    url_video1, url_video2, url_video3, 
                    url_img1, url_img2, url_img3
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                "TECH STORE", "/imagens/logo.png", 
                "Sistema de Comissionamento em Três Níveis", 
                "Construa sua rede de parceiros, escale suas indicações e garanta comissões automáticas de até 10%.",
                "O Sistema de Comissionamento em Três Níveis...", "Ao se tornar um afiliado...", "Quando você entra...", "Em cada um desses níveis...",
                "Como Funciona na Prática?", "Através de ferramentas visuais...",
                "", "", "", 
                "/imagens/rede.jpg", "/imagens/detalhe2.jpg", "/imagens/detalhe3.jpg"
            ))
            conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao inicializar o banco: {e}")

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
        cursor.execute("SELECT * FROM site_config ORDER BY id DESC LIMIT 1;")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            # Mapeia as colunas do banco para o formato esperado pelo frontend
            return {
                "tituloTopo": row['titulo_topo'],
                "urlLogo": row['url_logo'],
                "heroTitle": row['hero_title'],
                "heroSubtitle": row['hero_subtitle'],
                "texto1": row['texto1'],
                "texto2": row['texto2'],
                "texto3": row['texto3'],
                "texto4": row['texto4'],
                "tituloSecundario": row['titulo_secundario'],
                "textoSecundario": row['texto_secundario'],
                "urlVideo1": row['url_video1'],
                "urlVideo2": row['url_video2'],
                "urlVideo3": row['url_video3'],
                "urlImg1": row['url_img1'],
                "urlImg2": row['url_img2'],
                "urlImg3": row['url_img3'],
            }
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config")
def save_config(cfg: ConfigModel):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Limpa registros antigos e mantém sempre a configuração atualizada globalmente
        cursor.execute("DELETE FROM site_config;")
        
        cursor.execute("""
            INSERT INTO site_config (
                titulo_topo, url_logo, hero_title, hero_subtitle, 
                texto1, texto2, texto3, texto4, 
                titulo_secundario, texto_secundario, 
                url_video1, url_video2, url_video3, 
                url_img1, url_img2, url_img3
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            cfg.tituloTopo, cfg.urlLogo, cfg.heroTitle, cfg.heroSubtitle,
            cfg.texto1, cfg.texto2, cfg.texto3, cfg.texto4,
            cfg.tituloSecundario, cfg.textoSecundario,
            cfg.urlVideo1, cfg.urlVideo2, cfg.urlVideo3,
            cfg.urlImg1, cfg.urlImg2, cfg.urlImg3
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success", "message": "Configurações de vídeos, imagens e textos atualizadas no Neon!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
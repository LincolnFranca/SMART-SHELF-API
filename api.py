from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from PIL import Image
import io
import os
from prompts import PROMPTS
from typing import Literal
from pydantic import BaseModel
from pathlib import Path
import json

# Inicialização da API
app = FastAPI(
    title="Smart Shelf API",
    description="API para análise de prateleiras usando IA",
    version="1.0.0"
)

# Configuração CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do Gemini
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Classes para respostas
class AnalysisResponse(BaseModel):
    analysis: str
    cost: float
    execution_time: float

# Função para carregar configurações
def load_config():
    config_file = Path('config.json')
    if config_file.exists():
        return json.loads(config_file.read_text())
    return {
        'cost_per_analysis': 0.0005,
        'total_analyses': 0,
        'total_cost': 0.0
    }

# Função para salvar configurações
def save_config(config):
    Path('config.json').write_text(json.dumps(config, indent=2))

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_shelf(
    file: UploadFile = File(...),
    analysis_type: Literal["Rápida", "Completa"] = "Rápida"
):
    try:
        # Verificar se o arquivo é uma imagem
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="O arquivo deve ser uma imagem")
        
        # Ler e processar a imagem
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Realizar análise
        response = model.generate_content(
            contents=[PROMPTS[analysis_type], image],
            generation_config={
                'temperature': 0.1,
                'top_p': 0.8,
                'max_output_tokens': 300,
            }
        )
        
        # Atualizar estatísticas
        config = load_config()
        config['total_analyses'] += 1
        config['total_cost'] += config['cost_per_analysis']
        save_config(config)
        
        return AnalysisResponse(
            analysis=response.text,
            cost=config['cost_per_analysis'],
            execution_time=1.2  # Placeholder para tempo de execução real
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    config = load_config()
    return {
        "total_analyses": config['total_analyses'],
        "total_cost": config['total_cost']
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

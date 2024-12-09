from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from PIL import Image
import io
import os
from prompts import PROMPTS
from typing import Literal, List
from pydantic import BaseModel
from pathlib import Path
import json
from datetime import datetime
import time
from supabase import create_client
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from fastapi.responses import JSONResponse

# Classes para requisição e resposta
class Produto(BaseModel):
    nome: str
    descricao: str

class AnalysisResponse(BaseModel):
    analysis: str
    cost: float
    execution_time: float

# Inicialização da API
app = FastAPI(
    title="Smart Shelf API",
    description="API para análise de prateleiras usando IA",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do Gemini
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Configuração Supabase
supabase = create_client(
    os.environ.get("SUPABASE_URL", "sua_url"),
    os.environ.get("SUPABASE_KEY", "sua_key")
)

# Configuração Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
GOOGLE_SHEETS_CREDS = json.loads(os.environ.get('GOOGLE_SHEETS_CREDS', '{}'))
credentials = service_account.Credentials.from_service_account_info(GOOGLE_SHEETS_CREDS, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_shelf(
    file: UploadFile = File(...),
    produtos: str = Form(...)  # JSON string com lista de produtos
):
    start_time = time.time()
    try:
        # Verificar se o arquivo é uma imagem
        if not file.content_type.startswith("image/"):
            save_log(status="error", error="Arquivo inválido", produtos=[])
            raise HTTPException(status_code=400, detail="O arquivo deve ser uma imagem")
        
        # Converter string JSON para lista de produtos
        try:
            produtos_list = json.loads(produtos)
        except json.JSONDecodeError as e:
            save_log(status="error", error="JSON inválido", produtos=[])
            raise HTTPException(status_code=400, detail="Formato inválido da lista de produtos")
        
        # Validar número de produtos
        if len(produtos_list) > 3:
            save_log(status="error", error="Limite de produtos excedido", produtos=[p['nome'] for p in produtos_list])
            raise HTTPException(status_code=400, detail="Máximo de 3 produtos permitido")
        
        # Log dos produtos sendo analisados
        save_log(status="info", produtos=[p['nome'] for p in produtos_list])
        
        # Ler e processar a imagem
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Preparar o prompt com os produtos
        produtos_texto = "\n".join([
            f"- {p['nome']}: {p['descricao']}"
            for p in produtos_list
        ])
        
        # Realizar análise
        prompt = f"{PROMPTS['default']}\n\nProdutos a serem analisados:\n{produtos_texto}"
        response = model.generate_content(
            contents=[prompt, image],
            generation_config={
                'temperature': 0.1,
                'top_p': 0.8,
                'max_output_tokens': 300,
            }
        )
        
        execution_time = time.time() - start_time
        
        # Log da análise bem-sucedida
        save_log(
            status="success",
            produtos=[p['nome'] for p in produtos_list],
            execution_time=execution_time,
            cost=0.0005
        )

        return AnalysisResponse(
            analysis=response.text,
            cost=0.0005,
            execution_time=execution_time
        )

    except Exception as e:
        execution_time = time.time() - start_time
        save_log(
            status="error",
            error=str(e),
            produtos=[p['nome'] for p in produtos_list] if 'produtos_list' in locals() else [],
            execution_time=execution_time
        )
        raise

@app.post("/export-to-sheets")
async def export_to_sheets(spreadsheet_id: str):
    """Exporta os logs para uma planilha Google Sheets"""
    try:
        # Buscar logs do Supabase
        response = supabase.table('analysis_logs').select('*').order('timestamp', desc=True).execute()
        logs = response.data

        # Preparar dados para a planilha
        header = [['Data/Hora', 'Status', 'Produtos', 'Tempo de Execução (s)', 'Custo ($)', 'Erro']]
        rows = []
        for log in logs:
            # Formatar produtos como string
            produtos_str = ', '.join(log['produtos']) if log['produtos'] else ''
            
            # Formatar timestamp
            timestamp = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
            formatted_date = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            
            row = [
                formatted_date,
                log['status'],
                produtos_str,
                f"{log['execution_time']:.2f}" if log['execution_time'] else '',
                f"${log['cost']:.4f}" if log['cost'] else '',
                log['error'] if log['error'] else ''
            ]
            rows.append(row)

        # Atualizar planilha
        body = {
            'values': header + rows
        }
        
        # Limpar planilha e inserir novos dados
        sheet = sheets_service.spreadsheets()
        sheet.values().clear(
            spreadsheetId=spreadsheet_id,
            range='A1:Z'
        ).execute()
        
        result = sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range='A1',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        # Formatar cabeçalho
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 0.2,
                            'green': 0.2,
                            'blue': 0.2
                        },
                        'textFormat': {
                            'bold': True,
                            'foregroundColor': {
                                'red': 1.0,
                                'green': 1.0,
                                'blue': 1.0
                            }
                        }
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        }]

        sheet.batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()

        return JSONResponse(content={
            "message": "Logs exportados com sucesso",
            "rows_updated": len(rows)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar logs: {str(e)}")

def save_log(
    status: str,
    produtos: list,
    execution_time: float = 0,
    cost: float = 0,
    error: str = None
):
    """Salva o log da análise no Supabase"""
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": status,
        "produtos": produtos,
        "execution_time": execution_time,
        "cost": cost,
        "error": error
    }
    supabase.table('analysis_logs').insert(data).execute()

@app.get("/stats")
async def get_stats():
    """Retorna estatísticas das análises"""
    response = supabase.table('analysis_logs').select('*').execute()
    logs = response.data
    
    total = len(logs)
    successful = len([log for log in logs if log['status'] == 'success'])
    total_cost = sum(log['cost'] for log in logs if log['status'] == 'success')
    
    successful_times = [log['execution_time'] for log in logs if log['status'] == 'success']
    avg_time = sum(successful_times) / len(successful_times) if successful_times else 0
    
    return {
        "total_analyses": total,
        "successful_analyses": successful,
        "total_cost": total_cost,
        "average_execution_time": avg_time
    }

@app.get("/logs")
async def get_logs(limit: int = 10, status: str = None):
    """Retorna os últimos logs de análise"""
    query = supabase.table('analysis_logs').select('*')
    
    if status:
        query = query.eq('status', status)
    
    response = query.order('timestamp', desc=True).limit(limit).execute()
    
    return {"logs": response.data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

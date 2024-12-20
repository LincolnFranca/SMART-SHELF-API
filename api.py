from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
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
import asyncio

# Classes para requisição e resposta
class Produto(BaseModel):
    nome: str
    descricao: str

class ValidationResult(BaseModel):
    nome_marca: bool
    preco: bool
    posicionamento: bool
    organizacao: bool

class AnalysisResponse(BaseModel):
    status: str
    details: str
    validation: ValidationResult
    execution_time: float
    cost: float

# Inicialização da API
app = FastAPI(
    title="Smart Shelf API",
    description="API para análise de prateleiras usando IA",
    version="1.0.0"
)

# Handler para erros de validação
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação"""
    error_details = {
        "detail": exc.errors(),
        "headers": dict(request.headers),
        "method": request.method,
        "url": str(request.url)
    }
    
    print("\n=== Erro de Validação ===")
    print(f"URL: {request.url}")
    print(f"Método: {request.method}")
    print("Headers:", dict(request.headers))
    print("Detalhes do erro:", exc.errors())
    print("=== Fim do Erro ===\n")
    
    return JSONResponse(
        status_code=422,
        content=error_details
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

# Rota raiz
@app.get("/", include_in_schema=True)
@app.head("/", include_in_schema=True)
async def read_root():
    """Rota raiz que retorna informações básicas sobre a API"""
    return {
        "message": "Bem-vindo à Smart Shelf API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "analyze_shelf": "/analyze",
            "export_to_sheets": "/export-to-sheets",
            "get_stats": "/stats",
            "get_logs": "/logs"
        }
    }

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
    image: UploadFile = File(None),
    file: UploadFile = File(None),
    produtos: str = Form(...)
):
    """
    Analisa a imagem da prateleira usando o Google Gemini.
    
    - image/file: arquivo de imagem (pode usar qualquer um dos campos)
    - produtos: string JSON no formato '[{"nome": "Produto 1", "descricao": "Descrição 1"}]'
    """
    print("\n=== Nova Análise Iniciada ===")
    
    # Usa o campo 'file' se 'image' não for fornecido
    upload_file = image if image is not None else file
    if upload_file is None:
        raise HTTPException(status_code=400, detail="É necessário enviar uma imagem no campo 'image' ou 'file'")
    
    print(f"Tipo do arquivo: {upload_file.content_type}")
    print(f"Nome do arquivo: {upload_file.filename}")
    
    start_time = time.time()
    try:
        # Ler a imagem uma única vez
        image_data = await upload_file.read()
        print(f"Tamanho do arquivo: {len(image_data)} bytes")
        
        # Validar produtos
        try:
            produtos_list = json.loads(produtos)
            print("\nProdutos recebidos:", json.dumps(produtos_list, indent=2, ensure_ascii=False))
            
            if not isinstance(produtos_list, list):
                raise ValueError("O campo 'produtos' deve ser uma lista")
            
            for produto in produtos_list:
                if not isinstance(produto, dict):
                    raise ValueError("Cada produto deve ser um objeto")
                if 'nome' not in produto or 'descricao' not in produto:
                    raise ValueError("Cada produto deve ter 'nome' e 'descricao'")
                
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Formato inválido da lista de produtos")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Preparar a imagem para o Gemini
        image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
        
        # Formatar o prompt com os produtos
        produtos_nomes = ", ".join([p['nome'] for p in produtos_list])
        prompt_formatado = PROMPTS['default'].format(produtos=produtos_nomes)
        
        # Fazer a análise com timeout aumentado
        response = await asyncio.wait_for(
            model.generate_content_async(
                contents=[prompt_formatado, image_parts[0]],
                generation_config={
                    'temperature': 0.1,
                    'top_p': 0.8,
                    'max_output_tokens': 300,
                }
            ),
            timeout=120
        )
        
        # Processar resposta
        response_text = response.text
        print("\nResposta do Gemini:", response_text)
        
        # Extrair resultados da validação
        validation_text = response_text.split("Validação dos critérios:")[1].split("Dicas para melhoria:" if "Dicas para melhoria:" in response_text else "Motivos da aprovação:")[0].strip()
        
        # Processar cada critério
        validation_result = ValidationResult(
            nome_marca="Nome/marca: Verdadeiro" in validation_text,
            preco="Etiqueta de preço: Verdadeiro" in validation_text,
            posicionamento="Posicionamento: Verdadeiro" in validation_text,
            organizacao="Organização: Verdadeiro" in validation_text
        )
        
        if "Validada com sucesso" in response_text:
            status = "success"
            details = response_text.split("Motivos da aprovação:")[1].strip()
        else:
            status = "pending"
            details = response_text.split("Dicas para melhoria:")[1].strip()
        
        # Preparar resposta
        result = {
            "status": status,
            "details": details,
            "validation": validation_result,
            "execution_time": time.time() - start_time,
            "cost": 0.0005
        }
        
        # Log do resultado
        try:
            save_log(
                status=status,
                produtos=[p['nome'] for p in produtos_list],
                execution_time=result["execution_time"],
                cost=result["cost"],
                analysis_details=details,
                validation_result=validation_result
            )
        except Exception as e:
            print(f"\nErro ao salvar log: {str(e)}")
        
        print("\n=== Análise Concluída ===")
        return result
        
    except Exception as e:
        error_msg = f"Erro durante a análise: {str(e)}"
        print(f"\nERRO: {error_msg}")
        
        try:
            save_log(
                status="error",
                produtos=[],
                error=error_msg,
                analysis_details={"status": "error", "error": str(e)}
            )
        except Exception as log_error:
            print(f"\nErro ao salvar log de erro: {str(log_error)}")
        
        raise HTTPException(status_code=500, detail=error_msg)

def save_log(status: str, produtos: list, execution_time: float = 0, cost: float = 0, 
            error: str = None, analysis_details: str = None, validation_result: ValidationResult = None):
    """Salva o log da análise no Supabase"""
    try:
        # Preparar dados para o log
        log_data = {
            "status": status,
            "produtos": json.dumps(produtos),
            "execution_time": execution_time,
            "cost": cost,
            "error": error,
            "analysis_details": analysis_details,
            "validation": {
                "nome_marca": validation_result.nome_marca if validation_result else None,
                "preco": validation_result.preco if validation_result else None,
                "posicionamento": validation_result.posicionamento if validation_result else None,
                "organizacao": validation_result.organizacao if validation_result else None
            } if validation_result else None,
            "created_at": datetime.now().isoformat()
        }

        # Remover campos None
        log_data = {k: v for k, v in log_data.items() if v is not None}

        # Salvar no Supabase
        supabase.table("logs").insert(log_data).execute()
        print("\nLog salvo com sucesso!")

    except Exception as e:
        print(f"\nErro ao salvar log no Supabase: {str(e)}")
        raise

@app.post("/export-to-sheets", response_model=dict)
async def export_to_sheets(spreadsheet_id: str = Query(..., description="ID da planilha do Google Sheets para exportar os logs")):
    """
    Exporta os logs de análise para uma planilha do Google Sheets.
    
    - **spreadsheet_id**: ID da planilha (encontrado na URL do Google Sheets)
    
    Retorna:
    - **message**: Mensagem de sucesso
    - **rows_updated**: Número de linhas atualizadas
    """
    try:
        # Buscar logs do Supabase
        response = supabase.table('logs').select('*').order('id', desc=True).execute()
        logs = response.data

        # Preparar dados para a planilha
        header = [['ID', 'Status', 'Produtos', 'Tempo de Execução (s)', 'Custo ($)', 'Erro']]
        rows = []
        for log in logs:
            # Formatar produtos como string
            produtos_str = log['produtos'] if isinstance(log['produtos'], str) else json.dumps(log['produtos'])
            
            row = [
                str(log['id']),
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

@app.get("/stats")
async def get_stats():
    """Retorna estatísticas das análises"""
    response = supabase.table('logs').select('*').execute()
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
async def get_logs(limit: int = 10):
    """Retorna os últimos logs de análise"""
    try:
        query = supabase.table('logs').select('*')
        response = query.order('id', desc=True).limit(limit).execute()
        logs = response.data

        # Formatar logs para exibição
        formatted_logs = []
        for log in logs:
            produtos_str = log['produtos'] if isinstance(log['produtos'], str) else json.dumps(log['produtos'])
            
            formatted_log = {
                'id': log['id'],
                'status': log['status'],
                'produtos': produtos_str,
                'execution_time': f"{log['execution_time']:.2f}" if log['execution_time'] else '',
                'cost': f"${log['cost']:.4f}" if log['cost'] else '',
                'error': log['error'] if log['error'] else ''
            }
            formatted_logs.append(formatted_log)

        return formatted_logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar logs: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

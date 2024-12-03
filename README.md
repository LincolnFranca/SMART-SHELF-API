# SMART-SHELF-API
API para análise de prateleiras usando IA (Google Gemini).

## Endpoints

### 1. Análise de Prateleira (`/analyze`)
- **Método**: POST
- **URL**: `https://smart-shelf-api.onrender.com/analyze`

**Parâmetros**:
- `file`: Arquivo de imagem (JPG, PNG)
- `produtos`: Lista de produtos em formato JSON (máximo 3 produtos)
- `analysis_type`: "Rápida" ou "Completa"

**Formato dos Produtos**:
```json
[
    {
        "nome": "Nome do Produto 1",
        "descricao": "Descrição do Produto 1"
    },
    {
        "nome": "Nome do Produto 2",
        "descricao": "Descrição do Produto 2"
    }
]
```

**Exemplo de uso (JavaScript)**:
```javascript
async function analyzeShelf(imageFile, produtos) {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('analysis_type', 'Rápida');
    formData.append('produtos', JSON.stringify(produtos));

    try {
        const response = await fetch('https://smart-shelf-api.onrender.com/analyze', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Erro:', error);
    }
}

// Exemplo de uso
const produtos = [
    {
        nome: "Produto A",
        descricao: "Descrição do produto A"
    },
    {
        nome: "Produto B",
        descricao: "Descrição do produto B"
    }
];

// Com um input de arquivo
const input = document.querySelector('input[type="file"]');
input.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    const analysis = await analyzeShelf(file, produtos);
    console.log(analysis);
});
```

**Resposta**:
```json
{
    "analysis": "Texto da análise...",
    "cost": 0.0005,
    "execution_time": 1.2
}
```

### 2. Estatísticas (`/stats`)
- **Método**: GET
- **URL**: `https://smart-shelf-api.onrender.com/stats`

**Exemplo de uso**:
```javascript
async function getStats() {
    try {
        const response = await fetch('https://smart-shelf-api.onrender.com/stats');
        const stats = await response.json();
        return stats;
    } catch (error) {
        console.error('Erro:', error);
    }
}
```

## Tipos de Análise

### Análise Rápida
- Presença dos produtos selecionados
- Quantidade aproximada
- Estado de organização
- Necessidade de reposição
- Ocupação total da prateleira
- Principais problemas
- Ação mais urgente

### Análise Completa
- Análise detalhada de cada produto
- Localização na prateleira
- Quantidade e disposição
- Estado de conservação
- Visibilidade para o cliente
- Sugestões de melhoria
- Análise geral da prateleira
- Sugestões de layout

## Observações Importantes
1. Máximo de 3 produtos por análise
2. Tamanho máximo da imagem: 10MB
3. Formatos aceitos: JPG, PNG
4. A primeira requisição pode ser lenta (15-30s)
5. Use a documentação interativa: `/docs`

## Documentação Interativa
Para testar a API diretamente no navegador:
https://smart-shelf-api.onrender.com/docs

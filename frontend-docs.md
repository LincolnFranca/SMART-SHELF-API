# Smart Shelf API - Documentação Frontend

## Endpoints Disponíveis

### 1. Análise de Prateleira
**Endpoint**: `POST /analyze`  
**URL**: `https://smart-shelf-api.onrender.com/analyze`

**Parâmetros**:
- `file`: Arquivo de imagem (JPG, PNG)
- `produtos`: Lista de produtos (máximo 3)
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

**Exemplo de Implementação**:
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

// Com input de arquivo
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

### 2. Estatísticas
**Endpoint**: `GET /stats`  
**URL**: `https://smart-shelf-api.onrender.com/stats`

**Exemplo de Implementação**:
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

## Limitações e Observações
1. Máximo de 3 produtos por análise
2. Tamanho máximo da imagem: 10MB
3. Formatos aceitos: JPG, PNG
4. A primeira requisição pode ser lenta (15-30s)

## Suporte
Em caso de dúvidas ou problemas, entre em contato com a equipe de desenvolvimento.

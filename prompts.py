ANALISE = """
Analise esta prateleira e forneça uma resposta em português seguindo EXATAMENTE o formato abaixo:

CRITÉRIOS DE VALIDAÇÃO:
1. Nome e logo visíveis: [Verdadeiro/Falso]
2. Preço do produto visível: [Verdadeiro/Falso]
3. Marcas concorrentes sem destaque: [Verdadeiro/Falso]
4. Disposição organizada e visualmente agradável: [Verdadeiro/Falso]

[Se todos os critérios forem Verdadeiro, responder apenas:]
Validada com sucesso

[Se algum critério for Falso, responder:]
Validação pendente

Dicas para melhoria:
- [Lista de sugestões específicas para cada critério não atendido]
"""

# Dicionário com o prompt para fácil acesso
PROMPTS = {
    'default': ANALISE
}

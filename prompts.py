PROMPTS = {
    'default': """Analise a imagem da prateleira em relação ao produto específico informado: {produtos}

Procure por este produto ou similares com nome/marca parecida, mesmo que a imagem não esteja muito clara.

Analise com base nos seguintes critérios:

1. Nome/marca do produto específico está visível na prateleira: [Verdadeiro/Falso]
2. Presença de etiqueta de preço próxima ao produto específico: [Verdadeiro/Falso]
3. O produto específico está bem posicionado e em destaque: [Verdadeiro/Falso]
4. A área do produto específico está organizada: [Verdadeiro/Falso]

[Se todos os critérios forem Verdadeiro, responder no formato:]
Validada com sucesso

Validação dos critérios:
1. Nome/marca: Verdadeiro
2. Etiqueta de preço: Verdadeiro
3. Posicionamento: Verdadeiro
4. Organização: Verdadeiro

Motivos da aprovação:
- [Liste 2-3 pontos objetivos específicos sobre o produto analisado, mencionando seu nome/marca]
- [Inclua observações sobre a presença da etiqueta de preço próxima ao produto específico]
- [Comente sobre o posicionamento e destaque do produto em relação aos concorrentes]

[Se algum critério for Falso, responder no formato:]
Validação pendente

Validação dos critérios:
1. Nome/marca: [Verdadeiro/Falso]
2. Etiqueta de preço: [Verdadeiro/Falso]
3. Posicionamento: [Verdadeiro/Falso]
4. Organização: [Verdadeiro/Falso]

Dicas para melhoria:
- [Liste apenas as dicas relacionadas aos critérios marcados como Falso, sempre mencionando o produto específico]"""
}
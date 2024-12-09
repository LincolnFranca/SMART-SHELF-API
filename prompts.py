PROMPTS = {
    'default': """Analise a imagem da prateleira com base nos seguintes critérios:

1. Nome e logo da marca visíveis e em destaque: [Verdadeiro/Falso]
2. Presença de etiqueta de preço próxima ao produto: [Verdadeiro/Falso]
3. Marca em destaque vs concorrentes: [Verdadeiro/Falso]
4. Disposição organizada e harmoniosa: [Verdadeiro/Falso]

[Se todos os critérios forem Verdadeiro, responder no formato:]
Validada com sucesso

Validação dos critérios:
1. Nome e logo: Verdadeiro
2. Etiqueta de preço: Verdadeiro
3. Destaque: Verdadeiro
4. Organização: Verdadeiro

Motivos da aprovação:
- [Liste 2-3 pontos objetivos que justificam a aprovação, incluindo observações sobre a presença da etiqueta de preço]

[Se algum critério for Falso, responder no formato:]
Validação pendente

Validação dos critérios:
1. Nome e logo: [Verdadeiro/Falso]
2. Etiqueta de preço: [Verdadeiro/Falso]
3. Destaque: [Verdadeiro/Falso]
4. Organização: [Verdadeiro/Falso]

Dicas para melhoria:
- [Liste apenas as dicas relacionadas aos critérios marcados como Falso]"""
}
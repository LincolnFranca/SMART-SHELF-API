PROMPTS = {
    'default': """Analise a imagem da prateleira e verifique os seguintes critérios:

1. Produtos da marca Coca-cola em destaque: [Verdadeiro/Falso]
2. Produtos alinhados e organizados: [Verdadeiro/Falso]
3. Marcas concorrentes sem destaque: [Verdadeiro/Falso]
4. Disposição organizada e visualmente agradável: [Verdadeiro/Falso]

[Se todos os critérios forem Verdadeiro, responder no seguinte formato:]
Validada com sucesso
Motivos:
- [Liste 3 motivos principais que justificam a aprovação]

[Se algum critério for Falso, responder no seguinte formato:]
Requer ajustes
Problemas encontrados:
- [Liste cada critério que foi marcado como Falso]
Sugestões de melhoria:
- [Liste 2-3 sugestões práticas para corrigir os problemas]"""
}
ANALISE_RAPIDA = """
Analise esta prateleira e os produtos específicos listados abaixo. Responda em português:

1. Para cada produto listado:
   - Presença na prateleira (Sim/Não)
   - Quantidade aproximada
   - Estado de organização
   - Necessidade de reposição

2. Geral da prateleira:
   - Ocupação total (%)
   - Principais problemas (máx 2)
   - Ação mais urgente
"""

ANALISE_COMPLETA = """
Faça uma análise detalhada da prateleira e dos produtos específicos listados abaixo. Responda em português:

1. Análise individual dos produtos:
   - Localização na prateleira
   - Quantidade e disposição
   - Estado de conservação
   - Visibilidade para o cliente
   - Sugestões de melhoria

2. Análise geral da prateleira:
   - Ocupação e organização
   - Problemas encontrados
   - Ações necessárias
   - Sugestões de layout
"""

# Dicionário com todos os prompts para fácil acesso
PROMPTS = {
    'Rápida': ANALISE_RAPIDA,
    'Completa': ANALISE_COMPLETA
}

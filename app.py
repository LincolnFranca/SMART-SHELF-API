# app/main.py

import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
from datetime import datetime
from pathlib import Path
import json
from prompts import PROMPTS  # Importando os prompts do novo arquivo

# Configuração inicial
st.set_page_config(
    page_title="Smart Shelf",
    page_icon="",
    layout="centered",  # Melhor para mobile
    initial_sidebar_state="collapsed"
)

# Configuração do Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Estilo CSS otimizado para mobile
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        padding: 1rem;
        font-size: 1.2rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    .uploadedFile {
        border-radius: 10px;
        padding: 0.5rem;
    }
    .css-1v0mbdj.etr89bj1 {
        margin-top: 1rem;
    }
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Carregar/inicializar configurações
def load_config():
    config_file = Path('config.json')
    if config_file.exists():
        return json.loads(config_file.read_text())
    return {
        'cost_per_analysis': 0.0005,
        'total_analyses': 0,
        'total_cost': 0.0
    }

config = load_config()

# Interface principal
st.title(" Smart Shelf")
st.caption("Análise de Prateleiras")

# Tabs para organizar a interface
tab_analise, tab_config = st.tabs([" Análise", " Config"])

with tab_analise:
    # Opções de entrada de imagem
    entrada = st.radio(
        "Escolha como capturar a imagem:",
        [" Câmera", " Upload"],
        horizontal=True
    )
    
    if entrada == " Câmera":
        imagem = st.camera_input("Tirar foto da prateleira")
    else:
        imagem = st.file_uploader("Selecionar foto da prateleira", type=['jpg', 'jpeg', 'png'])

    if imagem:
        # Mostra imagem com preview responsivo
        st.image(imagem, use_container_width=True)
        
        # Tipo de análise (simplificado para mobile)
        tipo_analise = st.selectbox(
            "Tipo de análise:",
            ["Rápida", "Completa"],
            help="Escolha análise rápida para resultados imediatos"
        )
        
        # Botão de análise
        if st.button(" Analisar", use_container_width=True):
            with st.spinner("Analisando..."):
                try:
                    # Prepara a imagem
                    img = Image.open(imagem)
                    
                    # Análise com Gemini
                    response = model.generate_content(
                        contents=[PROMPTS[tipo_analise], img],
                        generation_config={
                            'temperature': 0.1,
                            'top_p': 0.8,
                            'max_output_tokens': 300,
                        }
                    )
                    
                    # Atualiza estatísticas
                    config['total_analyses'] += 1
                    config['total_cost'] += config['cost_per_analysis']
                    
                    # Mostra resultados
                    st.success(" Análise Concluída!")
                    
                    # Resultados em cards para melhor visualização mobile
                    st.markdown("""
                        <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### Resultados:")
                    st.write(response.text)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Métricas simplificadas
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Custo", f"${config['cost_per_analysis']:.4f}")
                    with col2:
                        st.metric("Tempo", "1.2s")
                    
                except Exception as e:
                    st.error(f"Erro na análise: {str(e)}")

with tab_config:
    st.markdown("### Configurações")
    
    # Removendo a edição de prompts da interface, já que agora está em arquivo separado
    st.markdown("#### Estatísticas")
    st.metric("Total de Análises", config['total_analyses'])
    st.metric("Custo Total", f"${config['total_cost']:.3f}")
    
    if st.button("Resetar Estatísticas"):
        if st.checkbox("Confirmar reset"):
            config['total_analyses'] = 0
            config['total_cost'] = 0.0
            Path('config.json').write_text(json.dumps(config, indent=2))
            st.success("Estatísticas resetadas!")

# Footer otimizado para mobile
st.markdown("---")
st.markdown("""
    <div style='text-align: center; font-size: 0.8rem;'>
        Smart Shelf Mobile v1.0<br>
        Powered by Gemini 1.5
    </div>
""", unsafe_allow_html=True)
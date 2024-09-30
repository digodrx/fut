import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import streamlit as st
import os

# Função para extrair coordenadas (latitude, longitude) de um arquivo GPX
def extrair_trajeto_gpx(content):
    root = ET.fromstring(content)
    trajeto = []
    
    # Iterando sobre os pontos de track (trkpt) no GPX
    for trkpt in root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt'):
        lat = trkpt.get('lat')
        lon = trkpt.get('lon')
        trajeto.append((float(lat), float(lon)))
    
    return trajeto

# Função para desenhar o trajeto e salvar como imagem
def salvar_trajeto_como_imagem(trajeto, cor_hex='#000000', linewidth=5, image_path='trajeto_gpx.png'):
    latitudes, longitudes = zip(*trajeto)
    
    # Aqui a espessura da linha é definida
    plt.plot(longitudes, latitudes, color=cor_hex, linewidth=linewidth)  # Agora a espessura da linha é ajustada
    plt.axis('off')  # Remove os eixos
    plt.savefig(image_path, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"Imagem salva em: {image_path}")

# Configuração da interface Streamlit
st.title('Visualizador de Trajeto GPX')

# Upload do arquivo GPX
uploaded_file = st.file_uploader("Escolha um arquivo GPX", type="gpx")

if uploaded_file is not None:
    # Leitura do conteúdo do arquivo GPX
    gpx_content = uploaded_file.read().decode("utf-8")
    
    # Extração do trajeto
    trajeto = extrair_trajeto_gpx(gpx_content)
    
    # Configurações de cor e espessura
    cor_hex = st.color_picker('Escolha a cor da linha do trajeto', '#FF5733')
    linewidth = st.slider('Escolha a espessura da linha', min_value=1, max_value=10, value=5)

    # Caminho temporário para salvar a imagem
    output_image_path = 'trajeto_gpx.png'
    
    # Gerar e salvar o gráfico
    salvar_trajeto_como_imagem(trajeto, cor_hex=cor_hex, linewidth=linewidth, image_path=output_image_path)
    
    # Mostrar o gráfico gerado
    st.image(output_image_path, caption='Trajeto Gerado', use_column_width=True)
    
    # Opção para download
    with open(output_image_path, "rb") as file:
        btn = st.download_button(
            label="Baixar imagem do trajeto",
            data=file,
            file_name="trajeto_gpx.png",
            mime="image/png"
        )

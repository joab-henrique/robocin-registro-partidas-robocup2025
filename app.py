# app.py (VERSÃO FINAL E CORRETA)

import base64  # Importante: Adicione esta linha no topo
from flask import Flask, render_template, request, flash, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import io
import os
import copy

app = Flask(__name__)
app.secret_key = 'uma_chave_secreta_muito_segura_e_longa_para_producao'


# ----- TEMPLATES SIMULAÇÃO 2D -----
CAMINHO_TEMPLATE_IMAGEM_2D_VITORIA = 'images/template_2d_vitoria.png'
CAMINHO_TEMPLATE_IMAGEM_2D_EMPATE = 'images/template_2d_empate.png'
CAMINHO_TEMPLATE_IMAGEM_2D_DERROTA = 'images/template_2d_derrota.png'

# ----- TEMPLATES SSL -----
CAMINHO_TEMPLATE_IMAGEM_SSL_VITORIA = 'images/template_ssl_vitoria.png'
CAMINHO_TEMPLATE_IMAGEM_SSL_EMPATE = 'images/template_ssl_empate.png'
CAMINHO_TEMPLATE_IMAGEM_SSL_DERROTA = 'images/template_ssl_derrota.png'

# ----- TEMPLATES ARM CHALLENGE -----
CAMINHO_TEMPLATE_IMAGEM_ARM_VITORIA = 'images/template_arm_vitoria.png'
CAMINHO_TEMPLATE_IMAGEM_ARM_EMPATE = 'images/template_arm_empate.png'
CAMINHO_TEMPLATE_IMAGEM_ARM_DERROTA = 'images/template_arm_derrota.png'

CAMINHO_FONTE = 'fonts/Manrope-Bold.ttf'

CONFIGURACOES_TEXTO = {
    'resultado': {'posicao': (200, 750), 'tamanho_fonte': 160, 'cor': (249, 249, 249)},
    'nosso_placar': {'posicao': (200, 1480), 'tamanho_fonte': 60, 'cor': (255, 255, 255)},
    'placar_adversario': {'posicao': (700, 1480), 'tamanho_fonte': 60, 'cor': (255, 255, 255)},
}

def criar_imagem_partida(categoria, equipe_rival, nosso_placar, placar_adversario):
    resultado = ''
    if nosso_placar > placar_adversario:
        resultado = 'VITÓRIA'
    elif nosso_placar < placar_adversario:
        resultado = 'DERROTA'
    else:
        resultado = 'EMPATE'

    imagem_path = ''
    if categoria == '2D':
        if resultado == 'VITÓRIA':
            imagem_path = CAMINHO_TEMPLATE_IMAGEM_2D_VITORIA
        elif resultado == 'EMPATE':
            imagem_path = CAMINHO_TEMPLATE_IMAGEM_2D_EMPATE
        else:
            imagem_path = CAMINHO_TEMPLATE_IMAGEM_2D_DERROTA
    elif categoria == 'SSL':
        if resultado == 'VITÓRIA':
            imagem_path = CAMINHO_TEMPLATE_IMAGEM_SSL_VITORIA
        elif resultado == 'EMPATE':
            imagem_path = CAMINHO_TEMPLATE_IMAGEM_SSL_EMPATE
        else:
            imagem_path = CAMINHO_TEMPLATE_IMAGEM_SSL_DERROTA
    elif categoria == 'ARM':
        if resultado == 'VITÓRIA':
            imagem_path = CAMINHO_TEMPLATE_IMAGEM_ARM_VITORIA
        elif resultado == 'EMPATE':
            imagem_path = CAMINHO_TEMPLATE_IMAGEM_ARM_EMPATE
        else:
            imagem_path = CAMINHO_TEMPLATE_IMAGEM_ARM_DERROTA

    try:
        imagem = Image.open(imagem_path).convert("RGBA")
    except FileNotFoundError:
        raise FileNotFoundError(f"Template de imagem não encontrado em: {imagem_path}")

    desenho = ImageDraw.Draw(imagem)
    config_texto = copy.deepcopy(CONFIGURACOES_TEXTO)

    def desenhar_texto(nome_campo, texto_para_escrever):
        config = config_texto[nome_campo]
        try:
            fonte = ImageFont.truetype(CAMINHO_FONTE, config['tamanho_fonte'])
        except IOError:
            fonte = ImageFont.load_default(size=config['tamanho_fonte'])
        desenho.text(config['posicao'], texto_para_escrever, font=fonte, fill=config['cor'])

    CAMINHO_LOGO = f'images/{equipe_rival}.png'
    if os.path.exists(CAMINHO_LOGO):
        adicionar_logo_adversario(imagem, CAMINHO_LOGO, posicao=(610, 1190), tamanho=(200, 200))

    desenhar_texto('nosso_placar', str(nosso_placar))
    desenhar_texto('placar_adversario', str(placar_adversario))

    buffer_imagem = io.BytesIO()
    imagem.save(buffer_imagem, 'PNG')
    buffer_imagem.seek(0)
    return buffer_imagem

def adicionar_logo_adversario(imagem_base, caminho_imagem_sobreposta, posicao, tamanho):
    with Image.open(caminho_imagem_sobreposta).convert("RGBA") as sobreposta:
        sobreposta = sobreposta.resize(tamanho)
        imagem_base.paste(sobreposta, posicao, sobreposta)

@app.route('/')
def principal():
    return render_template('index.html')

@app.route('/submit_form', methods=['POST'])
def enviar_formulario():
    if request.method == 'POST':
        categoria = request.form.get('categoria')
        equipe_rival = request.form.get('equipe_rival')
        nosso_placar = request.form.get('placar_equipe')
        placar_adversario = request.form.get('placar_adversario')

        if not all([categoria, equipe_rival, nosso_placar, placar_adversario]):
            flash('Por favor, preencha todos os campos do formulário.')
            return redirect(url_for('principal'))

        try:
            # 1. Cria a imagem na memória
            buffer_imagem_editada = criar_imagem_partida(
                categoria, equipe_rival, int(nosso_placar), int(placar_adversario)
            )

            # 2. Codifica a imagem para uma string de texto (Base64)
            imagem_b64 = base64.b64encode(buffer_imagem_editada.getvalue()).decode('utf-8')

            # 3. Renderiza a página de resultado e passa a imagem para ela
            return render_template('resultado.html', imagem_gerada=imagem_b64)

        except FileNotFoundError as e:
            flash(f"Erro de arquivo: {e}. Verifique se os templates e logos estão nos caminhos corretos.")
            return redirect(url_for('principal'))
        except Exception as e:
            flash(f'Ocorreu um erro inesperado ao gerar a imagem: {e}')
            return redirect(url_for('principal'))

if __name__ == '__main__':
    app.run(debug=True)
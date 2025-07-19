import base64
from flask import Flask, render_template, request, flash, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)
app.secret_key = 'uma_chave_secreta_muito_segura_e_longa_para_producao'

# ----- CAMINHOS DOS TEMPLATES -----
CAMINHO_TEMPLATE_2D_VITORIA = 'images/template_2d_vitoria.png'
CAMINHO_TEMPLATE_2D_EMPATE = 'images/template_2d_empate.png'
CAMINHO_TEMPLATE_2D_DERROTA = 'images/template_2d_derrota.png'
CAMINHO_TEMPLATE_IMAGEM_SSL_VITORIA = 'images/template_ssl_vitoria.png'
CAMINHO_TEMPLATE_IMAGEM_SSL_EMPATE = 'images/template_ssl_empate.png'
CAMINHO_TEMPLATE_IMAGEM_SSL_DERROTA = 'images/template_ssl_derrota.png'
CAMINHO_TEMPLATE_IMAGEM_ARM_VITORIA = 'images/template_arm_vitoria.png'
CAMINHO_TEMPLATE_IMAGEM_ARM_EMPATE = 'images/template_arm_empate.png'
CAMINHO_TEMPLATE_IMAGEM_ARM_DERROTA = 'images/template_arm_derrota.png'

# --- FONTES E LOGOS ---
CAMINHO_FONTE = 'fonts/Manrope-Bold.ttf'

# --- CONFIGURAÇÕES PARA JOGOS SIMPLES (1 JOGO 2D, SSL, ARM) ---
CONFIGURACOES_JOGO_UNICO = {
    'resultado': {'posicao': (200, 750), 'tamanho_fonte': 160, 'cor': (249, 249, 249)},
    'nosso_placar': {'posicao': (200, 1480), 'tamanho_fonte': 60, 'cor': (255, 255, 255)},
    'placar_adversario': {'posicao': (700, 1480), 'tamanho_fonte': 60, 'cor': (255, 255, 255)},
    'logo_adversario': {'posicao': (610, 1190), 'tamanho': (200, 200)}
}

# --- CONFIGURAÇÕES AJUSTADAS PARA SIMULAÇÃO 2D (MÚLTIPLOS JOGOS) ---
CONFIGURACOES_2D_MULTI = {
    '2': {
        'caminho_template': 'images/template_resultados_2d_2.png', 
        'tamanho_fonte': 50, 
        'tamanho_logo': (130, 130),
        'partidas': [
            {'nosso_placar': (935,980), 'logo_rival': (625, 810), 'placar_rival': (670,980)},
            {'nosso_placar': (140, 1262), 'logo_rival': (350, 1100), 'placar_rival': (400, 1262)},
        ]
    },
    '3': { # PRECISA AJUSTAR TODAS AS INFOS, ATE TAMANHO DA LOGO!!!!!!!!!!!!
        'caminho_template': 'images/template_resultados_2d_3.png', 
        'tamanho_fonte': 70,
        'tamanho_logo': (140, 140),
        'partidas': [
            {'nosso_placar': (270, 660), 'logo_rival': (725, 580), 'placar_rival': (765, 660)},
            {'nosso_placar': (270, 930), 'logo_rival': (725, 850), 'placar_rival': (765, 930)},
            {'nosso_placar': (270, 1200), 'logo_rival': (725, 1120), 'placar_rival': (765, 1200)},
        ]
    },
    '4': {
        'caminho_template': 'images/template_resultados_2d_4.png', 
        'tamanho_fonte': 50,
        'tamanho_logo': (130, 130),
        'partidas': [
            {'nosso_placar': (935, 865), 'logo_rival': (630, 700), 'placar_rival': (680, 865)},
            {'nosso_placar': (140, 1085), 'logo_rival': (352, 920), 'placar_rival': (400, 1085)},
            {'nosso_placar': (935, 1340), 'logo_rival': (630, 1180), 'placar_rival': (680, 1340)},
            {'nosso_placar': (140, 1607), 'logo_rival': (352, 1440), 'placar_rival': (400, 1607)},
        ]
    },
    '5': { # PRECISA AJUSTAR TODAS AS INFOS, ATE TAMANHO DA LOGO!!!!!!!!!!!!
        'caminho_template': 'images/template_resultados_2d_5.png', 
        'tamanho_fonte': 70,
        'tamanho_logo': (140, 140),
        'partidas': [
            {'nosso_placar': (270, 610), 'logo_rival': (725, 530), 'placar_rival': (765, 610)},
            {'nosso_placar': (270, 800), 'logo_rival': (725, 720), 'placar_rival': (765, 800)},
            {'nosso_placar': (270, 990), 'logo_rival': (725, 910), 'placar_rival': (765, 990)},
            {'nosso_placar': (270, 1180), 'logo_rival': (725, 1100), 'placar_rival': (765, 1180)},
            {'nosso_placar': (270, 1370), 'logo_rival': (725, 1290), 'placar_rival': (765, 1370)},
        ]
    }
}

def adicionar_logo(imagem_base, caminho_logo, posicao, tamanho):
    if not os.path.exists(caminho_logo):
        print(f"Aviso: Logo não encontrada em {caminho_logo}, será ignorada.")
        return
    with Image.open(caminho_logo).convert("RGBA") as logo:
        logo = logo.resize(tamanho)
        imagem_base.paste(logo, posicao, logo)

def desenhar_texto(desenho, texto, posicao, fonte, cor):
    desenho.text(posicao, str(texto), font=fonte, fill=cor)

def criar_imagem_2d_multi(num_jogos, dados_partidas):
    config = CONFIGURACOES_2D_MULTI.get(str(num_jogos))
    if not config:
        raise ValueError(f"Configuração para {num_jogos} jogos não encontrada.")

    imagem = Image.open(config['caminho_template']).convert("RGBA")
    desenho = ImageDraw.Draw(imagem)
    try:
        fonte = ImageFont.truetype(CAMINHO_FONTE, config['tamanho_fonte'])
    except IOError:
        fonte = ImageFont.load_default(size=config['tamanho_fonte'])

    tamanho_logo = config['tamanho_logo']

    for i, partida_info in enumerate(config['partidas']):
        dados_partida_atual = dados_partidas[i]
        desenhar_texto(desenho, dados_partida_atual['nosso_placar'], partida_info['nosso_placar'], fonte, (255,255,255))
        caminho_logo_rival = f"images/{dados_partida_atual['equipe_rival']}.png"
        adicionar_logo(imagem, caminho_logo_rival, partida_info['logo_rival'], tamanho_logo)
        desenhar_texto(desenho, dados_partida_atual['placar_rival'], partida_info['placar_rival'], fonte, (255,255,255))
        
    buffer_imagem = io.BytesIO()
    imagem.save(buffer_imagem, 'PNG')
    buffer_imagem.seek(0)
    return buffer_imagem

def criar_imagem_jogo_unico(categoria, nosso_placar, placar_adversario, equipe_rival):
    if nosso_placar > placar_adversario: resultado_tipo = 'VITORIA'
    elif nosso_placar < placar_adversario: resultado_tipo = 'DERROTA'
    else: resultado_tipo = 'EMPATE'

    if categoria == '2D':
        caminho_template_base = f'CAMINHO_TEMPLATE_2D_{resultado_tipo}'
    else:
        caminho_template_base = f'CAMINHO_TEMPLATE_IMAGEM_{categoria.upper()}_{resultado_tipo}'
    
    caminho_template = globals()[caminho_template_base]

    imagem = Image.open(caminho_template).convert("RGBA")
    desenho = ImageDraw.Draw(imagem)

    for campo, config in CONFIGURACOES_JOGO_UNICO.items():
        if campo == 'resultado':
            continue
        if 'logo' in campo: continue
        try:
            fonte = ImageFont.truetype(CAMINHO_FONTE, config['tamanho_fonte'])
        except IOError:
            fonte = ImageFont.load_default(size=config['tamanho_fonte'])
        
        texto_para_escrever = ''
        if campo == 'nosso_placar':
            texto_para_escrever = str(nosso_placar)
        elif campo == 'placar_adversario':
            texto_para_escrever = str(placar_adversario)
        
        if texto_para_escrever:
            desenhar_texto(desenho, texto_para_escrever, config['posicao'], fonte, config['cor'])

    logo_config = CONFIGURACOES_JOGO_UNICO['logo_adversario']
    caminho_logo_rival = f"images/{equipe_rival}.png"
    adicionar_logo(imagem, caminho_logo_rival, logo_config['posicao'], logo_config['tamanho'])

    buffer_imagem = io.BytesIO()
    imagem.save(buffer_imagem, 'PNG')
    buffer_imagem.seek(0)
    return buffer_imagem

@app.route('/')
def principal():
    return render_template('index.html')

@app.route('/submit_form', methods=['POST'])
def enviar_formulario():
    try:
        categoria = request.form.get('categoria')

        if categoria == '2D':
            num_jogos_str = request.form.get('num_jogos')
            if not num_jogos_str:
                flash('Por favor, selecione o número de jogos para Simulação 2D.')
                return redirect(url_for('principal'))
            
            num_jogos = int(num_jogos_str)
            
            if num_jogos == 1:
                nosso_placar_str = request.form.get('placar_equipe_2d_simples')
                placar_adversario_str = request.form.get('placar_adversario_2d_simples')
                equipe_rival = request.form.get('equipe_rival_2d_simples')
                if not all([nosso_placar_str, placar_adversario_str, equipe_rival]):
                    flash('Por favor, preencha todos os campos para o jogo.')
                    return redirect(url_for('principal'))
                buffer_imagem_editada = criar_imagem_jogo_unico(
                    '2D', int(nosso_placar_str), int(placar_adversario_str), equipe_rival
                )
            else:
                equipes_rivais = request.form.getlist('equipe_rival[]')
                nossos_placares = request.form.getlist('placar_equipe[]')
                placares_rivais = request.form.getlist('placar_adversario[]')

                if len(equipes_rivais) < num_jogos:
                    flash('Formulário incompleto. Preencha os dados de todas as partidas.')
                    return redirect(url_for('principal'))

                dados_partidas = []
                for i in range(num_jogos):
                    if not all([equipes_rivais[i], nossos_placares[i], placares_rivais[i]]):
                        flash(f"Dados para a Partida {i+1} estão incompletos.")
                        return redirect(url_for('principal'))
                    dados_partidas.append({
                        'equipe_rival': equipes_rivais[i], 'nosso_placar': int(nossos_placares[i]), 'placar_rival': int(placares_rivais[i])
                    })
                buffer_imagem_editada = criar_imagem_2d_multi(num_jogos, dados_partidas)

        elif categoria in ['SSL', 'ARM']:
            nosso_placar_str = request.form.get('placar_equipe_simples')
            placar_adversario_str = request.form.get('placar_adversario_simples')
            equipe_rival = request.form.get('equipe_rival_simples')
            if not all([nosso_placar_str, placar_adversario_str, equipe_rival]):
                flash('Por favor, preencha todos os campos.')
                return redirect(url_for('principal'))
            buffer_imagem_editada = criar_imagem_jogo_unico(
                categoria, int(nosso_placar_str), int(placar_adversario_str), equipe_rival
            )

        else:
            flash('Categoria selecionada é inválida.')
            return redirect(url_for('principal'))

        imagem_b64 = base64.b64encode(buffer_imagem_editada.getvalue()).decode('utf-8')
        return render_template('resultado.html', imagem_gerada=imagem_b64)

    except (FileNotFoundError, ValueError) as e:
        flash(f"Erro de Arquivo ou Valor: {e}")
        return redirect(url_for('principal'))
    except Exception as e:
        error_type = type(e).__name__
        flash(f'Ocorreu um erro inesperado do tipo "{error_type}": {e}')
        return redirect(url_for('principal'))

if __name__ == '__main__':
    app.run(debug=True)
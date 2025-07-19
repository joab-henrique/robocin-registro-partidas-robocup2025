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
TAMANHO_LOGO_RIVAL_2D = (160, 160)

# --- CONFIGURAÇÕES PARA JOGOS SIMPLES (1 JOGO 2D, SSL, ARM) ---
CONFIGURACOES_JOGO_UNICO = {
    'resultado': {'posicao': (200, 750), 'tamanho_fonte': 160, 'cor': (249, 249, 249)},
    'nosso_placar': {'posicao': (200, 1480), 'tamanho_fonte': 60, 'cor': (255, 255, 255)},
    'placar_adversario': {'posicao': (700, 1480), 'tamanho_fonte': 60, 'cor': (255, 255, 255)},
    'logo_adversario': {'posicao': (610, 1190), 'tamanho': (200, 200)}
}

# --- CONFIGURAÇÕES DE POSIÇÃO PARA SIMULAÇÃO 2D (MÚLTIPLOS JOGOS) ---
CONFIGURACOES_2D_MULTI = {
    '2': {'caminho_template': 'images/template_resultados_2d_2.png', 'tamanho_fonte': 80, 'partidas': [
            {'nosso_placar': (200, 810), 'logo_rival': (715, 800), 'placar_rival': (880, 810)},
            {'nosso_placar': (200, 1140), 'logo_rival': (715, 1130), 'placar_rival': (880, 1140)},
        ]},
    '3': {'caminho_template': 'images/template_resultados_2d_3.png', 'tamanho_fonte': 80, 'partidas': [
            {'nosso_placar': (200, 670), 'logo_rival': (715, 660), 'placar_rival': (880, 670)},
            {'nosso_placar': (200, 940), 'logo_rival': (715, 930), 'placar_rival': (880, 940)},
            {'nosso_placar': (200, 1210), 'logo_rival': (715, 1200), 'placar_rival': (880, 1210)},
        ]},
    '4': {'caminho_template': 'images/template_resultados_2d_4.png', 'tamanho_fonte': 80, 'partidas': [
            {'nosso_placar': (170, 640), 'logo_rival': (395, 500), 'placar_rival': (445, 640)},
            {'nosso_placar': (685, 640), 'logo_rival': (915, 500), 'placar_rival': (965, 640)},
            {'nosso_placar': (170, 1160), 'logo_rival': (395, 1020), 'placar_rival': (445, 1160)},
            {'nosso_placar': (685, 1160), 'logo_rival': (915, 1020), 'placar_rival': (965, 1160)},
        ]},
    '5': {'caminho_template': 'images/template_resultados_2d_5.png', 'tamanho_fonte': 80, 'partidas': [
            {'nosso_placar': (200, 620), 'logo_rival': (715, 580), 'placar_rival': (880, 620)},
            {'nosso_placar': (200, 810), 'logo_rival': (715, 770), 'placar_rival': (880, 810)},
            {'nosso_placar': (200, 1000), 'logo_rival': (715, 960), 'placar_rival': (880, 1000)},
            {'nosso_placar': (200, 1190), 'logo_rival': (715, 1150), 'placar_rival': (880, 1190)},
            {'nosso_placar': (200, 1380), 'logo_rival': (715, 1340), 'placar_rival': (880, 1380)},
        ]}
}

# --- FUNÇÕES AUXILIARES ---
def adicionar_logo(imagem_base, caminho_logo, posicao, tamanho):
    if not os.path.exists(caminho_logo):
        print(f"Aviso: Logo não encontrada em {caminho_logo}, será ignorada.")
        return
    with Image.open(caminho_logo).convert("RGBA") as logo:
        logo = logo.resize(tamanho)
        imagem_base.paste(logo, posicao, logo)

def desenhar_texto(desenho, texto, posicao, fonte, cor):
    desenho.text(posicao, str(texto), font=fonte, fill=cor)

# --- FUNÇÕES DE CRIAÇÃO DE IMAGEM ---
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

    for i, partida_info in enumerate(config['partidas']):
        dados_partida_atual = dados_partidas[i]
        desenhar_texto(desenho, dados_partida_atual['nosso_placar'], partida_info['nosso_placar'], fonte, (255,255,255))
        caminho_logo_rival = f"images/{dados_partida_atual['equipe_rival']}.png"
        adicionar_logo(imagem, caminho_logo_rival, partida_info['logo_rival'], TAMANHO_LOGO_RIVAL_2D)
        desenhar_texto(desenho, dados_partida_atual['placar_rival'], partida_info['placar_rival'], fonte, (255,255,255))
        
    buffer_imagem = io.BytesIO()
    imagem.save(buffer_imagem, 'PNG')
    buffer_imagem.seek(0)
    return buffer_imagem

def criar_imagem_jogo_unico(categoria, nosso_placar, placar_adversario, equipe_rival):
    # Determina o TIPO de resultado para escolher o template correto
    if nosso_placar > placar_adversario: resultado_tipo = 'VITORIA'
    elif nosso_placar < placar_adversario: resultado_tipo = 'DERROTA'
    else: resultado_tipo = 'EMPATE'

    caminho_template_base = f'CAMINHO_TEMPLATE_{categoria.upper()}_{resultado_tipo}'
    caminho_template = globals()[caminho_template_base]

    imagem = Image.open(caminho_template).convert("RGBA")
    desenho = ImageDraw.Draw(imagem)

    # Itera sobre as configurações para desenhar APENAS placares e logo
    for campo, config in CONFIGURACOES_JOGO_UNICO.items():
        # **A CORREÇÃO ESTÁ AQUI: Ignora o campo 'resultado' para não desenhá-lo**
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

    # Adiciona a logo do adversário
    logo_config = CONFIGURACOES_JOGO_UNICO['logo_adversario']
    caminho_logo_rival = f"images/{equipe_rival}.png"
    adicionar_logo(imagem, caminho_logo_rival, logo_config['posicao'], logo_config['tamanho'])

    buffer_imagem = io.BytesIO()
    imagem.save(buffer_imagem, 'PNG')
    buffer_imagem.seek(0)
    return buffer_imagem

# --- ROTAS FLASK ---
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
            else: # 2 a 5 jogos
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
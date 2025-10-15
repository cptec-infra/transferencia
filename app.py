import socket
import threading
import time
import plotly.graph_objs as go
import configparser
from gevent.pywsgi import WSGIServer
from urllib.parse import unquote

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from filters.filters import class_status, size_to_human_view
from functions import *
from repositories.user_repository import UserRepository
from repositories.dado_repository import DadoRepository
from models import UsuarioModel

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.ini")

app.secret_key = config.get('FLASK', 'flask_key')

fdt_server = config.get('FDT', 'fdt_server')
fdt_port = config.get('FDT', 'fdt_port')

last_check_fdt = None

# Variáveis globais para controle
background_thread = None
background_thread_dartcom = None
stop_event = threading.Event()
stop_event_dartcom_cba = threading.Event()
stop_event_dartcom_cp = threading.Event()

def run_background_process(process_name, process_function, interval_minutes, stop_event):
    with app.app_context():
        interval_seconds = interval_minutes * 60
        while not stop_event.is_set():
            try:
                print(f'{get_datetime_str()} - Iniciando {process_name}')
                process_function()
                print(f'{get_datetime_str()} - Fim {process_name}')
            except Exception as e:
                print(f"{get_datetime_str()} - Erro no processo {process_name}: {e}")
            stop_event.wait(interval_seconds)
        print(f'{get_datetime_str()} - {process_name} finalizado')

# Inicializando os threads para os processos de background
def start_background_process():
    global background_thread, stop_event
    print(f"{get_datetime_str()} - start_background_process")
    transfer_list.clear()

    stop_event.clear()
    background_thread = threading.Thread(target=run_background_process, args=("background_process", background_process, 2, stop_event))
    background_thread.daemon = True
    background_thread.start()

def start_background_process_dartcom_cba():
    global background_thread_dartcom_cba, stop_event_dartcom_cba
    print(f"{get_datetime_str()} - inicio_thread_background_process_dartcom_cba")

    stop_event_dartcom_cba.clear()
    background_thread_dartcom_cba = threading.Thread(target=run_background_process, args=("background_process_dartcom_cba", background_process_dartcom_cba, 1, stop_event_dartcom_cba))
    background_thread_dartcom_cba.daemon = True
    background_thread_dartcom_cba.start()
    print(f"{get_datetime_str()} - fim_thread_background_process_dartcom_cba")

def start_background_process_dartcom_cp():
    global background_thread_dartcom_cp, stop_event_dartcom_cp
    print(f"{get_datetime_str()} - inicio_thread_background_process_dartcom_cp")

    stop_event_dartcom_cp.clear()
    background_thread_dartcom_cp = threading.Thread(target=run_background_process, args=("background_process_dartcom_cp", background_process_dartcom_cp, 1, stop_event_dartcom_cp))
    background_thread_dartcom_cp.daemon = True
    background_thread_dartcom_cp.start()    
    print(f"{get_datetime_str()} - fim_thread_background_process_dartcom_cp")

def stop_background_process():
    global stop_event, background_thread
    print(f"{get_datetime_str()} - Parando background_process...")
    stop_event.set()

    dado_repository = DadoRepository()
    error_db = dado_repository.delete_dado_executando()
    
    if error_db:
            send_email(subject='Falha ao deletar o dado', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            return render_template('index.html', dados=[], msg='Erro no banco de dados')

    if background_thread:
        background_thread.join(timeout=5)
    print(f"{get_datetime_str()} - background_process parado")

def stop_background_process_dartcom_cba():
    global stop_event_dartcom_cba, background_thread_dartcom_cba
    print(f"{get_datetime_str()} - Parando background_process_dartcom cba...")
    stop_event_dartcom_cba.set()
    if background_thread_dartcom_cba:
        background_thread_dartcom_cba.join(timeout=5)
    print(f"{get_datetime_str()} - background_process_dartcom cba parado")

def stop_background_process_dartcom_cp():
    global stop_event_dartcom_cp, background_thread_dartcom_cp
    print(f"{get_datetime_str()} - Parando background_process_dartcom cp...")
    stop_event_dartcom_cp.set()
    if background_thread_dartcom_cp:
        background_thread_dartcom_cp.join(timeout=5)
    print(f"{get_datetime_str()} - background_process_dartcom cp parado")

# Chama a função para iniciar os threads em paralelo
start_background_process()
start_background_process_dartcom_cba()
start_background_process_dartcom_cp()

@app.route('/', methods=['GET', 'POST'])
def index():    
    if is_logado():
        page = request.args.get('pag', 1, type=int)
        search_data = request.args.get('search', type=str)
        per_page = int(request.args.get('items', 25)) 

        if request.method == 'POST' and 'search-data' in request.form:
            search_data = request.form['search-data']        

        dado_repository = DadoRepository()
        dados, error_db = dado_repository.get_all(search_data)

        if error_db:
            send_email(subject='Falha na rota index', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            return render_template('index.html', dados=[], msg='Erro no banco de dados')
        else:
            dados_paginado, total_pages = pagination(dados, page, per_page)
            return render_template('index.html', dados=dados_paginado, page=page, per_page=per_page, total_pages=total_pages, transfer_list=get_transfer_list(), daily_volume=dado_repository.get_daily_volume(), search_data=search_data)
    else:
        return redirect(url_for('login'))

@app.route('/dartcom', methods=['GET', 'POST'])
def dartcom():    
    if is_logado():
        page = request.args.get('pag', 1, type=int)
        search_data = request.args.get('search', type=str)
        per_page = int(request.args.get('items', 25)) 

        if request.method == 'POST' and 'search-data' in request.form:
            search_data = request.form['search-data']        

        dado_repository = DadoRepository()
        dartcoms, error_db = dado_repository.get_dartcom_all(search_data)

        if error_db:
            send_email(subject='Falha na rota dartcom', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            return render_template('dartcom_index.html', dartcoms=[], msg='Erro no banco de dados')
        else:
            dados_paginado, total_pages = pagination(dartcoms, page, per_page)
            return render_template('dartcom_index.html', dartcoms=dados_paginado, page=page, per_page=per_page, total_pages=total_pages, transfer_list=get_dartcom_list(), daily_volume=dado_repository.get_dartcom_daily_volume(), search_data=search_data)
    else:
        return redirect(url_for('login'))
    
@app.route('/dartcom/<int:id_dartcom>')
def dartcom_dado(id_dartcom):
    if is_logado():
        dado_repository = DadoRepository()
        dartcom, error_db = dado_repository.get_dartcom(id_dartcom=id_dartcom)
        if error_db:
            send_email(subject='Falha na rota dartcom', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            return render_template('dado_dartcom.html', dartcom = dartcom, msg = 'Erro no banco de dados')
        
        historico, error_db = dado_repository.get_dartcom_history(id_dartcom=id_dartcom)
        if error_db:
            send_email(subject='Falha na rota dartcom historico', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            return render_template('dado_dartcom.html', msg = 'Erro no banco de dados')
        
        return render_template('dado_dartcom.html', dartcom = dartcom, historico = historico)
    else:
        return redirect(url_for('login'))

@app.route('/dado/<int:id_dado>')
def dado(id_dado):
    if is_logado():
        dado_repository = DadoRepository()
        dado, error_db = dado_repository.get_data(id=id_dado)
        if error_db:
            send_email(subject='Falha na rota dado', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            return render_template('dado.html', dado = dado, msg = 'Erro no banco de dados')
        
        historico, error_db = dado_repository.get_history(id=id_dado)
        if error_db:
            send_email(subject='Falha na rota dado', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            return render_template('dado.html', msg = 'Erro no banco de dados')
        
        return render_template('dado.html', dado = dado, historico = historico)
    else:
        return redirect(url_for('login'))

@app.route('/errors', methods=['GET', 'POST'])
def errors():
    if is_logado():
        dado_repository = DadoRepository()
        
        if not is_visitante():
            if request.method == 'POST' and 'selected' in request.form:
                selected = request.form['selected'].split(',')
                error_db_retry = dado_repository.set_retry(selected=selected)
                print(error_db_retry)
                if error_db_retry:
                    send_email(subject='Falha ao registrar retry', body=f'Favor verificar o ocorrido.\n\n{error_db_retry}', is_adm=True)
        
        dados, error_db = dado_repository.get_errors()
        if error_db:
            send_email(subject='Falha na rota errors', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            return render_template('errors.html', dados = [], msg = 'Erro no banco de dados')
        else:
            return render_template('errors.html', dados = dados)
    else:
        return redirect(url_for('login'))
    
@app.route('/dartcom/erro', methods=['GET', 'POST'])
def dartcom_erro():
    if is_logado():
        dado_repository = DadoRepository()
        
        if not is_visitante():
            if request.method == 'POST' and 'selected' in request.form:
                selected = request.form['selected'].split(',')
                error_db_retry = dado_repository.set_retry_dartcom(selected=selected)
                if error_db_retry:
                    send_email(subject='Falha ao registrar retry', body=f'Favor verificar o ocorrido.\n\n{error_db_retry}', is_adm=True)
        
        dartcoms, error_db = dado_repository.get_dartcom_errors()
        if error_db:
            send_email(subject='Falha na rota errors', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            return render_template('dartcom_errors.html', dartcoms = [], msg = 'Erro no banco de dartcoms')
        else:
            return render_template('dartcom_errors.html', dartcoms = dartcoms)
    else:
        return redirect(url_for('login'))
    
@app.route('/dartcom/settings', methods=['GET', 'POST'])
def dartcom_settings():
    if is_logado():        
        if is_adm():
            msg = ''
            form = request.form
            dado_repository = DadoRepository()
            
            if request.method == "POST":
                if 'id-antena' in form and 'antena' in form:
                    id = form['id-antena']
                    antena = form['antena']

                    if id:
                        # editar
                        dado_repository.update_antena(id=id, antena=antena)
                    else:
                        # cadastrar a antena
                        dado_repository.insert_antena(antena)

                # elif all(key in form for key in ['id-satelite','antena', 'satelite', 'sensor', 'data-type', 'satelite-path', 'template-name', 'is-compressed', 'epsl0']):
                elif all(key in form for key in ['id-satelite','antena', 'satelite', 'sensor', 'data-type', 'satelite-path', 'template-name']):
                    id = form['id-satelite']
                    id_dartcom_antena = form['antena']
                    nome = form['satelite']
                    sensor = form['sensor']
                    data_type = form['data-type']
                    satelite_path = form['satelite-path']
                    template_name = form['template-name']
                    command = form['command']
                    is_compressed = 1 if form.get('is-compressed') == 'on' else 0
                    is_epsl0 = 1 if form.get('epsl0') == 'on' else 0

                    epsl0_template = form['epsl0-template']

                    satelite = DartcomSateliteModel(id=id, id_dartcom_antena=id_dartcom_antena, nome=nome, sensor=sensor, data_type=data_type, satelite_path=satelite_path, template_name=template_name, command=command, is_compressed=is_compressed, is_epsl0=is_epsl0, epsl0_template=epsl0_template)

                    if id:
                        # editar
                        error_db = dado_repository.update_satelite(id=id, satelite=satelite)
                        if error_db:
                            send_email(subject='Falha ao editar satélite', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
                            msg = 'Falha ao editar satélite'
                    else:
                        #cadastrar
                        msg, error_db = dado_repository.insert_satelite(satelite=satelite)
                        if error_db:
                            send_email(subject='Falha ao cadastrar satélite', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
                            msg = 'Falha ao cadastrar satélite'

            satelites, error_db = dado_repository.get_dartcom_satelites()
            antenas, error_db = dado_repository.get_dartcom_antena()

            return render_template('dartcom_cadastros.html', satelites = satelites, antenas = antenas, msg = msg)
        else:
            return redirect(url_for('dartcom'))    
    else:
        return redirect(url_for('login'))
    
@app.route('/md5_cba_zerados', methods=['GET'])
def md5_cba_zerados():
    if is_logado():
        dado_repository = DadoRepository()
        list_md5, error_db = dado_repository.get_md5_cba_zerados()
        if error_db:
            send_email(subject='Falha na rota md5_cba_zerado', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            return render_template('md5_cba_zerados.html', list_md5 = [], msg = 'Erro no banco de dados')
        else:
            return render_template('md5_cba_zerados.html', list_md5 = list_md5)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form: 
        
        email = request.form['email'] 
        password = gera_hash_MD5(request.form['password'])

        user_repository = UserRepository()

        usuario, first_login, error_db = user_repository.login(email=email, senha=password)

        if error_db:
            send_email(subject='Falha na rota login', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            msg = 'Erro no banco de dados'                
        elif usuario: 
            if first_login:
                if 'new_password' in request.form:
                    new_password = request.form['new_password']
                    hash_new_password = gera_hash_MD5(new_password)
                    user_repository = UserRepository()
                    msg, error_db = user_repository.update_password(email, hash_new_password)
                    
                    if error_db:
                        send_email(subject='Falha no reset de senha', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
                        msg = 'Erro no banco de dados'                    

                    return render_template('login.html', msg = msg)

                else:
                    return render_template('first_login.html', email= email,msg = msg)
            else:
                session['loggedin'] = True
                session['id'] = usuario.id 
                session['nome'] = usuario.nome
                session['perfil'] = usuario.perfil
                session['dark_theme'] = usuario.darkTheme == 1
                msg = 'Logado com sucesso!'
                return redirect(url_for('index'))
        else: 
            msg = 'Login ou senha incorretos!'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None) 
    session.pop('id', None) 
    session.pop('nome', None) 
    session.pop('perfil', None)
    session.pop('dark_theme', None)
    return redirect(url_for('login'))

@app.route('/reset_password', methods=['POST'])
def reset_password():
    msg = ''
    if request.method == 'POST' and 'email' in request.form: 
        email = request.form['email'] 
        user_repository = UserRepository()
        usuario, error_db = user_repository.reset(email)

        if error_db:
            send_email(subject='Falha no reset de senha', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            msg = 'Erro no banco de dados'

        elif usuario:
            s = URLSafeTimedSerializer(key_reset_password)
            token = s.dumps(email, salt='reset-passwd')
            link = 'http://150.163.212.53/password/' + token
            #link = url_for('password', token=token, _external=True)
            body=f"Prezado {usuario.nome},\n\nPara concluir seu reset de senha, favor acessar o link abaixo em até 30 minutos: \n\n{link}\n\nAtenciosamente,\nCOIDS."
            subject = 'Reset de senha de acesso portal de transferências'
            msg, e = send_email_user(email, body, subject)

            if e:
                send_email(subject='Falha ao enviar o email para o usuário', body=f'Favor verificar o ocorrido.\n\n{e}', is_adm=True)
        else:  
            msg = f"Email {email} não foi encontrado na base de dados."
    return render_template('login.html', msg = msg)

@app.route('/password/<token>', methods=['GET', 'POST'])
def password(token):
    token_valided, token_email = verify_token(token)

    # Valida o token
    if not token_valided:
        msg = 'Token inválido, Favor realizar o processo novamente.'
        return render_template('login.html', msg = msg)

    # Faz o update da senha no bd
    if request.method == 'POST':
        email = request.form['email']
        if email != token_email:
            msg = 'Não foi possível validar o e-mail.'
            return render_template('login.html', msg = msg)
        
        password = gera_hash_MD5(request.form['new_password'])

        user_repository = UserRepository()
        msg, error_db = user_repository.update_password(email, password)
        
        if error_db:
            send_email(subject='Falha no reset de senha', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            msg = 'Erro no banco de dados'
        
        return render_template('login.html', msg = msg)
    
    return render_template('password.html', email=token_email, token=token)

@app.route('/users', methods=['GET', 'POST'])
def users():
    if is_logado():        
        if is_adm():
            msg = ''
            form = request.form

            user_repository = UserRepository()
            if request.method == 'POST' and 'id-usuario' in form and 'nome' in form and 'email' in form and 'perfil' in form:
                id = form['id-usuario']
                nome = form['nome']
                email = form['email']
                senha = generate_random_password()
                senha_hash = gera_hash_MD5(senha)
                empresa = form['empresa']
                ativo = 'ativo' in form
                perfil = form['perfil']
                user = UsuarioModel(id=id, nome=nome, email=email, senha=senha_hash, empresa=empresa, perfil=perfil, ativo=ativo)

                if nome == '' or empresa == ''  or email == '':
                    msg = 'Informe todos os campos'
                else:
                    if id:
                        # Editar
                        error_db = user_repository.update(user=user)
                        if error_db:
                            send_email(subject='Falha ao editar usuário', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
                            msg = 'Falha ao editar usuário'
                    else:
                        # Cadastrar
                        msg, error_db = user_repository.insert(user=user)
                        if error_db:
                            send_email(subject='Falha ao cadastrar usuário', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
                            msg = 'Falha ao cadastrar usuário'
                        else:
                            body=f"Prezado {nome},\n\nSua conta foi criada.\n\nAgora é só logar na aplicação de transferência http://150.163.212.53 utilizando a VPN COIDS.\n\nuser: {email}\npassword: {senha}\n\nNo primeiro acesso será solicitada a troca de senha.\n\nDúvidas e problemas com o acesso, por favor entrar em contato com o Help Desk no e-mail helpdesk.cptec@inpe.br ou pelo telefone (12)3186-8476\n\nAtenciosamente,\nCOIDS."
                            subject = 'Conta criada'
                            send_email_user(email=email, body=body, subject=subject)

            usuarios = user_repository.get_all()

            return render_template('usuarios.html', usuarios = usuarios, msg = msg)
        else:
            return redirect(url_for('index'))    
    else:
        return redirect(url_for('login'))
   
@app.route('/relatorio', methods=['GET', 'POST'])
def relatorio(date_start=None, date_end=None, daily_volume=None, grafico_volume_json = None, grafico_quantidade_json = None, grafico_satellite_json = None, grafico_tempo_json = None,  msg = None, dados=[]):
    if is_logado():
        date_start = request.args.get('start')
        date_end = request.args.get('end')
        
        if request.method == 'POST':
            date_start = request.form['date-start']
            date_end = request.form['date-end']

        if date_start or date_end:
            dado_repository = DadoRepository()
            dados, error_db, volume_for_date, quantidade_for_date, satellite_for_date, tempo_for_date_downlaod, tempo_for_date_armazenamento = dado_repository.get_report_data(date_start, date_end)
            if error_db:
                send_email(subject='Falha na rota /relatorio', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
                msg = 'Erro no banco de dados'
            else:
                daily_volume = dado_repository.get_daily_volume(date_start, date_end)
                if volume_for_date is None:
                    volume_for_date = []
                grafico_volume_json, volume_fig = create_graph_volume(volume_for_date)
                grafico_quantidade_json, quantidade_fig = create_graph_quantity(quantidade_for_date)
                grafico_satellite_json, satellite_fig = create_graph_satellite(satellite_for_date)    
                grafico_tempo_json, tempo_fig = create_graph_time(tempo_for_date_downlaod, tempo_for_date_armazenamento, 'Download')    

                if request.args.get('download'):
                    return create_pdf(dados=dados, daily_volume=daily_volume, date_start=date_start, date_end=date_end,volume_fig=volume_fig,quantidade_fig=quantidade_fig,satellite_fig=satellite_fig, tempo_fig=tempo_fig)                         
                          
        return render_template('relatorio.html', dados=dados, daily_volume=daily_volume, date_start=date_start, date_end=date_end, grafico_volume=grafico_volume_json, grafico_quantidade=grafico_quantidade_json, grafico_satellite=grafico_satellite_json, grafico_tempo=grafico_tempo_json, msg=msg)
    else:
        return redirect(url_for('login'))
    
@app.route('/dartcom/relatorio', methods=['GET', 'POST'])
def dartcom_relatorio(date_start=None, date_end=None, daily_volume=None, grafico_volume_json = None, grafico_quantidade_json = None, grafico_satellite_json = None, grafico_tempo_json = None,  msg = None, dartcoms=[]):
    if is_logado():
        date_start = request.args.get('start')
        date_end = request.args.get('end')
        
        if request.method == 'POST':
            date_start = request.form['date-start']
            date_end = request.form['date-end']

        if date_start or date_end:
            dado_repository = DadoRepository()
            # ALTERAR
            dartcoms, error_db, volume_for_date, quantidade_for_date, satellite_for_date, tempo_for_date_downlaod, tempo_for_date_armazenamento = dado_repository.get_report_dartcom(date_start, date_end)
            if error_db:
                send_email(subject='Falha na rota /dartcom/relatorio', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
                msg = 'Erro no banco de dados'
            else:
                # ALTERAR
                daily_volume = dado_repository.get_dartcom_daily_volume(date_start, date_end)
                if volume_for_date is None:
                    volume_for_date = []
                grafico_volume_json, volume_fig = create_graph_volume(volume_for_date)
                grafico_quantidade_json, quantidade_fig = create_graph_quantity(quantidade_for_date)
                grafico_satellite_json, satellite_fig = create_graph_satellite(satellite_for_date)    
                grafico_tempo_json, tempo_fig = create_graph_time(tempo_for_date_downlaod, tempo_for_date_armazenamento, 'Compactação')    

                if request.args.get('download'):
                    # ALTERAR
                    return create_dartcom_pdf(dartcoms=dartcoms, daily_volume=daily_volume, date_start=date_start, date_end=date_end,volume_fig=volume_fig,quantidade_fig=quantidade_fig,satellite_fig=satellite_fig, tempo_fig=tempo_fig)                         
                          
        return render_template('dartcom_relatorio.html', dartcoms=dartcoms, daily_volume=daily_volume, date_start=date_start, date_end=date_end, grafico_volume=grafico_volume_json, grafico_quantidade=grafico_quantidade_json, grafico_satellite=grafico_satellite_json, grafico_tempo=grafico_tempo_json, msg=msg)
    else:
        return redirect(url_for('login'))

def create_graph_volume(volume_for_date):
    dates = [str(date) for date, volume in volume_for_date]
    volumes = [volume for date, volume in volume_for_date]
    volumes_text = [f'{volume:.2f}' for volume in volumes]

    # Criar o objeto de gráfico de barras
    fig = go.Figure(data=[go.Bar(x=dates, y=volumes, text=volumes_text, textposition='auto', hovertemplate='Volume: %{y:.2f}<extra></extra>')])

    # Atualizar layout do gráfico
    fig.update_layout(
        title='Volume de dados baixados diariamente',
        xaxis=dict(title='Data',tickangle=-45, tickformat='%d/%m/%Y',dtick='D1'),
        yaxis=dict(title='Volume (GB)'),
        bargap=0.2,
        colorway=["#008E9B"],
    )

    # Salvar o gráfico em uma variável como JSON
    grafico_json = fig.to_json()

    return grafico_json, fig

def create_graph_quantity(quantidade_for_date):
    dates = [str(date) for date, quantidade in quantidade_for_date]
    quantidades = [quantidade for date, quantidade in quantidade_for_date]

    # Criar o objeto de gráfico de barras
    fig = go.Figure(data=[go.Scatter(x=dates, y=quantidades,hovertemplate='Quantidade: %{y}<extra></extra>')])

    fig.update_traces(marker_size=10)

    # Atualizar layout do gráfico
    fig.update_layout(
        title='Quantidade de arquivos baixados diariamente',
        xaxis=dict(title='Data',tickangle=-30, tickformat='%d/%m', dtick='D1'),
        yaxis=dict(title='Quantidade', range=[0, max(quantidades) +10]),
        bargap=0.2,
        colorway=["#1f912e"],
        
    )

    # Salvar o gráfico em uma variável como JSON
    grafico_json = fig.to_json()

    return grafico_json, fig

def create_graph_satellite(satellite_for_date):
    satelite = [satelites for satelites, quantidade in satellite_for_date]
    quantidade = [quantidade['quantidade'] for satelites, quantidade in satellite_for_date]
    volume = [quantidade['volume'] for satelites, quantidade in satellite_for_date]

    # Criar o objeto de gráfico de barras
    fig = go.Figure(data=[go.Bar(x=quantidade, y=satelite, text=quantidade, textposition='auto', hovertemplate='Quantidade: %{x}<br>Volume: %{customdata:.2f} GB<extra></extra>', customdata=volume, orientation='h', width=0.3 )])

    # Atualizar layout do gráfico
    fig.update_layout(
        title='Quantidade de arquivos baixados por satélite',
        xaxis=dict(title='Quantidade'),
        yaxis=dict(title='Satélite'),
        bargap=0.2,
        colorway=["#0077BA"]
    )

    # Salvar o gráfico em uma variável como JSON
    grafico_json = fig.to_json()

    return grafico_json, fig

def create_graph_time(time_for_date_processes, tempo_for_date_armazenamento, title_processes):
    dates = [date for date, processes in time_for_date_processes]
    processes = [processes.total_seconds() / 60 for date, processes in time_for_date_processes]
    armazenados = [armazenado.total_seconds() / 60 for date, armazenado in tempo_for_date_armazenamento]

    processes_time = [minutes_to_time(p) for p in processes]
    armazenados_time = [minutes_to_time(a) for a in armazenados]

    # Criar o objeto de gráfico de barras
    fig = go.Figure()
    fig.add_trace(go.Bar(x=dates, y=processes, name=f'Tempo de {title_processes}', hovertemplate=f'{title_processes}: '+'%{customdata}<extra></extra>', customdata=processes_time, marker_color='#1f912e'))
    fig.add_trace(go.Bar(x=dates, y=armazenados, name='Tempo de Armazenamento', hovertemplate='Armazenamento: %{customdata}<extra></extra>', customdata=armazenados_time, marker_color='#d62728'))

    # Atualizar layout do gráfico
    fig.update_layout(
        title=f'Tempo de {title_processes} e Armazenamento por dia',
        xaxis=dict(title='Data', tickangle=-30, tickformat='%d/%m', dtick='D1'),
        yaxis=dict(title='Tempo (minutos)', range=[0, max(max(processes), max(armazenados)) + 10]),
        barmode='group',  
        bargap=0.6, 
        legend=dict(
            orientation='h',  
            yanchor='bottom', 
            y=-1.02,
            xanchor='right',
            x=0.5
        )
    )

    # Salvar o gráfico em uma variável como JSON
    grafico_json = fig.to_json()

    return grafico_json, fig

@app.route('/settings', methods=['GET', 'POST'])
def settings():    
    if is_logado():
        user_repository = UserRepository()
        
        if request.method == 'POST' and 'theme' in request.form:
            dark_theme = request.form['theme'].lower() == 'true'
            error_db = user_repository.update_theme(theme = dark_theme)
            if error_db:
                send_email(subject='Falha ao atualizar tema', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            else:
                session['dark_theme'] = dark_theme
        
        return render_template('settings.html')
    else:
        return redirect(url_for('login'))

@app.route('/check_service_connection')
def check_service_connection():
    global last_check_fdt
    try:
        is_first_check = False
        if not last_check_fdt:
            is_first_check = True
            last_check_fdt = datetime.now()
        # calcula a diferença entre a data atual e o último check
        check_diff = datetime.now() - last_check_fdt
        # se a diferença for pelo menos 5 minutos
        if check_diff >= timedelta(minutes=5) or is_first_check:
            last_check_fdt = datetime.now()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((fdt_server, int(fdt_port)))
            sock.close()

        return jsonify({'status': 'success'})
    except socket.error as e:
        error_message = str(e)
        send_email('Erro na conexão com o servidor FDT', f'Ocorreu um erro na comunicação com o serviço FDT na CORCR - Cuiabá.\n\nInformativo do erro: {error_message}')
        return jsonify({'status': 'error', 'message': error_message})

# Rota para resetar os processos de background
@app.route("/reset_background", methods=["POST"])
def reset_background():
    stop_background_process()
    start_background_process()
    return jsonify({"status": "reiniciado com sucesso"})
    
@app.template_filter('class_status')
def class_status_filter(s):
    return class_status(s)

@app.template_filter('size_to_human_view')
def size_to_human_view_filter(s):
    return size_to_human_view(s)

def is_logado():
    return 'loggedin' in session and session['loggedin'] is True

def is_adm():
    return 'perfil' in session and session['perfil'] == 'administrador'

def is_visitante():
    return 'perfil' in session and session['perfil'] == 'visitante'


if __name__ == '__main__':
    # Production
    http_server = WSGIServer(('', 3001), app)
    http_server.serve_forever()

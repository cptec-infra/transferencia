import os
import glob
import re
import requests
import hashlib
import configparser
import smtplib
import subprocess
import shutil
import asyncio
import random
import string
import math
from typing import List
from string import Template
from io import BytesIO
from flask import send_file
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from models import DadoModel, DartcomModel, DartcomSateliteModel
from filters.filters import size_to_human_view
from repositories.dado_repository import DadoRepository
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from itsdangerous import URLSafeTimedSerializer

config = configparser.ConfigParser()
config.read("config.ini")

# Declaracao de variaveis para transferencia FDT
fdt_server = config.get('FDT', 'fdt_server')
fdt_port = config.get('FDT', 'fdt_port')
fdt_service = config.get('FDT', 'fdt_service')
fdt_destiny_all = config.get('FDT', 'fdt_destiny_all')
fdt_origin_data = config.get('FDT', 'fdt_origin_data')
fdt_origin_md5 = config.get('FDT', 'fdt_origin_md5')
fdt_destiny_md5 = config.get('FDT', 'fdt_destiny_md5')
# Dartcom
fdt_port_dartcom = config.get('FDT', 'fdt_port_dartcom')
fdt_destiny_dartcom = config.get('FDT', 'fdt_destiny_dartcom')
fdt_destiny_dartcom_cmd = config.get('FDT', 'fdt_destiny_dartcom_cmd')
fdt_origin_dartcom = config.get('FDT', 'fdt_origin_dartcom')
dartcom_time_min = config.getint('DARTCOM', 'dartcom_time_min')

fdt_server_cp = config.get('FDT', 'fdt_server_cp')
fdt_origin_dartcom_cp = config.get('FDT', 'fdt_origin_dartcom_cp')

# Declaracao de variaveis para armazenar
storage_path = config.get('STORAGE','storage_path')

# Declaracao de variaveis para email
smtp_username = config.get('SMTP', 'smtp_username')
smtp_password = config.get('SMTP', 'smtp_password')
smtp_server = config.get('SMTP', 'smtp_server')
smtp_port = config.get('SMTP', 'smtp_port')
contacts = config.get('SMTP','contacts')
contact_adm = config.get('SMTP','contact_adm')

# Declaracao de id do usuário admin
id_admin = config.get('APP', 'id_admin')

# Declaracao de status
status_error = 'Erro'
status_running = 'Executando'
status_completed = 'Concluído'
status_na = 'N.A.'

# Carrega a chave para criar o token de senha
key_reset_password = config.get('PASSWORD', 'key_reset_password')

transfer_list = []
dartcom_list = []

def get_transfer_list():
    return transfer_list

def get_dartcom_list():
    return dartcom_list

# procura novos arquivos
def background_process():
    # atualiza os md5s
    service_running = search_files_md5()
    if service_running:
        return
    
    global transfer_list
    transfer_list = []
    
    # lista de dados para retentar
    retries = search_retries()
    # lista de dados com base em todos os md5s na ampare
    result_files_md5, list_md5_error = list_md5_search_data()
    # lista de dados que não foram registrados ainda (novos)
    new_files_list = get_new_files_list(result_files_md5)

    # add os nomes dos dados (retry) na lista de transferência
    for r in retries:
        transfer_list.append(r.nome)

    # add os nomes dos dados (novos) na lista de transferência
    for f in new_files_list:
        transfer_list.append(f)

    # realiza os retries
    if retries:
        for retry in retries:
            print(f'Retentando o arquivo {retry.nome}')
            retry_file(retry)

    # realiza a transferencia dos novos arquivos            
    for md5_cba in list_md5_error:
        save_md5_cba_zerado(md5_cba)
    for data in new_files_list:
        transfer_file(data)
        print(f'{get_datetime_str()} - Término transfer_file - {data}')
    print(f'{get_datetime_str()} - Término background_process na def')

def background_process_dartcom():
    servers = []
    servers.append((fdt_server, fdt_origin_dartcom))
    servers.append((fdt_server_cp, fdt_origin_dartcom_cp))

    service_running = search_files_dartcom(servers)
    # service_running_cp = search_files_dartcom_cp()
    if service_running:
        return

    global dartcom_list
    dartcom_list = []
    result_dartcom = []

    # lista de dados para retentar
    dartcom_retries = search_dartcom_retries()
    # lista de diretorios dartcom na ampare
    result_dartcom, dartcom_error = list_search_dartcom(fdt_destiny_dartcom)
    print('lista de resultados:')
    print(len(result_dartcom))

    if dartcom_error:
        send_email('Falha ao buscar dados da antenas', f'Favor verificar o ocorrido.\n\n{dartcom_error}', True)
        return
    # lista de dados que não foram registrados ainda (novos)
    new_files_dartcom = get_new_files_dartcom(result_dartcom)
    print('NEWFILES')
    print(new_files_dartcom)

    # add os nomes dos dados (retry) na lista de transferência
    for r in dartcom_retries:
        dartcom_list.append(r.nome)

    # add os nomes dos dados (novos) na lista de transferência
    for f in new_files_dartcom:
        dartcom_list.append(f[0])

    # realiza os retries
    if dartcom_retries:
        for retry in dartcom_retries:
            print(f'Retentando o arquivo dartcom {retry.nome}')
            retry_file_dartcom(retry)

    # realiza os processos para os novos arquivos            
    # dartcom_file(new_files_dartcom[0])
    for data in new_files_dartcom:
        dartcom_file(data)

# Fluxo:
# Compactar
# Armazenar dado
def dartcom_file(dartcom):
    data, missao, files_path, satelite, date_modified, date_dir = dartcom

    dado_repository = DadoRepository()

    dartcom = DartcomModel()
    dartcom.set_nome(data)
    dartcom.set_modified_datetime(date_modified)
    dartcom.set_compressed_status(status_running)
    dartcom.set_compressed_start_datetime(get_datetime_str())
    dartcom.set_date_path(date_dir)
    dartcom.set_missao(missao)
    dartcom.set_id_dartcom_satelite(satelite.id)

    print('INSERT DARTCOM')
    id_dartcom, error_db = dado_repository.insert_dartcom(dartcom)
    if error_db:
        send_email('Falha no registro da tabela dartcom', f'Favor verificar o ocorrido.\n\n{error_db}', True)
        return
    dartcom_list.remove(dartcom.nome)    
    dartcom.set_id(id_dartcom)

    # name
    filename = data

    print('Dado: ', filename)
    
    # compactar
    path_transfer = ''
    error_vcdu = False
    if satelite.is_compressed:
        print('IS COMPRESSED')
        filename += ".tar.gz"
        # compacta os arquivos
        epsl0_path = get_dartcom_epsl0_path(satelite.epsl0_template, data)       
        file_compress, compress_status, compress_end_datetime, filesize, compress_error = dartcom_compress(data, files_path, satelite.is_epsl0, epsl0_path)

        path_transfer = file_compress
        dartcom.set_compressed_status(compress_status)
        dartcom.set_compressed_end_datetime(compress_end_datetime)
        dartcom.set_filesize(filesize)

        print('UPDATE DARTCOM COMPRESS')

        error_db = dado_repository.update_dartcom_compress(dartcom)
        if error_db:
            send_email('Falha ao atualizar dados na compactação', f'Favor verificar o ocorrido.\n\n{error_db}', True)
            return

        if compress_status == status_error:
            # Erro ao compactar
            # Envia e-mail comunicando o erro
            send_email(f'Falha ao compactar {data}', f'Erro ao compactar o dado {data}.\n\nFavor realizar o processo novamente!\n\nDescrição do erro: \n\n{compress_error}\n\nAtenciosamente, \n\nCOIDS')
            return
    else:
        print('IS NOT COMPRESSED')
        dartcom.set_compressed_status(status_na)
        dartcom.set_compressed_start_datetime(None)

        # localizar o arquivo e pegar o tamanho
        path_transfer, filesize, error_vcdu = dartcom_vcdu(files_path)
        dartcom.set_filesize(filesize)

        print('UPDATE DARTCOM VCDU')

        error_db = dado_repository.update_dartcom_vcdu(dartcom)
        if error_db:
            send_email('Falha ao atualizar dado vcdu', f'Favor verificar o ocorrido.\n\n{error_db}', True)
            return
        
    # Atualiza o registro com o início do armazenamento
    storing_start_datetime = get_datetime_str()
    storing_status = status_running
    dartcom.set_storing_start_datetime(storing_start_datetime)
    if error_vcdu:
        dartcom.set_storing_status(status_error)
    else:
        dartcom.set_storing_status(storing_status)

    print('UPDATE DARTCOM STORING RUNNING')
    error_db = dado_repository.update_dartcom_storing_running(dartcom=dartcom)
    if error_db:
        send_email('Falha ao atualizar dados do armazenamento dartcom', f'Favor verificar o ocorrido.\n\n{error_db}', True)
        return
    
    # ARAMAZENA O DADO
    if storing_status != status_error:
        print('COPY DARTCOM')
        storing_status, storing_end_datetime, storing_error = copy_dartcom(path_transfer, satelite, missao, date_dir, filename)
    if storing_status == status_error:
        # Erro ao armazenar o dado
        # Envia e-mail comunicando o erro
        send_email(f'Falha ao armazenar o dartcom {data}', f'Erro ao armazenar o dartcom {data} na COIDS.\n\nFavor realizar o processo novamente!\n\nDescrição do erro: \n\n{storing_error}\n\nAtenciosamente, \n\nCOIDS')
    
    dartcom.set_storing_status(storing_status)
    dartcom.set_storing_end_datetime(storing_end_datetime)

    print('UPDATE DARTCOM STORING COMPLETED')
    error_db = dado_repository.update_dartcom_storing_completed(dartcom=dartcom)
    if error_db:
        send_email('Falha ao atualizar dados do término do armazenamento dartcom', f'Favor verificar o ocorrido.\n\n{error_db}', True)

def retry_file_dartcom(dartcom: DartcomModel):
    dado_repository = DadoRepository()
    dado_repository.insert_dartcom_historico(dartcom.id)

    files_path = f'{dartcom.dartcom_satelite.satelite_path}/{dartcom.date_path}'

    error = dartcom.error

    # redefine os valores para realizar a retentativa - inicio
    if error == 'compactar':
        dartcom.set_compressed_status(None)
        dartcom.set_compressed_start_datetime(None)
        dartcom.set_compressed_end_datetime(None)
        dartcom.set_filesize(None)
        dartcom.set_storing_status(None)
        dartcom.set_storing_start_datetime(None)
        dartcom.set_storing_end_datetime(None)
    elif error == 'armazenamento':
        dartcom.set_storing_status(None)
        dartcom.set_storing_start_datetime(None)
        dartcom.set_storing_end_datetime(None)

    dartcom.set_retry_user(None)
    dartcom.set_retry_datetime(None)
    # redefine os valores para realizar a retentativa - fim
    dado_repository.update_dartcom_reset(dartcom)

    data = dartcom.nome    
    dartcom_list.remove(data)

    # name
    filename = data

    # compactar
    path_transfer = ''
    if dartcom.dartcom_satelite.is_compressed:
        filename += ".tar.gz"
        # compacta os arquivos
        epsl0_path = get_dartcom_epsl0_path(dartcom.dartcom_satelite.epsl0_template, data)       
        file_compress, compress_status, compress_end_datetime, filesize, compress_error = dartcom_compress(data, files_path, dartcom.dartcom_satelite.is_epsl0, epsl0_path)

        path_transfer = file_compress
        dartcom.set_compressed_status(compress_status)
        dartcom.set_compressed_end_datetime(compress_end_datetime)
        dartcom.set_filesize(filesize)

        error_db = dado_repository.update_dartcom_compress(dartcom)
        if error_db:
            send_email('Falha ao atualizar dados na compactação', f'Favor verificar o ocorrido.\n\n{error_db}', True)
            return

        if compress_status == status_error:
            # Erro ao compactar
            # Envia e-mail comunicando o erro
            send_email(f'Falha ao compactar {data}', f'Erro ao compactar o dado {data}.\n\nFavor realizar o processo novamente!\n\nDescrição do erro: \n\n{compress_error}\n\nAtenciosamente, \n\nCOIDS')
            return
    else:
        dartcom.set_compressed_status(status_na)
        dartcom.set_compressed_start_datetime(None)

        # localizar o arquivo e pegar o tamanho
        path_transfer, filesize, error_vcdu = dartcom_vcdu(files_path)
        dartcom.set_filesize(filesize)

        error_db = dado_repository.update_dartcom_vcdu(dartcom)
        if error_db:
            send_email('Falha ao atualizar dado vcdu', f'Favor verificar o ocorrido.\n\n{error_db}', True)
            return
        
    # Atualiza o registro com o início do armazenamento
    storing_start_datetime = get_datetime_str()
    storing_status = status_running
    dartcom.set_storing_start_datetime(storing_start_datetime)
    if error_vcdu:
        dartcom.set_storing_status(status_error)
    else:
        dartcom.set_storing_status(storing_status)

    error_db = dado_repository.update_dartcom_storing_running(dartcom=dartcom)
    if error_db:
        send_email('Falha ao atualizar dados do armazenamento dartcom', f'Favor verificar o ocorrido.\n\n{error_db}', True)
        return
    
    # ARAMAZENA O DADO
    if storing_status != status_error:
        storing_status, storing_end_datetime, storing_error = copy_dartcom(path_transfer, dartcom.dartcom_satelite, dartcom.missao, dartcom.date_path, filename)
    if storing_status == status_error:
        # Erro ao armazenar o dado
        # Envia e-mail comunicando o erro
        send_email(f'Falha ao armazenar o dartcom {data}', f'Erro ao armazenar o dartcom {data} na COIDS.\n\nFavor realizar o processo novamente!\n\nDescrição do erro: \n\n{storing_error}\n\nAtenciosamente, \n\nCOIDS')
    
    dartcom.set_storing_status(storing_status)
    dartcom.set_storing_end_datetime(storing_end_datetime)

    error_db = dado_repository.update_dartcom_storing_completed(dartcom=dartcom)
    if error_db:
        send_email('Falha ao atualizar dados do término do armazenamento dartcom', f'Favor verificar o ocorrido.\n\n{error_db}', True)

def get_dartcom_epsl0_path(epsl0_template, data):
    data = data.replace(".","_")
    data_array = data.split("_")[2:7]
    date = data_array[0]+"-"+data_array[1]+"-"+data_array[2]
    time = data_array[3]+"-"+data_array[4]

    epsl0_template = Template(template=epsl0_template)
    return epsl0_template.substitute(date=date, time=time)

def dartcom_vcdu(path):
    error = None
    vcdu_path = None
    filesize = None
    try:
        vcdu_name = next((f for f in os.listdir(path) if f.endswith('.vcdu')), None)
        if not vcdu_name:
            error = 'VCDU não encontrado'
        else:
            vcdu_path = os.path.join(path, vcdu_name)
            filesize = os.path.getsize(vcdu_path)

        return vcdu_path, filesize, error
    except Exception as e:
        return vcdu_path, filesize, e

def dartcom_compress(data, path, is_epsl0, epsl0_path_origin):
    subfolder = os.path.join(path, data)
    try:
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)

        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        for file in files:
            file_extension = os.path.splitext(file)[1]
            file_name_parts = file.split('_')
            if file_extension in ('.png', '.nmf', '.nav') or len(file_name_parts) < 3:
                renamed_file = data+file_extension
            else:
                renamed_file = data+'_'+file_name_parts[2]
            file_path = os.path.join(path, file)
            file_path_destiny = os.path.join(subfolder, renamed_file)
            shutil.copy(file_path, file_path_destiny)

        if is_epsl0:
            epsl0_path_destiny = os.path.join(subfolder, 'EPSL0')
            if not os.path.exists(epsl0_path_destiny):
                os.makedirs(epsl0_path_destiny)

            if os.path.isdir(epsl0_path_origin):
                files_epsl0 = [f for f in os.listdir(epsl0_path_origin) if os.path.isfile(os.path.join(epsl0_path_origin, f))]
                for file in files_epsl0:
                    renamed_epsl0_file = file.split('_')[0]+"_"+data
                    file_epsl0_path = os.path.join(epsl0_path_origin, file)
                    file_epsl0_path_destiny = os.path.join(epsl0_path_destiny, renamed_epsl0_file)
                    shutil.copy(file_epsl0_path, file_epsl0_path_destiny)

        file_compress = shutil.make_archive(subfolder, 'gztar', subfolder)
        filesize = os.path.getsize(file_compress)

        # apaga subfolder
        shutil.rmtree(subfolder)

        compress_end_datetime = get_datetime_str()
        compress_status = status_completed

        return file_compress, compress_status, compress_end_datetime, filesize, None
    except Exception as e:
        compress_end_datetime = get_datetime_str()
        compress_status = status_error        
        return file_compress, compress_status, compress_end_datetime, filesize, e  

# dados sensoriamento
def search_files_md5():
    if is_process_running(fdt_destiny_all):
        print("O processo já está em execução.")
        return True
    else:
        print('{} - início sincronização fdt md5'.format(get_datetime_str()))
        try:
            fdt_cmd = 'sudo -u transfcba java -jar {} -p {} -P 24 -pull -r -c {} -d {} {}'.format(fdt_service,fdt_port,fdt_server,fdt_destiny_all,fdt_origin_md5)
            # fdt_process = subprocess.Popen(fdt_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # output, error = fdt_process.communicate()
            result = subprocess.run(fdt_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout
            error = result.stderr

            if error:
                print('Error no comando: {}'.format(error))
            if output:
                print('Output do comando: {}'.format(output))
                
        except Exception as e:
            print('erro no fdt: ', e)
        print('{} - término sincronização fdt md5'.format(get_datetime_str()))
        return False

#dados meteorologicos
def search_files_dartcom(servers):
    if is_process_running(fdt_destiny_dartcom):
        print("O processo fdt dartcom já está em execução.")
        return True
    else:
        try:
            for server, origin in servers:
                print('{} - início sincronização fdt dartcom - {}'.format(get_datetime_str(), server))
                fdt_cmd = 'sudo -u transfcba java -jar {} -p {} -P 24 -pull -r -c {} -d {} {}'.format(fdt_service,fdt_port_dartcom,server,fdt_destiny_dartcom_cmd,origin)
                result = subprocess.run(fdt_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output = result.stdout.decode()
                error = result.stderr.decode()

                if result.returncode != 0:
                    print('Error no comando: {}'.format(error))
                if output:
                    print('Output do comando: {}'.format(output))


        except Exception as e:
            print('erro no fdt: ', e)
        print('{} - término sincronização fdt dartcom'.format(get_datetime_str()))
        return False
    
# def search_files_dartcom_cp():
#     if is_process_running(scp_ip):
#         print("O processo scp dartcom já está em execução.")
#         return True
#     else:
#         return False
#         dado_repository = DadoRepository()
#         antenas, error_db = dado_repository.get_dartcom_antena()
#         if error_db:
#             return
#         for antena in antenas:
#             satelites, error_db = dado_repository.get_dartcom_templates(id_dartcom_antena=antena.id)
#             if error_db:
#                 return
            
#             for satelite in satelites:
#                 # se satelite possui path scp realiza a transferencia via scp
#                 if satelite.template_path_origin_scp:
#                     try:
#                         date_now = get_date_str()
#                         # template_path_origin_scp = Template(template=satelite.get_template_path_origin_scp)
#                         template_path_origin_scp = Template(template=str(satelite.template_path_origin_scp))
#                         path_origin_scp = template_path_origin_scp.substitute(date=date_now)
#                         print('{} - início sincronização scp dartcom'.format(get_datetime_str()))

#                         scp_cmd = 'sudo -u transfcba rsync -avz --progress {}@{}:{} {}'.format(scp_user, scp_ip, path_origin_scp, satelite.satelite_path)
#                         result = subprocess.run(scp_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#                         output = result.stdout.decode()
#                         error = result.stderr.decode()

#                         if result.returncode != 0:
#                             print('Error no comando: {}'.format(error))
#                         if output:
#                             print('Output do comando: {}'.format(output))
#                     except Exception as e:
#                         print('erro no scp: ', e)
#                     print('{} - término sincronização scp dartcom'.format(get_datetime_str()))
#         return False

def is_process_running(fdt_origin_data):
    ps_process = subprocess.Popen(['ps', '-eo', 'args'], stdout=subprocess.PIPE)
    output_ps, _ = ps_process.communicate()
    ps_output_lines = output_ps.decode('utf-8').split('\n')
    filtered_lines = [line for line in ps_output_lines if fdt_origin_data in line]
    if filtered_lines:
        return True
    return False

def list_md5_search_data():
    list_files_md5 = []
    list_md5_error = []
    if os.path.exists(fdt_destiny_md5):
        files = os.listdir(fdt_destiny_md5)
        for file in files:
            # pega o tamanho do md5_cba
            md5_size = os.path.getsize(fdt_destiny_md5 + '/' + file)

            parts = file.split('.')  
            if len(parts) >= 2:  
                file_name = '.'.join(parts[:-1])
                # caso o md5 esteja zerado
                if md5_size == 0:
                    # add para lista de erros
                    list_md5_error.append(file_name)
                else:
                    # add para lista de arquivos para baixar
                    list_files_md5.append(file_name)
    else:
        print('O diretório não existe')

    return list_files_md5, list_md5_error

def list_search_dartcom(path):
    list_dartcom = []
    try:
        if os.path.exists(path):
            dado_repository = DadoRepository()
            antenas, error_db = dado_repository.get_dartcom_antena()

            if error_db:
                send_email('Falha ao listar antenas', f'Favor verificar o ocorrido.\n\n{error_db}', True)
                return None, error_db
        
            for antena in antenas:
                satelites: List[DartcomSateliteModel]
                satelites, error_db = dado_repository.get_dartcom_templates(antena.id)
                if error_db:
                    print(f"Erro ao obter templates de satélites: {error_db}")
                    continue

                for satelite in satelites:
                    if os.path.isdir(satelite.satelite_path):
                        dates_dirs = os.listdir(satelite.satelite_path)
                        for date_dir in dates_dirs:
                            datas_dirs = os.listdir(f'{satelite.satelite_path}/{date_dir}')
                            for data_dir in datas_dirs:
                                files_path = f'{satelite.satelite_path}/{date_dir}/{data_dir}'

                                date_now = datetime.now()
                                date_modified = datetime.fromtimestamp(os.path.getmtime(files_path))

                                diff = date_now - date_modified
                                missao = ''
                                error = ''
                                if diff >= timedelta(minutes=dartcom_time_min):
                                    if satelite.command:
                                        missao, error = define_missao(files_path, satelite.command)
                                
                                    if not error:
                                        dartcom_name = define_dartcom_name(data_dir, satelite, missao)
                                        if dartcom_name:
                                            list_dartcom.append((dartcom_name, missao, files_path, satelite, date_modified, date_dir))
                                        else:
                                            print(f"Nome do Dartcom vazio para data_dir: {data_dir}")
                                    else:
                                        print('Erro na definição da missão:', error)
                            
            return list_dartcom, None
    except Exception as e:
        print('Erro:', e)
        return list_dartcom, e
    
def get_new_files_dartcom(lista):
    new_dartcoms = []

    dado_repository = DadoRepository()
    for data, missao, files_path, satelite, date_modified, date_dir in lista:
        file_found, error_db = dado_repository.find_dartcom(data)
        # envia email caso ocorra erro no bd
        if error_db:
            # envia email
            send_email(subject='Falha na busca do dado', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            continue
        # se dado ja registrado
        if not file_found:
            # se dado nao cadastrado, add na lista new_dartcoms
            new_dartcoms.append((data, missao, files_path, satelite, date_modified, date_dir))

    return new_dartcoms

def define_dartcom_name(data_dir, satelite, missao):
    try:
        datetime = data_dir.split(" ")
        date = datetime[0].replace("-", "_")
        time = datetime[1].replace("-", "_")
        name_template = Template(satelite.template_name)
        name = name_template.substitute(missao=missao, date=date, time=time)
        if not name:
            print(f"Warning: Nome gerado está vazio para o data_dir: {data_dir}")
        return name
    except Exception as e:
        print(f"Erro ao definir o nome do Dartcom: {e}")
        return None
    
def define_missao(path, command):
    infos = glob.glob(os.path.join(path, '*.info'), recursive=False)
    error = ''
    if infos:
        info_path = infos[0]
        command_template = Template(command)
        command = command_template.substitute(file=f'"{info_path}"')
        try:
            info_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error_command = info_process.communicate()
            missao = output.decode().strip()
            error = error_command.decode()
            if not missao:
                print(f"Warning: Missão está vazia para o caminho: {info_path}")
            return missao, error
        except Exception as e:
            error = str(e)
            missao = None
            print(f"Erro ao executar comando: {error}")
            return missao, error
    else:
        error = 'file not found'
        return None, error

def search_retries():
    dado_repository = DadoRepository()
    retries, error_db = dado_repository.get_retries()    
    if not error_db:
        print(retries)
        return retries
    return None

def search_dartcom_retries():
    dado_repository = DadoRepository()
    retries, error_db = dado_repository.get_retries_dartcom()
    if not error_db:
        print(retries)
        return retries
    return None

def get_new_files_list(files):
    new_files_list = []

    dado_repository = DadoRepository()
    for data in files:
        if not data: continue
        storage_data, pattern, satelity = define_directory(data)
        if not pattern: continue
        if not re.match(pattern, data): continue

        file_found, error_db = dado_repository.find_data(data)
        # envia email caso ocorra erro no bd
        if error_db:
            # envia email
            send_email(subject='Falha na busca do dado', body=f'Favor verificar o ocorrido.\n\n{error_db}', is_adm=True)
            continue
        # se dado ja registrado
        if not file_found:
            # se dado nao cadastrado, add na lista new_files_list
            new_files_list.append(data)            

    return new_files_list

def add_header(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 12)

    header_text = "Relatório de Transferência de Dados"
    image_path = "static/images/logo-coids.png"
    text_width = canvas.stringWidth(header_text, 'Helvetica-Bold', 12)
    x_position = (letter[0] - text_width) / 2

    image_width = 2 * cm
    image_height = 2 * cm    
    canvas.drawImage(image_path, 1 * cm, letter[1] - 2.5 * cm, width=image_width, height=image_height, preserveAspectRatio=True)

    canvas.drawString(x_position, letter[1] - 1.5 * cm, header_text)

    canvas.restoreState()

def create_pdf(dados, daily_volume, date_start, date_end, volume_fig, quantidade_fig, satellite_fig, tempo_fig):
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=1 * cm, rightMargin=1 * cm)
    
    elements = []

    # Informações adicionais
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    elements.append(Spacer(1, 12))  
    elements.append(Paragraph(f"Período: {convert_string_datetime_br(date_start)} - {convert_string_datetime_br(date_end)}", normal_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Volume: {'-' if not daily_volume else size_to_human_view(daily_volume)}", normal_style))
    elements.append(Spacer(1, 12))

    # Dados para a tabela
    data = [['Nome','Data', 'Download', 'Tempo', 'Válido', 'Armazenado', 'Tempo', 'Tamanho']]  # Cabeçalho da tabela
    for dado in dados:
        data.append([
            dado.nome,
            convert_datetime_to_string(dado.download_start_datetime),
            dado.download_status,
            '-' if not dado.download_time else dado.download_time,
            'Sim' if dado.md5_validated else ('Aguardando' if dado.md5_validated == None else 'Não'),
            dado.storing_status if dado.storing_status else 'Aguardando',
            '-' if not dado.storing_time else dado.storing_time,
            size_to_human_view(dado.filesize)
        ])
    
    # Estilo da tabela
    table = Table(data, colWidths=[8.2 * cm, 2.1 * cm, 2.1 * cm, 1.4 * cm, 1.2 * cm, 2.2 * cm, 1.4 * cm, 1.7 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#0077BA'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)

    # add graphs
    for fig in volume_fig, quantidade_fig, tempo_fig, satellite_fig:
        img_buffer = BytesIO()
        fig.write_image(img_buffer, format='png')
        img_buffer.seek(0)
        
        # Adicionar a imagem do gráfico ao PDF
        img = Image(img_buffer)
        img.drawHeight = 10 * cm
        img.drawWidth = 15 * cm
        elements.append(Spacer(3, 12))
        elements.append(img)
        elements.append(Spacer(1, 12))

    pdf.build(elements, onFirstPage=add_header, onLaterPages=add_header)
    buffer.seek(0)

    response = send_file(buffer, as_attachment=False, download_name='relatorio.pdf', mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename="relatorio_de_transferencia_de_dados.pdf"'
    response.headers['Content-Type'] = 'application/pdf'
    return response

def create_dartcom_pdf(dartcoms, daily_volume, date_start, date_end, volume_fig, quantidade_fig, satellite_fig, tempo_fig):
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=1 * cm, rightMargin=1 * cm)
    
    elements = []

    # Informações adicionais
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    elements.append(Spacer(1, 12))  
    elements.append(Paragraph(f"Período: {convert_string_datetime_br(date_start)} - {convert_string_datetime_br(date_end)}", normal_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Volume: {'-' if not daily_volume else size_to_human_view(daily_volume)}", normal_style))
    elements.append(Spacer(1, 12))

    # Dados para a tabela
    data = [['Nome','Data', 'Compactação', 'Tempo', 'Armazenado', 'Tempo', 'Tamanho']]  # Cabeçalho da tabela
    for dartcom in dartcoms:
        data.append([
            dartcom.nome,
            convert_datetime_to_string(dartcom.storing_start_datetime),
            dartcom.compressed_status,
            '-' if not dartcom.compressed_time else dartcom.compressed_time,
            dartcom.storing_status if dartcom.storing_status else 'Aguardando',
            '0:00:00' if not dartcom.storing_time else dartcom.storing_time,
            size_to_human_view(dartcom.filesize)
        ])
    
    # Estilo da tabela
    table = Table(data, colWidths=[8.2 * cm, 2.1 * cm, 2.1 * cm, 1.4 * cm, 2.2 * cm, 1.4 * cm, 1.7 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#0077BA'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)

    # add graphs
    for fig in volume_fig, quantidade_fig, tempo_fig, satellite_fig:
        img_buffer = BytesIO()
        fig.write_image(img_buffer, format='png')
        img_buffer.seek(0)
        
        # Adicionar a imagem do gráfico ao PDF
        img = Image(img_buffer)
        img.drawHeight = 10 * cm
        img.drawWidth = 15 * cm
        elements.append(Spacer(3, 12))
        elements.append(img)
        elements.append(Spacer(1, 12))

    pdf.build(elements, onFirstPage=add_header, onLaterPages=add_header)
    buffer.seek(0)

    response = send_file(buffer, as_attachment=False, download_name='relatorio.pdf', mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename="relatorio_de_transferencia_de_dados.pdf"'
    response.headers['Content-Type'] = 'application/pdf'
    return response

# Fluxo:
# Baixar arquivo
# Gerar MD5-CP
# Validar MD5
# Armazenar dado

# inicia o processo de transferencia
def transfer_file(data):
    if not data: return
    storage_data, pattern, satelity = define_directory(data)
    if not pattern: return
    if not re.match(pattern, data): return

    date_cba = find_data_cba_table(data=data)
    if not date_cba:
        # o dado ainda não está disponível em CBA
        return

    dado_repository = DadoRepository()

    download_start_datetime = get_datetime_str()
    download_status = status_running

    dado = DadoModel()
    dado.set_nome(data)
    dado.set_download_start_datetime(download_start_datetime)
    dado.set_download_status(download_status)
    dado.set_date_cba(date_cba)

    #inserir o dado inicial
    id_dado, error_db = dado_repository.insert_dado(dado=dado)
    if error_db:
        send_email('Falha no registro da tabela dado', f'Favor verificar o ocorrido.\n\n{error_db}', True)
        return
    
    transfer_list.remove(data)    
    dado.set_id(id_dado)

    # BAIXA O ARQUIVO
    download_status, download_end_datetime, filesize, download_error = download_file(data)
    dado.set_download_status(download_status)
    dado.set_download_end_datetime(download_end_datetime)
    dado.set_filesize(filesize)

    error_db = dado_repository.update_download(dado=dado)
    if error_db:
        send_email('Falha ao atualizar dados do download', f'Favor verificar o ocorrido.\n\n{error_db}', True)
        return
    
    if download_status == status_error:
        # Erro no download
        # Envia e-mail comunicando o erro do download
        #send_email(f'Falha na Transferência do dado {data}', f'Erro ao transferir o dado {data} para a COIDS.\n\nFavor realizar a transferência novamente!\n\nDescrição do erro: \n\n{download_error}\n\nAtenciosamente, \n\nCOIDS')

        # Cria um retry automático na primeira falha
        error_db_retry = dado_repository.set_auto_retry(id_dado=id_dado, id_admin=id_admin)
        if error_db_retry:
            send_email(subject='Falha ao registrar retry automático', body=f'Favor verificar o ocorrido.\n\n{error_db_retry}', is_adm=True)
        else:
            send_email(subject='Retry automático', body=f'O sistema gerou um retry automático para o dado {dado.nome}.')

        return
    
    # Atualiza os dados de início do MD5-CP
    md5_cp_start_datetime = get_datetime_str()
    md5_cp_status = status_running
    dado.set_md5_cp_status(md5_cp_status)
    dado.set_md5_cp_start_datetime(md5_cp_start_datetime)

    error_db = dado_repository.update_md5_cp_start(dado = dado)
    if error_db:
        send_email('Falha ao atualizar dados de início do download', f'Favor verificar o ocorrido.\n\n{error_db}', True)
        return
    
    # GERA O MD5-CP
    md5_cp, md5_cp_status, md5_cp_end_datetime, md5_cp_error = generate_md5_cp(data)
    dado.set_md5_cp_status(md5_cp_status)
    dado.set_md5_cp_end_datetime(md5_cp_end_datetime)

    error_db = dado_repository.update_md5_cp(dado=dado)
    if error_db:
        send_email('Falha ao atualizar dados do MD5-CP', f'Favor verificar o ocorrido.\n\n{error_db}', True)
        return
    
    if md5_cp_status == status_error:
        # Erro ao gerar MD5-CP
        # Envia e-mail comunicando o erro do MD5-CP
        send_email(f'Falha no MD5-CP do dado {data}', f'Erro ao gerar o MD5-CP do dado {data} na COIDS.\n\nFavor realizar o processo novamente!\n\nDescrição do erro: \n\n{md5_cp_error}\n\nAtenciosamente, \n\nCOIDS')
        return
    
    # VALIDA O MD5
    md5_validated, md5_validated_status, md5_validated_datetime, md5_validated_error = validate_md5(data, md5_cp) 
    dado.set_md5_validated(md5_validated)
    dado.set_md5_validated_datetime(md5_validated_datetime)

    error_db = dado_repository.update_md5_validated(dado=dado)
    if error_db:
        send_email('Falha ao atualizar dados da validação MD5', f'Favor verificar o ocorrido.\n\n{error_db}', True)
        return
    
    if not md5_validated:

        #remove o arquivo da área
        remove_file(data)

        # Envia e-mail comunicando o erro do MD5 inválido
        send_email(f'Falha na Validação do dado {data}', f'Erro na validação do MD5 do dado {data} transferido.\n\nFavor realizar a transferência novamente!\n\nDescrição do erro: \n\n{md5_validated_error}\n\nAtenciosamente, \n\nCOIDS')
        return
    
    # Atualiza o registro com o início do armazenamento
    storing_start_datetime = get_datetime_str()
    storing_status = status_running
    dado.set_storing_start_datetime(storing_start_datetime)
    dado.set_storing_status(storing_status)

    error_db = dado_repository.update_storing_running(dado=dado)
    if error_db:
        send_email('Falha ao atualizar dados do armazenamento', f'Favor verificar o ocorrido.\n\n{error_db}', True)
        return
    
    # ARAMAZENA O DADO
    storing_status, storing_end_datetime, storing_error = copy_file(data, storage_data, satelity)
    if storing_status == status_error:
        # Erro ao armazenar o dado
        # Envia e-mail comunicando o erro
        send_email(f'Falha ao armazenar o dado {data}', f'Erro ao armazenar o dado {data} na COIDS.\n\nFavor realizar o processo novamente!\n\nDescrição do erro: \n\n{storing_error}\n\nAtenciosamente, \n\nCOIDS')
    
    dado.set_storing_status(storing_status)
    dado.set_storing_end_datetime(storing_end_datetime)

    error_db = dado_repository.update_storing_completed(dado=dado)
    if error_db:
        send_email('Falha ao atualizar dados do término do armazenamento', f'Favor verificar o ocorrido.\n\n{error_db}', True)

def retry_file(dado: DadoModel):
    dado_repository = DadoRepository()
    dado_repository.insert_dado_historico(id_dado=dado.id)

    error = dado.error

    # redefine os valores para realizar a retentativa - inicio
    if error == 'download' or error == 'validacao':
        dado.set_download_status(None)
        dado.set_download_start_datetime(None)
        dado.set_download_end_datetime(None)
        dado.set_filesize(None)
        dado.set_md5_cp_status(None)
        dado.set_md5_cp_start_datetime(None)
        dado.set_md5_cp_end_datetime(None)
        dado.set_md5_validated(None)
        dado.set_md5_validated_datetime(None)
        dado.set_storing_status(None)
        dado.set_storing_start_datetime(None)
        dado.set_storing_end_datetime(None)        
    elif error == 'md5-cp':
        dado.set_md5_cp_status(None)
        dado.set_md5_cp_start_datetime(None)
        dado.set_md5_cp_end_datetime(None)
        dado.set_md5_validated(None)
        dado.set_md5_validated_datetime(None)
        dado.set_storing_status(None)
        dado.set_storing_start_datetime(None)
        dado.set_storing_end_datetime(None)
        pass
    elif error == 'armazenamento':
        dado.set_storing_status(None)
        dado.set_storing_start_datetime(None)
        dado.set_storing_end_datetime(None)
        pass

    dado.set_retry_user(None)
    dado.set_retry_datetime(None)
    # redefine os valores para realizar a retentativa - fim
    dado_repository.update_reset(dado)

    data = dado.nome

    transfer_list.remove(data)
    
    if error in ('download', 'validacao'):
        ## DOWNLOAD - INICIO
        download_start_datetime = get_datetime_str()
        download_status = status_running
        date_cba = find_data_cba_table(data=data)

        dado.set_download_start_datetime(download_start_datetime)
        dado.set_download_status(download_status)
        dado.set_date_cba(date_cba)

        #atualiza o dado inicial
        error_db = dado_repository.update_dado(dado=dado)
        if error_db:
            send_email('Falha no registro da tabela dado', f'Favor verificar o ocorrido.\n\n{error_db}', True)
            return

        # BAIXA O ARQUIVO
        download_status, download_end_datetime, filesize, download_error = download_file(data)
        dado.set_download_status(download_status)
        dado.set_download_end_datetime(download_end_datetime)
        dado.set_filesize(filesize)

        error_db = dado_repository.update_download(dado=dado)
        if error_db:
            send_email('Falha ao atualizar dados do download', f'Favor verificar o ocorrido.\n\n{error_db}', True)
            return
        
        if download_status == status_error:
            # Erro no download
            # Envia e-mail comunicando o erro do download
            dado_repository.delete_retry(dado.id_dado_retry)
            send_email(f'Falha na Transferência do dado {data}', f'Erro ao transferir o dado {data} para a COIDS.\n\nFavor realizar a transferência novamente!\n\nDescrição do erro: \n\n{download_error}\n\nAtenciosamente, \n\nCOIDS')
            return        
        ## DOWNLOAD - FIM
        
    if error in ('download', 'validacao', 'md5-cp'):
        ## MD5-CP - INICIO
        # Atualiza os dados de início do MD5-CP
        md5_cp_start_datetime = get_datetime_str()
        md5_cp_status = status_running
        dado.set_md5_cp_status(md5_cp_status)
        dado.set_md5_cp_start_datetime(md5_cp_start_datetime)

        error_db = dado_repository.update_md5_cp_start(dado=dado)
        if error_db:
            send_email('Falha ao atualizar dados de início do download', f'Favor verificar o ocorrido.\n\n{error_db}', True)
            return
        
        # GERA O MD5-CP
        md5_cp, md5_cp_status, md5_cp_end_datetime, md5_cp_error = generate_md5_cp(data)
        dado.set_md5_cp_status(md5_cp_status)
        #dado.set_md5_cp = md5_cp
        dado.md5_cp_end_datetime = md5_cp_end_datetime

        error_db = dado_repository.update_md5_cp(dado=dado)
        if error_db:
            send_email('Falha ao atualizar dados do MD5-CP', f'Favor verificar o ocorrido.\n\n{error_db}', True)
            return
        
        if md5_cp_status == status_error:
            # Erro ao gerar MD5-CP
            # Envia e-mail comunicando o erro do MD5-CP
            dado_repository.delete_retry(dado.id_dado_retry)
            send_email(f'Falha no MD5-CP do dado {data}', f'Erro ao gerar o MD5-CP do dado {data} na COIDS.\n\nFavor realizar o processo novamente!\n\nDescrição do erro: \n\n{md5_cp_error}\n\nAtenciosamente, \n\nCOIDS')
            return        
        ## MD5-CP - FIM
    
        ## VALIDA O MD5 - INICIO
        md5_validated, md5_validated_status, md5_validated_datetime, md5_validated_error = validate_md5(data, md5_cp) 
        dado.set_md5_validated(md5_validated)
        dado.set_md5_validated_datetime(md5_validated_datetime)

        error_db = dado_repository.update_md5_validated(dado=dado)
        if error_db:
            send_email('Falha ao atualizar dados da validação MD5', f'Favor verificar o ocorrido.\n\n{error_db}', True)
            return
        
        if not md5_validated:
            # MD5 inválido

            #remove o arquivo da área
            remove_file(data)

            # Envia e-mail comunicando o erro do MD5 inválido
            dado_repository.delete_retry(dado.id_dado_retry)
            send_email(f'Falha na Validação do dado {data}', f'Erro na validação do MD5 do dado {data} transferido.\n\nFavor realizar a transferência novamente!\n\nDescrição do erro: \n\n{md5_validated_error}\n\nAtenciosamente, \n\nCOIDS')
            return    
        ## VALIDA O MD5 - FIM
    
    if error in ('download', 'validacao', 'md5-cp', 'armazenamento'):
        # ARMAZENAMENTO - INICIO
        # Atualiza o registro com o início do armazenamento
        storing_start_datetime = get_datetime_str()
        storing_status = status_running
        dado.set_storing_start_datetime(storing_start_datetime)
        dado.set_storing_status(storing_status)

        error_db = dado_repository.update_storing_running(dado=dado)
        if error_db:
            send_email('Falha ao atualizar dados do armazenamento', f'Favor verificar o ocorrido.\n\n{error_db}', True)
            return
        
        # ARAMAZENA O DADO
        storage_data, pattern, satelity = define_directory(data)
        storing_status, storing_end_datetime, storing_error = copy_file(data, storage_data, satelity)
        if storing_status == status_error:
            # Erro ao armazenar o dado
            # Envia e-mail comunicando o erro
            dado_repository.delete_retry(dado.id_dado_retry)
            send_email(f'Falha ao armazenar o dado {data}', f'Erro ao armazenar o dado {data} na COIDS.\n\nFavor realizar o processo novamente!\n\nDescrição do erro: \n\n{storing_error}\n\nAtenciosamente, \n\nCOIDS')
        
        dado_repository.delete_retry(dado.id_dado_retry)

        dado.set_storing_status(storing_status)
        dado.set_storing_end_datetime(storing_end_datetime)

        error_db = dado_repository.update_storing_completed(dado=dado)
        if error_db:
            send_email('Falha ao atualizar dados do término do armazenamento', f'Favor verificar o ocorrido.\n\n{error_db}', True)
        # ARMAZENAMENTO - FIM
        
def save_md5_cba_zerado(data):
    if not data: return
    storage_data, pattern, satelity = define_directory(data)
    if not pattern: return
    if not re.match(pattern, data): return

    dado_repository = DadoRepository()
    error_db = dado_repository.save_md5_cba_error(data)
    if(error_db):
        send_email('Falha ao registrar MD5-CBA zerado', f'Favor verificar o ocorrido.\n\n{error_db}', True)

def find_data_cba_table(data):
    try:
        url = 'http://200.129.242.12/secor.html'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tabela = soup.find('table')
            # dados = []
            for linha in tabela.find_all('tr'):
                linha_dados = []
                for celula in linha.find_all(['td']):             
                    linha_dados.append(celula.text.strip())
                if linha_dados and linha_dados[0] == data:
                    date_table = linha_dados[2]                
                    return date_table
        else:
            return None
    except Exception:
        return None

def download_file(filename):
    #realiza o download
    search_data = fdt_origin_data + '/' + filename
    filesize = None

    print('{} - início Download FDT dado {} '.format(get_datetime_str(),filename))
    
    try:
        fdt_cmd = 'sudo -u transfcba java -jar {} -p {} -P 24 -pull -md5 -c {} -d {} {}'.format(fdt_service,fdt_port,fdt_server,fdt_destiny_all,search_data)


        print('Comando FDT: {}'.format(fdt_cmd))
        result = subprocess.run(fdt_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()
        error = result.stderr.decode()
        
        print('------------------------------')
        print(result.returncode)
        print('------------------------------')
        
        download_end_datetime = get_datetime_str()

        if output:
            print('Output do comando: {}'.format(output))
        
        if result.returncode != 0:
            print('Error no comando: {}'.format(error))
            download_status = status_error
        else:
            filesize = os.path.getsize(fdt_destiny_all + "/" + filename)
            download_status = status_completed            

        print('{} - término Download FDT dado {}'.format(get_datetime_str(),filename))
        
        return download_status, download_end_datetime, filesize, error
    except Exception as e:        
        download_status = status_error  
        download_end_datetime = get_datetime_str()
        
        print('{} - término Download Exception FDT dado {}'.format(get_datetime_str(),filename))

        return download_status, download_end_datetime, filesize, e


def generate_md5_cp(filename):
    md5_cp = ''
    error = ''
    try:
        with open(fdt_destiny_all + '/' + filename, 'rb') as f:
            hash_md5 = hashlib.md5()
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        md5_cp = hash_md5.hexdigest()        
        md5_cp_status = status_completed
    except Exception as e:
        error = e
        md5_cp_status = status_error

    md5_cp_end_datetime = get_datetime_str()

    return md5_cp, md5_cp_status, md5_cp_end_datetime, error

def validate_md5(data, md5_cp):
    md5_validated = False
    md5_validated_status = status_error
    md5_validated_datetime = None
    error = ''

    #valida MD5
    file_md5_cba = data + '.md5_cba'
    result_md5_cba = define_md5_cba(fdt_destiny_md5 + '/' + file_md5_cba)
    md5_validated = md5_cp == result_md5_cba
    md5_validated_status = status_completed
    md5_validated_datetime = get_datetime_str()

    return md5_validated, md5_validated_status, md5_validated_datetime, error

def remove_file(data):
    data_path = fdt_destiny_all + '/' + data
    os.remove(data_path)

def copy_file(data, storage_data, satelity):
    data_path = fdt_destiny_all + '/' + data
    satelity_path = fdt_destiny_all + '/' + satelity
    storage = storage_data + '/' + data
    try:
        os.makedirs(os.path.dirname(storage), exist_ok=True)
        shutil.copy(data_path, storage)
        storing_end_datetime = get_datetime_str()
        storing_status = status_completed

        # move to satelity folder
        shutil.move(data_path, satelity_path)

        return storing_status, storing_end_datetime, None
    except Exception as e:
        storing_end_datetime = get_datetime_str()
        storing_status = status_error        
        return storing_status, storing_end_datetime, e    

def copy_dartcom(path_transfer, satelite, missao, date_dir, filename):
    missao = '' if not missao else missao
    date_array = date_dir.split("-")
    date = date_array[0]+"_"+date_array[1]
    storage = storage_path + "/" + satelite.nome + missao + "/" + date + "/" + satelite.sensor + "/"+ filename
    try:
        os.makedirs(os.path.dirname(storage), exist_ok=True)
        shutil.copy(path_transfer, storage)
        storing_end_datetime = get_datetime_str()
        storing_status = status_completed

        return storing_status, storing_end_datetime, None
    except Exception as e:
        storing_end_datetime = get_datetime_str()
        storing_status = status_error        
        return storing_status, storing_end_datetime, e    

def define_directory(file1):
    sat_partes = file1.split('_')
    satelite = sat_partes[0]

    if satelite == 'CBERS' or satelite == 'AMAZONIA':
        missao = sat_partes[1]
        sensor = sat_partes[2]
        ano_mes = sat_partes[4] + '_' + sat_partes[5]
        ultima_parte = sat_partes[-1]
        pattern = r'(AMAZONIA|CBERS)_[A-Z0-9]_[A-Z0-9]+_(RAW|DRD)_\d{4}_\d{2}_\d{2}\.\d{2}_\d{2}_\d{2}_[A-Z0-9]'

        if ultima_parte == 'DRP':
            sensor = 'DRP'
            pattern = r'(AMAZONIA|CBERS)_[A-Z0-9]_[A-Z0-9]+_(RAW|DRD)_\d{4}_\d{2}_\d{2}\.\d{2}_\d{2}_\d{2}_[A-Z0-9]\d+_DRP$'

    elif satelite == 'AQUA' or satelite == 'TERRA':
        missao = ''
        sensor = 'MODIS'
        ano_mes = sat_partes[2] + '_' + sat_partes[3]
        pattern = r'(AQUA|TERRA)_(RAW|CADU|DRD)_\d{4}_\d{2}_\d{2}\.\d{2}_\d{2}_\d{2}_[A-Z0-9]'

    elif satelite == 'NPP' or satelite == 'NOAA20':
        missao = ''
        sensor = 'VIIRS'
        ano_mes = sat_partes[2] + '_' + sat_partes[3]
        pattern = r'(NPP|NOAA20)_(RAW|DRD)_\d{4}_\d{2}_\d{2}\.\d{2}_\d{2}_\d{2}_[A-Z0-9]'

    elif satelite == 'SPORT':
        missao = ''
        sensor = ''
        ano_mes = sat_partes[2] + '_' + sat_partes[3]
        pattern = r'SPORT_(RAW|DRD)_\d{4}_\d{2}_\d{2}\.\d{2}_\d{2}_\d{2}_[A-Z0-9]'

    else:
        pattern = ''
        directory = ''
        satelite = ''
        return directory, pattern, satelite

    directory = storage_path + "/" + satelite + missao + '/' + ano_mes + '/' + sensor
    return directory, pattern, satelite

def get_files_info(directory, extension=None):
    files = []
    for filename in os.listdir(directory):
        if extension:
            if not filename.endswith(extension):
                continue
        if filename.startswith(".0."):
            continue

        path = os.path.join(directory, filename)
        if os.path.isfile(path):
            files.append({'name': filename, 'size': os.path.getsize(path)})

    return files

def define_md5_cba(filename):
    with open(filename, 'r') as arquivo:
        linha = arquivo.readline()
        partes = linha.split()
        if len(partes) == 0:
            return ''
        md5 = partes[0]
        return md5
    
def send_email(subject, body, is_adm = False):
    asyncio.run(send_email_background(subject, body, is_adm))

async def send_email_background(subject, body, is_adm = False):
    tentativas_maximas = 3
    tentativa_atual = 0
    sleep_sec = 5
    while tentativa_atual < tentativas_maximas:
        try:
            #Cria uma conexão com o servidor SMTP do Gmail
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)

            # Configura o e-mail
            from_email = smtp_username
            to_email = contact_adm if is_adm else contacts
            to_email_list = [email.strip() for email in to_email.split(',')]

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = 'noreply@inpe.br'
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Envia o e-mail
            server.sendmail(from_email, to_email_list, msg.as_string())

            # Finaliza a conexão
            server.quit()
            return True
        except Exception as e:
            tentativa_atual += 1
            print(f"Tentando novamente em {sleep_sec} segundos... (tentativa {tentativa_atual}/{tentativas_maximas})")
            await asyncio.sleep(sleep_sec)
    return False

def send_email_user(email, body, subject):
    try:
        #Cria uma conexão com o servidor SMTP do Gmail
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Configura o e-mail
        from_email = smtp_username
        to_email = email

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = 'noreply@inpe.br'
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Envia o e-mail
        server.sendmail(from_email, to_email, msg.as_string())

        # Finaliza a conexão
        server.quit()

        return f"Email enviado para {email} com as orientações para acesso!", None
    
    except Exception as e:
        print(e)        
        return f"Falha no envio de email, favor realizar o processo novamente", e

def get_datetime_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_date_str():
    return datetime.now().strftime('%Y-%m-%d')

def convert_datetime_to_string(data:datetime):
    return data.strftime('%d/%m/%Y')

def convert_string_datetime_br(data:str):
    return datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')

def gera_hash_MD5(string):
    string_encoded = string.encode("utf-8")
    hash_object = hashlib.sha256(string_encoded)
    hash_value = hash_object.hexdigest()
    return hash_value

def verify_token(token):
    try:
        s = URLSafeTimedSerializer(key_reset_password)
        email = s.loads(token, salt='reset-passwd', max_age=1800)
        return True, email
    except:
        return False, None
    
def generate_random_password(length=10):
    # Definindo os caracteres permitidos na senha
    characters = string.ascii_letters + string.digits
    # Gerando a senha aleatória
    random_password = ''.join(random.choice(characters) for _ in range(length))
    return random_password

def pagination(dados, page, per_page):
    total_itens = len(dados)
    page_total = math.ceil(total_itens / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_dados = dados[start:end]
    pages_info = {
        'total_pages': page_total,
        'total_items': total_itens
    }
    return paginated_dados, pages_info

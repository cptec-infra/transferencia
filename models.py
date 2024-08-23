from datetime import datetime

class UsuarioModel:
    def __init__(self, id, nome, email, senha, empresa, perfil, ativo) -> None:
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.empresa = empresa
        self.perfil = perfil
        self.ativo = ativo 
        self.darkTheme = 0

    def get_id(self):
        return self.id

    def set_id(self, value):
        self.id = value

    def get_nome(self):
        return self.nome

    def set_nome(self, value):
        self.nome = value

    def get_email(self):
        return self.email

    def set_email(self, value):
        self.email = value

    def get_senha(self):
        return self.senha

    def set_senha(self, value):
        self.senha = value

    def get_empresa(self):
        return self.empresa

    def set_empresa(self, value):
        self.empresa = value

    def get_adm(self):
        return self.adm

    def set_adm(self, value):
        self.adm = value

    def get_ativo(self):
        return self.ativo

    def set_ativo(self, value):
        self.ativo = value

    def get_dark_theme(self):
        return self.darkTheme

    def set_dark_theme(self, value):
        self.darkTheme = value    

    def __str__(self) -> str:
        return self._nome
    
class DadoModel:
    def __init__(self):
        self.id = None
        self.nome = None
        self.download_status = None
        self.download_start_datetime = None
        self.download_end_datetime = None
        self.md5_cp_status = None
        self.md5_cp_start_datetime = None
        self.md5_cp_end_datetime = None
        self.md5_validated = None
        self.md5_validated_datetime = None
        self.storing_status = None
        self.storing_start_datetime = None
        self.storing_end_datetime = None
        self.retry_user = None
        self.retry_user_name = None
        self.retry_datetime = None
        self.download_time = None
        self.md5_cp_time = None
        self.storing_time = None
        self.error = None
        self.id_dado_retry = None
        self.filesize = None
        self.date_cba = None

    def get_id(self):
        return self.id

    def set_id(self, value):
        self.id = value

    def get_nome(self):
        return self.nome

    def set_nome(self, value):
        self.nome = value

    def get_download_status(self):
        return self.download_status

    def set_download_status(self, value):
        self.download_status = value

    def get_download_start_datetime(self):
        return self.download_start_datetime

    def set_download_start_datetime(self, value):
        self.download_start_datetime = value

    def get_download_end_datetime(self):
        return self.download_end_datetime

    def set_download_end_datetime(self, value):
        self.download_end_datetime = value

    def get_md5_cp_status(self):
        return self.md5_cp_status

    def set_md5_cp_status(self, value):
        self.md5_cp_status = value

    def get_md5_cp_start_datetime(self):
        return self.md5_cp_start_datetime

    def set_md5_cp_start_datetime(self, value):
        self.md5_cp_start_datetime = value

    def get_md5_cp_end_datetime(self):
        return self.md5_cp_end_datetime

    def set_md5_cp_end_datetime(self, value):
        self.md5_cp_end_datetime = value

    def get_md5_validated(self):
        return self.md5_validated

    def set_md5_validated(self, value):
        self.md5_validated = value

    def get_md5_validated_datetime(self):
        return self.md5_validated_datetime

    def set_md5_validated_datetime(self, value):
        self.md5_validated_datetime = value

    def get_storing_status(self):
        return self.storing_status

    def set_storing_status(self, value):
        self.storing_status = value

    def get_storing_start_datetime(self):
        return self.storing_start_datetime

    def set_storing_start_datetime(self, value):
        self.storing_start_datetime = value

    def get_storing_end_datetime(self):
        return self.storing_end_datetime

    def set_storing_end_datetime(self, value):
        self.storing_end_datetime = value

    def get_retry_user(self):
        return self.retry_user

    def set_retry_user(self, value):
        self.retry_user = value

    def get_retry_user_name(self):
        return self.retry_user_name

    def set_retry_user_name(self, value):
        self.retry_user_name = value

    def get_retry_datetime(self):
        return self.retry_datetime

    def set_retry_datetime(self, value):
        self.retry_datetime = value

    def get_download_time(self):
        return self.download_time

    def set_download_time(self, value):
        self.download_time = value

    def get_md5_cp_time(self):
        return self.md5_cp_time

    def set_md5_cp_time(self, value):
        self.md5_cp_time = value

    def get_storing_time(self):
        return self.storing_time

    def set_storing_time(self, value):
        self.storing_time = value

    def get_error(self):
        return self.error

    def set_error(self, value):
        self.error = value

    def get_id_dado_retry(self):
        return self.id_dado_retry

    def set_id_dado_retry(self, value):
        self.id_dado_retry = value

    def get_filesize(self):
        return self.filesize
    
    def set_filesize(self, value):
        self.filesize = value

    def get_date_cba(self):
        return self.date_cba
    
    def set_date_cba(self, value):
        self.date_cba = value

    def __str__(self) -> str:
        return self.nome
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'download_status': self.download_status,
            'download_start_datetime': self.download_start_datetime,
            'download_end_datetime': self.download_end_datetime.strftime("%d/%m/%Y") if self.download_end_datetime else None,
            'download_time': str(self.download_time) if self.download_time else None,
            'md5_cp_status': self.md5_cp_status,
            'md5_cp_start_datetime': self.md5_cp_start_datetime,
            'md5_cp_end_datetime': self.md5_cp_end_datetime,
            'md5_validated': self.md5_validated,
            'md5_validated_datetime': self.md5_validated_datetime,
            'storing_status': self.storing_status,
            'storing_start_datetime': self.storing_start_datetime,
            'storing_end_datetime': self.storing_end_datetime,
            'retry_user': self.retry_user,
            'retry_user_name': self.retry_user_name,
            'retry_datetime': self.retry_datetime,
            'download_time': str(self.download_time) if self.download_time else None,
            'md5_cp_time': str(self.md5_cp_time) if self.md5_cp_time else None,
            'storing_time': str(self.storing_time) if self.storing_time else None,
            'error': self.error,
            'id_dado_retry': self.id_dado_retry,
            'filesize': self.filesize,
            'date_cba': self.date_cba
        }
    
class DartcomModel:
    def __init__(self):
        self.id = None
        self.nome = None
        self.modified_datetime = None
        self.compressed_status = None
        self.compressed_start_datetime = None
        self.compressed_end_datetime = None  
        self.storing_status = None
        self.storing_start_datetime = None
        self.storing_end_datetime = None
        self.retry_user = None
        self.retry_user_name = None
        self.retry_datetime = None
        self.compressed_time = None
        self.storing_time = None
        self.error = None
        self.id_dartcom_retry = None
        self.filesize = None
        self.id_dartcom_satelite = None
        self.date_path = None
        self.dartcom_satelite: DartcomSateliteModel = None
        self.missao = None

    def get_id(self):
        return self.id

    def set_id(self, value):
        self.id = value

    def get_nome(self):
        return self.nome

    def set_nome(self, value):
        self.nome = value

    def get_modified_datetime(self):
        return self.modified_datetime

    def set_modified_datetime(self, value):
        self.modified_datetime = value

    def get_compressed_status(self):
        return self.compressed_status

    def set_compressed_status(self, value):
        self.compressed_status = value

    def get_compressed_start_datetime(self):
        return self.compressed_start_datetime

    def set_compressed_start_datetime(self, value):
        self.compressed_start_datetime = value

    def get_compressed_end_datetime(self):
        return self.compressed_end_datetime

    def set_compressed_end_datetime(self, value):
        self.compressed_end_datetime = value

    def get_storing_status(self):
        return self.storing_status

    def set_storing_status(self, value):
        self.storing_status = value

    def get_storing_start_datetime(self):
        return self.storing_start_datetime

    def set_storing_start_datetime(self, value):
        self.storing_start_datetime = value

    def get_storing_end_datetime(self):
        return self.storing_end_datetime

    def set_storing_end_datetime(self, value):
        self.storing_end_datetime = value

    def get_retry_user(self):
        return self.retry_user

    def set_retry_user(self, value):
        self.retry_user = value

    def get_retry_user_name(self):
        return self.retry_user_name

    def set_retry_user_name(self, value):
        self.retry_user_name = value

    def get_retry_datetime(self):
        return self.retry_datetime

    def set_retry_datetime(self, value):
        self.retry_datetime = value

    def get_compressed_time(self):
        return self.compressed_time

    def set_compressed_time(self, value):
        self.compressed_time = value

    def get_storing_time(self):
        return self.storing_time

    def set_storing_time(self, value):
        self.storing_time = value

    def get_error(self):
        return self.error

    def set_error(self, value):
        self.error = value

    def get_id_dartcom_retry(self):
        return self.id_dartcom_retry

    def set_id_dartcom_retry(self, value):
        self.id_dartcom_retry = value

    def get_filesize(self):
        return self.filesize

    def set_filesize(self, value):
        self.filesize = value

    def get_id_dartcom_satelite(self):
        return self.id_dartcom_satelite

    def set_id_dartcom_satelite(self, value):
        self.id_dartcom_satelite = value

    def get_date_path(self):
        return self.date_path

    def set_date_path(self, value):
        self.date_path = value

    def get_dartcom_satelite(self):
        return self.dartcom_satelite

    def set_dartcom_satelite(self, value):
        self.dartcom_satelite = value

    def get_missao(self):
        return self.missao

    def set_missao(self, value):
        self.missao = value

    def __str__(self) -> str:
        return self.nome
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'modified_datetime': self.modified_datetime,
            'compressed_status': self.compressed_status,
            'compressed_start_datetime': self.compressed_start_datetime,
            'compressed_end_datetime': self.compressed_end_datetime,
            'storing_status': self.storing_status,
            'storing_start_datetime': self.storing_start_datetime,
            'storing_end_datetime': self.storing_end_datetime,
            'retry_user': self.retry_user,
            'retry_user_name': self.retry_user_name,
            'retry_datetime': self.retry_datetime,
            'compressed_time': str(self.compressed_time) if self.compressed_time else None,
            'storing_time': str(self.storing_time) if self.storing_time else None,
            'error': self.error,
            'id_dartcom_retry': self.id_dartcom_retry,
            'filesize': self.filesize,
            'id_dartcom_satelite': self.id_dartcom_satelite,
            'date_path': self.date_path,
            'missao': self.missao
        }
    
class DartcomAntenaModel:
    def __init__(self, id, nome) -> None:
        self.id = id
        self.nome = nome

    def get_id(self):
        return self.id

    def set_id(self, value):
        self.id = value

    def get_nome(self):
        return self.nome

    def set_nome(self, value):
        self.nome = value

    def __str__(self) -> str:
        return self.nome
    
class DartcomSateliteModel:
    def __init__(self, id, id_dartcom_antena, nome, sensor, data_type, satelite_path, template_name, command, is_compressed, is_epsl0, epsl0_template, template_path_origin_scp) -> None:
        self.id = id
        self.id_dartcom_antena = id_dartcom_antena
        self.nome = nome
        self.sensor = sensor
        self.data_type = data_type
        self.satelite_path = satelite_path
        self.template_name = template_name
        self.command = command
        self.is_compressed = is_compressed
        self.is_epsl0 = is_epsl0
        self.epsl0_template = epsl0_template
        self.template_path_origin_scp = template_path_origin_scp

    def get_id(self):
        return self.id

    def get_id_dartcom_antena(self):
        return self.id_dartcom_antena

    def get_nome(self):
        return self.nome

    def get_sensor(self):
        return self.sensor

    def get_data_type(self):
        return self.data_type

    def get_satelite_path(self):
        return self.satelite_path
    
    def get_template_name(self):
        return self.template_name

    def get_command(self):
        return self.command
    
    def get_is_compressed(self):
        return self.is_compressed
    
    def get_is_epsl0(self):
        return self.is_epsl0
    
    def get_epsl0_template(self):
        return self.epsl0_template

    def set_id(self, id):
        self.id = id

    def set_id_dartcom_antena(self, id_dartcom_antena):
        self.id_dartcom_antena = id_dartcom_antena

    def set_nome(self, nome):
        self.nome = nome

    def set_sensor(self, sensor):
        self.sensor = sensor

    def set_data_type(self, data_type):
        self.data_type = data_type

    def set_satelite_path(self, satelite_path):
        self.satelite_path = satelite_path

    def set_template_name(self, template_name):
        self.template_name = template_name

    def set_command(self, command):
        self.command = command

    def set_is_compressed(self, is_compressed):
        self.is_compressed = is_compressed

    def set_is_epsl0(self, is_epsl0):
        self.is_epsl0 = is_epsl0

    def set_epsl0_template(self, epsl0_template):
        self.epsl0_template = epsl0_template

    def get_template_path_origin_scp(self):
        return self.template_path_origin_scp
    
    def set_template_path_origin_scp(self, value):
        self.template_path_origin_scp = value

    def __str__(self) -> str:
        return self.nome

class MD5CbaZerado:
    def __init__(self, id, dado_nome, registro_datetime) -> None:
        self.id = id
        self.dado_nome = dado_nome
        self.registro_datetime = registro_datetime

    def get_id(self):
        return self.id

    def set_id(self, value):
        self.id = value

    def get_dado_nome(self):
        return self.dado_nome

    def set_dado_nome(self, value):
        self.dado_nome = value

    def get_registro_datetime(self):
        return self.registro_datetime

    def set_registro_datetime(self, value):
        self.registro_datetime = value

    def __str__(self) -> str:
        return self.dado_nome
from flask import session
from datetime import datetime, timedelta
from connection import *
from models import DadoModel, MD5CbaZerado

class DadoRepository:
    def __init__(self) -> None:
        self.db = get_db()

    def get_satellite_name(self, dado: str):
        sat_partes = dado.split('_')
        name = sat_partes[0]
        missao = ''
        if name == 'CBERS' or name == 'AMAZONIA':
            name = name + '_' + sat_partes[1]
        return name
        

    def get_report_data(self, date_start = None, date_end = None):    
        try:
            cursor = self.db.cursor()
            query = f"SELECT * FROM dado WHERE date(download_start_datetime) >= '{date_start}' and date(download_start_datetime) <= '{date_end}' order by download_start_datetime"
            cursor.execute(query)
            result = cursor.fetchall()
            dados = []
            date_volume = {}
            date_quantidade = {}
            date_satellite = {}
            date_tempo_download = {}
            date_tempo_armazenado = {}

            
            for d in result:
                date = d[3].date()  
                volume_temp = d[15] if d[15] else 0
                volume = volume_temp / (1024**3)
                satellite = self.get_satellite_name(d[1])
                
                # Define o tempo do download
                download_start_datetime=d[3]
                download_end_datetime=d[4]
                download_time = timedelta(0)

                if download_start_datetime and download_end_datetime:
                    download_time = download_end_datetime - download_start_datetime

                # Define o tempo de armazenamento
                storing_start_datetime=d[11]
                storing_end_datetime=d[12]
                storing_time = timedelta(0)

                if storing_start_datetime and storing_end_datetime:
                    storing_time = storing_end_datetime - storing_start_datetime
                
                if date in date_volume:
                    date_volume[date] += volume
                    date_quantidade[date] += 1
                    date_tempo_download[date] += download_time
                    
                else:
                    date_volume[date] = volume
                    date_quantidade[date] = 1
                    date_tempo_download[date] = download_time

                if date in date_tempo_armazenado:
                    date_tempo_armazenado[date] += storing_time
                else:
                    date_tempo_armazenado[date] = storing_time

                if satellite in date_satellite:
                    date_satellite[satellite] += 1
                else:
                    date_satellite[satellite] = 1                

                dado = DadoModel()
                dado.set_id(d[0])
                dado.set_nome(d[1])
                dado.set_download_status(d[2])
                dado.set_download_start_datetime(d[3])
                dado.set_download_end_datetime(d[4])
                dado.set_md5_cp_status(d[5])
                dado.set_md5_cp_start_datetime(d[6])
                dado.set_md5_cp_end_datetime(d[7])
                dado.set_md5_validated(d[8])
                dado.set_md5_validated_datetime(d[9])
                dado.set_storing_status(d[10])
                dado.set_storing_start_datetime(d[11])
                dado.set_storing_end_datetime(d[12])
                dado.set_retry_user(d[13])
                dado.set_retry_datetime(d[14])
                dado.set_download_time(download_time)
                dado.set_storing_time(storing_time)
                dado.set_filesize(d[15])
                dado.set_date_cba(d[16])
                dados.append(dado)
            
            volume_for_date = [(date, volume) for date, volume in date_volume.items()]            
            quantidade_for_date = [(date, quantidade) for date, quantidade in date_quantidade.items()]
            tempo_for_date_download = [(date, download) for date, download in date_tempo_download.items()]
            tempo_for_date_armazenamento = [(date, armazenamento) for date, armazenamento in date_tempo_armazenado.items()]

            date_satellite = dict(sorted(date_satellite.items()))
            satellite_for_date = [(date, sateliite) for date, sateliite in date_satellite.items()]

            cursor.close()
            self.db.commit()
            return dados, None, volume_for_date, quantidade_for_date, satellite_for_date, tempo_for_date_download, tempo_for_date_armazenamento

        except Exception as e:
            print(e)
            return [], e, [], [], [], [], []    
    
    def find_data(self, name):
        try:
            cursor = self.db.cursor()
            cursor.execute('select id_dado from dado where nome=%s',(name))
            result = cursor.fetchone()
            self.db.commit()
            cursor.close()
            if result:
                return True, None
            else:
                return False, None

        except Exception as e:
            print(e)
            return True, e
        
    def get_daily_volume(self, date_start = None, date_end = None):
        try:
            cursor = self.db.cursor()
            if date_start and date_end:
                query = f"select sum(filesize) from dado WHERE date(download_start_datetime) >= '{date_start}' and date(download_start_datetime) <= '{date_end}'"
            # elif data:
                # query = 'select sum(filesize) from dado where date(download_end_datetime) = date(now())'
            else:
                query = 'select sum(filesize) from dado where date(download_end_datetime) = date(now())'
            cursor.execute(query)
            result = cursor.fetchone()
            self.db.commit()
            cursor.close()
            return result[0]
        except Exception as e:
            print(e)
            return None
        
    def get_data(self, id):
        try:
            cursor = self.db.cursor()
            cursor.execute('select * from dado where id_dado=%s',(id))
            result = cursor.fetchone()
            self.db.commit()
            cursor.close()
            if result:
                download_start_datetime=result[3]
                download_end_datetime=result[4]
                download_time = None
                if download_start_datetime and download_end_datetime:
                    download_time = download_end_datetime - download_start_datetime

                md5_cp_start_datetime = result[6]
                md5_cp_end_datetime = result[7]
                md5_cp_time = None
                if md5_cp_start_datetime and md5_cp_end_datetime:
                    md5_cp_time = md5_cp_end_datetime - md5_cp_start_datetime

                storing_start_datetime=result[11]
                storing_end_datetime=result[12]
                storing_time = None
                if storing_start_datetime and storing_end_datetime:
                    storing_time = storing_end_datetime - storing_start_datetime
                
                dado = DadoModel()
                dado.set_id(result[0])
                dado.set_nome(result[1])
                dado.set_download_status(result[2])
                dado.set_download_start_datetime(result[3])
                dado.set_download_end_datetime(result[4])
                dado.set_md5_cp_status(result[5])
                dado.set_md5_cp_start_datetime(result[6])
                dado.set_md5_cp_end_datetime(result[7])
                dado.set_md5_validated(result[8])
                dado.set_md5_validated_datetime(result[9])
                dado.set_storing_status(result[10])
                dado.set_storing_start_datetime(result[11])
                dado.set_storing_end_datetime(result[12])
                dado.set_retry_user(result[13])
                dado.set_retry_datetime(result[14])                
                dado.set_download_time(download_time)
                dado.set_md5_cp_time(md5_cp_time)
                dado.set_storing_time(storing_time)
                dado.set_filesize(result[15])
                dado.set_date_cba(result[16])
                return dado, None
            else:
                return None, None

        except Exception as e:
            print(e)
            return None, e
        
    def get_history(self, id):
        try:
            cursor = self.db.cursor()
            cursor.execute('select h.id_dado_historico,h.id_dado,h.nome,h.download_status,h.download_start_datetime,h.download_end_datetime,h.md5_cp_status,h.md5_cp_start_datetime,h.md5_cp_end_datetime,h.md5_validated,h.md5_validated_datetime,h.storing_status,h.storing_start_datetime,h.storing_end_datetime,h.retry_user,h.retry_datetime,u.nome,h.filesize,h.date_cba from dado_historico h left join usuario u on (h.retry_user = u.id_usuario) where id_dado=%s order by id_dado_historico',(id))
            result =  cursor.fetchall()
            historico = []
            for h in result:
                download_start_datetime=h[4]
                download_end_datetime=h[5]
                download_time = None
                if download_start_datetime and download_end_datetime:
                    download_time = download_end_datetime - download_start_datetime

                md5_cp_start_datetime = h[7]
                md5_cp_end_datetime = h[8]
                md5_cp_time = None
                if md5_cp_start_datetime and md5_cp_end_datetime:
                    md5_cp_time = md5_cp_end_datetime - md5_cp_start_datetime

                storing_start_datetime=h[12]
                storing_end_datetime=h[13]
                storing_time = None
                if storing_start_datetime and storing_end_datetime:
                    storing_time = storing_end_datetime - storing_start_datetime
                
                dado = DadoModel()
                dado.set_id(h[1])
                dado.set_nome(h[2])
                dado.set_download_status(h[3])
                dado.set_download_start_datetime(h[4])
                dado.set_download_end_datetime(h[5])
                dado.set_md5_cp_status(h[6])
                dado.set_md5_cp_start_datetime(h[7])
                dado.set_md5_cp_end_datetime(h[8])
                dado.set_md5_validated(h[9])
                dado.set_md5_validated_datetime(h[10])
                dado.set_storing_status(h[11])
                dado.set_storing_start_datetime(h[12])
                dado.set_storing_end_datetime(h[13])
                dado.set_retry_user(h[14])
                dado.set_retry_datetime(h[15])
                dado.set_retry_user_name(h[16])
                dado.set_download_time(download_time)
                dado.set_md5_cp_time(md5_cp_time)
                dado.set_storing_time(storing_time)
                dado.set_filesize(h[17])
                dado.set_date_cba(h[18])
                historico.append(dado)
            return historico, None

        except Exception as e:
            print(e)
            return None, e

    def get_all(self, search_data):
        try:
            dados = []            
            cursor = self.db.cursor()            

            if search_data:
                search_data = "%" + str(search_data) + "%"
                query="""select *,case when download_status = 'Executando' or download_status = 'Erro' or md5_cp_status = 'Executando' or md5_cp_status = 'Erro' or (md5_validated is null) or (md5_validated = 0) or storing_status='Executando' or storing_status = 'Erro' then 0 else 1 end as dado_status from dado where nome like %s order by dado_status, id_dado desc"""
                cursor.execute(query, (search_data))
            else:
                cursor.execute('select *,case when download_status = "Executando" or download_status = "Erro" or md5_cp_status = "Executando" or md5_cp_status = "Erro" or (md5_validated is null) or (md5_validated = 0) or storing_status="Executando" or storing_status = "Erro" then 0 else 1 end as dado_status from dado order by     dado_status, id_dado desc')

            result = cursor.fetchall()

            for d in result:
                download_start_datetime=d[3]
                download_end_datetime=d[4]
                download_time = None
                if download_start_datetime and download_end_datetime:
                    download_time = download_end_datetime - download_start_datetime

                storing_start_datetime=d[11]
                storing_end_datetime=d[12]
                storing_time = None
                if storing_start_datetime and storing_end_datetime:
                    storing_time = storing_end_datetime - storing_start_datetime
                
                dado = DadoModel()
                dado.set_id(d[0])
                dado.set_nome(d[1])
                dado.set_download_status(d[2])
                dado.set_download_start_datetime(d[3])
                dado.set_download_end_datetime(d[4])
                dado.set_md5_cp_status(d[5])
                dado.set_md5_cp_start_datetime(d[6])
                dado.set_md5_cp_end_datetime(d[7])
                dado.set_md5_validated(d[8])
                dado.set_md5_validated_datetime(d[9])
                dado.set_storing_status(d[10])
                dado.set_storing_start_datetime(d[11])
                dado.set_storing_end_datetime(d[12])
                dado.set_retry_user(d[13])
                dado.set_retry_datetime(d[14])
                dado.set_download_time(download_time)
                dado.set_storing_time(storing_time)
                dado.set_filesize(d[15])
                dado.set_date_cba(d[16])
                dados.append(dado)
            cursor.close()
            self.db.commit()
            return dados, None

        except Exception as e:
            print('--------')
            print(e)
            return None, e

    def get_retries(self):
        try:
            cursor = self.db.cursor()
            cursor.execute('select dado.id_dado, dado.nome, download_status, download_start_datetime, download_end_datetime, md5_cp_status, md5_cp_start_datetime, md5_cp_end_datetime, md5_validated, md5_validated_datetime, storing_status, storing_start_datetime, storing_end_datetime, retry_user, retry_datetime, error, id_dado_retry from dado join dado_retry on dado.id_dado = dado_retry.id_dado order by id_dado desc')
            result = cursor.fetchall()
            dados:list[DadoModel] = []
            for d in result:
                download_start_datetime=d[3]
                download_end_datetime=d[4]
                download_time = None
                if download_start_datetime and download_end_datetime:
                    download_time = download_end_datetime - download_start_datetime

                storing_start_datetime=d[11]
                storing_end_datetime=d[12]
                storing_time = None
                if storing_start_datetime and storing_end_datetime:
                    storing_time = storing_end_datetime - storing_start_datetime
                
                dado = DadoModel()
                dado.set_id(d[0])
                dado.set_nome(d[1])
                dado.set_download_status(d[2])
                dado.set_download_start_datetime(d[3])
                dado.set_download_end_datetime(d[4])
                dado.set_md5_cp_status(d[5])
                dado.set_md5_cp_start_datetime(d[6])
                dado.set_md5_cp_end_datetime(d[7])
                dado.set_md5_validated(d[8])
                dado.set_md5_validated_datetime(d[9])
                dado.set_storing_status(d[10])
                dado.set_storing_start_datetime(d[11])
                dado.set_storing_end_datetime(d[12])
                dado.set_retry_user(d[13])
                dado.set_retry_datetime(d[14])
                dado.set_download_time(download_time)
                dado.set_storing_time(storing_time)
                dado.set_error(d[15])
                dado.set_id_dado_retry(d[16])
                dados.append(dado)
            cursor.close()
            self.db.commit()
            return dados, None

        except Exception as e:
            print('--------')
            print(e)
            return None, e
        
    def get_errors(self):
        try:
            cursor = self.db.cursor()
            cursor.execute('select id_dado,nome, download_status, md5_cp_status, md5_validated, storing_status from dado where (download_status = \'erro\' or md5_cp_status = \'erro\' or !md5_validated or storing_status = \'erro\') and retry_user is null order by id_dado desc')
            result = cursor.fetchall()
            dados = []
            for d in result:
                
                dado = DadoModel()
                dado.set_id(d[0])
                dado.set_nome(d[1])
                dado.set_download_status(d[2])
                dado.set_md5_cp_status(d[3])
                dado.set_md5_validated(d[4])
                dado.set_storing_status(d[5])
                dados.append(dado)
            cursor.close()
            self.db.commit()
            return dados, None
        except Exception as e:
            print(e)
            return None, e
        
    def set_retry(self, selected):
        try:
            cursor = self.db.cursor()
            for id_dado in selected:
                cursor.execute('select nome,concat(if(download_status = "Erro", "download",""), if(md5_cp_status = "Erro","md5-cp",""), if(!md5_validated, "validacao",""), if(storing_status="Erro", "armazenamento","")) as error from dado where id_dado = %s', (id_dado))
                result = cursor.fetchone()
                if result:
                    name = result[0]
                    error = result[1]

                    cursor.execute('insert into dado_retry(id_dado,nome,error) values(%s,%s,%s)',(id_dado, name, error))
                    cursor.execute('update dado set retry_user=%s, retry_datetime = %s where id_dado=%s', (session['id'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id_dado))

            self.db.commit()
            cursor.close()
            return None
        except Exception as e:
            print(e)
            return e
        
    def set_auto_retry(self, id_dado, id_admin):
        try:
            cursor = self.db.cursor()
            cursor.execute('select nome,concat(if(download_status = "Erro", "download",""), if(md5_cp_status = "Erro","md5-cp",""), if(!md5_validated, "validacao",""), if(storing_status="Erro", "armazenamento","")) as error from dado where id_dado = %s', (id_dado))
            result = cursor.fetchone()
            if result:
                name = result[0]
                error = result[1]

                cursor.execute('insert into dado_retry(id_dado,nome,error) values(%s,%s,%s)',(id_dado, name, error))
                cursor.execute('update dado set retry_user=%s, retry_datetime=%s  where id_dado=%s', (id_admin, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id_dado))

            self.db.commit()
            cursor.close()
            return None
        except Exception as e:
            print(e)
            return e

    def delete_retry(self,  id_dado_retry):
        try:
            cursor = self.db.cursor()
            cursor.execute('delete from dado_retry where id_dado_retry=%s', (id_dado_retry))
            self.db.commit()
            cursor.close()
            return None
        except Exception as e:
            print(e)
            return e

    def insert_dado(self, dado: DadoModel):   
        try:
            cursor = self.db.cursor()
            cursor.execute('insert into dado (nome, download_start_datetime, download_status, date_cba) values (%s, %s, %s, %s)', (dado.nome, dado.download_start_datetime, dado.download_status, dado.date_cba))
            id = cursor.lastrowid
            self.db.commit()
            cursor.close()
            #id do dado e error_db
            return id, False
        except Exception as e:
            print(e)
            #id do dado e error_db
            return None, e
        
    def insert_dado_historico(self, id_dado):   
        try:
            cursor = self.db.cursor()
            cursor.execute('insert into dado_historico (id_dado,nome,download_status,download_start_datetime,download_end_datetime,md5_cp_status,md5_cp_start_datetime,md5_cp_end_datetime,md5_validated,md5_validated_datetime,storing_status,storing_start_datetime,storing_end_datetime,retry_user,retry_datetime,filesize,date_cba) select * from dado where id_dado=%s', (id_dado))
            self.db.commit()
            cursor.close()
            #id do dado e error_db
            return False
        except Exception as e:
            print(e)
            #id do dado e error_db
            return e
        
    def update_reset(self, dado: DadoModel):
        try:
            cursor = self.db.cursor()
            cursor.execute('update dado set download_status=%s,download_start_datetime=%s,download_end_datetime=%s,md5_cp_status=%s,md5_cp_start_datetime=%s,md5_cp_end_datetime=%s,md5_validated=%s,md5_validated_datetime=%s,storing_status=%s,storing_start_datetime=%s,storing_end_datetime=%s,retry_user=%s,retry_datetime=%s where id_dado=%s',(dado.download_status,dado.download_start_datetime,dado.download_end_datetime,dado.md5_cp_status,dado.md5_cp_start_datetime,dado.md5_cp_end_datetime,dado.md5_validated,dado.md5_validated_datetime,dado.storing_status,dado.storing_start_datetime,dado.storing_end_datetime,dado.retry_user,dado.retry_datetime,dado.id))
            self.db.commit()
            cursor.close()
            return False
        except Exception as e:
            print(f'update_reset {e}')
            return e 
        
    def update_dado(self, dado: DadoModel):
        try:
            cursor = self.db.cursor()
            cursor.execute('update dado set download_start_datetime=%s, download_status=%s, date_cba=%s where id_dado=%s', (dado.download_start_datetime, dado.download_status, dado.date_cba, dado.id))
            self.db.commit()
            cursor.close()
            return False
        except Exception as e:
            print(f'update_dado {e}')
            return e
        

    def update_download(self, dado: DadoModel):
        try:
            cursor = self.db.cursor()
            cursor.execute('update dado set download_status=%s, download_end_datetime=%s, filesize=%s where id_dado=%s', (dado.download_status, dado.download_end_datetime, dado.filesize, dado.id))
            self.db.commit()
            cursor.close()
            return False
        except Exception as e:        
            print(f'update_download {e}')
            return e
        
    def update_md5_cp_start(self, dado: DadoModel):
        try:
            cursor = self.db.cursor()
            cursor.execute('update dado set md5_cp_status=%s, md5_cp_start_datetime=%s where id_dado=%s', (dado.md5_cp_status, dado.md5_cp_start_datetime, dado.id))
            self.db.commit()
            cursor.close()
            return False
        except Exception as e:
            print(f'update_md5_cp_start {e}')       
            return e

    def update_md5_cp(self, dado: DadoModel):
        try:
            cursor = self.db.cursor()
            cursor.execute('update dado set md5_cp_status=%s, md5_cp_end_datetime=%s where id_dado=%s', (dado.md5_cp_status, dado.md5_cp_end_datetime, dado.id))
            self.db.commit()
            cursor.close()
            return False
        except Exception as e:
            print(f'update_md5_cp {e}')               
            return e

    def update_md5_validated(self, dado: DadoModel):
        try:
            cursor = self.db.cursor()
            cursor.execute('update dado set md5_validated=%s, md5_validated_datetime=%s where id_dado=%s', (dado.md5_validated, dado.md5_validated_datetime, dado.id))
            self.db.commit()
            cursor.close()
            return False
        except Exception as e:      
            print(f'update_md5_validated {e}')      
            return e

    def update_storing_running(self, dado: DadoModel):
        try:
            cursor = self.db.cursor()
            cursor.execute('update dado set storing_status=%s, storing_start_datetime=%s where id_dado=%s', (dado.storing_status, dado.storing_start_datetime, dado.id))
            self.db.commit()
            cursor.close()
            return False
        except Exception as e:       
            print(f'update_storing_running {e}')       
            return e
        
    def update_storing_completed(self, dado: DadoModel):
        try:
            cursor = self.db.cursor()
            cursor.execute('update dado set storing_status=%s, storing_end_datetime=%s where id_dado=%s', (dado.storing_status, dado.storing_end_datetime, dado.id))
            self.db.commit()
            cursor.close()
            return False
        except Exception as e:        
            print(f'update_storing_completed {e}')       
            return e
        
    def save_md5_cba_error(self, nome_dado):
        try:
            cursor = self.db.cursor()
            cursor.execute('select id_md5_cba_zerado from md5_cba_zerado where nome_dado=%s', (nome_dado))
            result = cursor.fetchone()
            if not result:
                cursor.execute('insert into md5_cba_zerado(nome_dado) values (%s)', (nome_dado))
            self.db.commit()
            cursor.close()
            return False
        except Exception as e:
            print(f'save_md5_cba_error {e}')
            return e
        
    def get_md5_cba_zerados(self):
        try:
            cursor = self.db.cursor()
            cursor.execute('select id_md5_cba_zerado, nome_dado, registro_datetime from md5_cba_zerado order by id_md5_cba_zerado desc')
            result = cursor.fetchall()
            list_md5_cba_zerados = []
            for r in result:
                
                md5 = MD5CbaZerado(id=r[0], dado_nome=r[1], registro_datetime=r[2])
                list_md5_cba_zerados.append(md5)
                cursor.close()
            self.db.commit()
            return list_md5_cba_zerados, None

        except Exception as e:
            print(e)
        
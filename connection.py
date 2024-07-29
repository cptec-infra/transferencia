import pymysql.cursors
import configparser
from flask import g

config = configparser.ConfigParser()
config.read("config.ini")

def get_db():
    if 'db' not in g:
        # Conectando ao banco de dados
        g.db = pymysql.connect(
            host=config.get('MYSQL', 'host'),
            user=config.get('MYSQL', 'user'),
            password=config.get('MYSQL', 'password'),
            db=config.get('MYSQL', 'bd')
        )
    return g.db

def close_db(error):
    if 'db' in g:
        # Fechando a conexão com o banco de dados
        g.db.close()
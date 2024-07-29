from flask import session
from connection import *
from models import UsuarioModel

class UserRepository:
    def __init__(self) -> None:
        self.db = get_db()

    def login(self, email, senha):
        try:
            cursor = self.db.cursor()            
            cursor.execute('select id_usuario,nome, email, empresa, perfil, ativo, dark_theme, first_login from usuario where email=%s and senha=%s and ativo', (email, senha))
            result = cursor.fetchone()
            
            if result:
                usuario = UsuarioModel(id=result[0], nome=result[1], email=result[2], empresa=result[3], perfil=result[4], ativo=result[5], senha=None)
                usuario.set_dark_theme(result[6])
                first_login = result[7]
                cursor.close()
                return usuario, first_login, None
            else:
                cursor.close()
                return None, None, None
        except Exception as e:
            print(e)
            return None, None, e

    def reset(self, email):
        try:
            usuario = []
            cursor = self.db.cursor()      
            cursor.execute('select id_usuario,nome, email, empresa, perfil, ativo, dark_theme from usuario where email=%s and ativo=True', (email,))
            result = cursor.fetchone()
            cursor.close()

            if result:
                usuario = UsuarioModel(id=result[0], nome=result[1], email=result[2], empresa=result[3], perfil=result[4], ativo=result[5], senha=None)
            return usuario, None
        except Exception as e:
            print(e)
            return None, e
    
    def update_password(self, email, password):
        try:
            cursor = self.db.cursor()      
            cursor.execute('update usuario set senha=%s, first_login=false where email=%s', (password, email))
            self.db.commit()            
            cursor.close()
            return 'Senha do usuário atualizada com sucesso', None
        except Exception as e:
            print(e)
            return 'Senha do usuário não atualizada', e  
    
    def insert(self, user: UsuarioModel):
        try:
            cursor = self.db.cursor()
            cursor.execute('select id_usuario from usuario where email=%s', (user.email,))
            result = cursor.fetchone()

            if result:
                cursor.close()
                return 'Email já cadastrado', None
            else:
                cursor.execute('insert into usuario(nome,email,senha,empresa,perfil) values (%s,%s,%s,%s,%s)',(user.nome, user.email, user.senha, user.empresa, user.perfil))
                self.db.commit()            
                cursor.close()
                return None, None

        except Exception as e:
            print('erro')
            print(e)
            return None, e
        
    def update(self, user: UsuarioModel):
        try:
            cursor = self.db.cursor()
            cursor.execute('update usuario set nome=%s, email=%s, empresa=%s, perfil=%s, ativo=%s where id_usuario=%s and nome!="admin"',(user.nome, user.email, user.empresa, user.perfil, user.ativo, user.id))
            self.db.commit()            
            cursor.close()
            return None
        except Exception as e:            
            print(e)
            return e
    
    def get_all(self):
        try:
            cursor = self.db.cursor()
            cursor.execute('select id_usuario,nome,email,empresa,perfil,ativo from usuario order by nome')
            result = cursor.fetchall()
            usuarios = []
            for u in result:
                user = UsuarioModel(id=u[0], nome=u[1], email=u[2], empresa=u[3], perfil=u[4], ativo=u[5], senha=None)
                usuarios.append(user)
            cursor.close()
            return usuarios

        except Exception as e:
            print(e)
            return None
        
    def update_theme(self, theme):
        try:
            cursor = self.db.cursor()
            cursor.execute('update usuario set dark_theme=%s where id_usuario=%s', (theme, session['id']))
            self.db.commit()            
            cursor.close()
            return None
        except Exception as e:
            print(e)
            return e
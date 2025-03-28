#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from datetime import datetime

class DatabaseManager:
    """Classe responsável por gerenciar a conexão com o banco de dados"""
    
    def __init__(self, db_path):
        """Inicializa o gerenciador de banco de dados"""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """Estabelece a conexão com o banco de dados"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Para acessar colunas pelo nome
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return False
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
    
    def commit(self):
        """Comita as alterações no banco de dados"""
        if self.connection:
            self.connection.commit()
    
    def execute(self, query, params=None):
        """Executa uma query SQL"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor
        except sqlite3.Error as e:
            print(f"Erro ao executar query: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return None
    
    def executemany(self, query, params_list):
        """Executa uma query SQL múltiplas vezes com diferentes parâmetros"""
        try:
            self.cursor.executemany(query, params_list)
            return self.cursor
        except sqlite3.Error as e:
            print(f"Erro ao executar query múltipla: {e}")
            return None
    
    def setup_database(self):
        """Configura o banco de dados com o schema inicial"""
        # Lê o arquivo de schema principal
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
            
            # Executa o schema principal
            self.cursor.executescript(schema)
            self.connection.commit()
            print("Schema principal configurado com sucesso.")
            
            # Configura o schema de usuários
            self.setup_usuarios_schema()
            
            # Verifica se precisa criar dados de exemplo
            count = self.execute("SELECT COUNT(*) FROM territorios").fetchone()[0]
            if count == 0:
                self._criar_dados_exemplo()
            
            # Cria um usuário administrador padrão se não existir
            count = self.execute("SELECT COUNT(*) FROM usuarios").fetchone()
            if count and count[0] == 0:
                self._criar_usuario_admin()
            
            return True
        except Exception as e:
            print(f"Erro ao configurar banco de dados: {e}")
            return False
    
    def setup_usuarios_schema(self):
        """Configura o schema para usuários, logs e notificações"""
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema_usuarios.sql')
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
            
            # Executa o schema de usuários
            self.cursor.executescript(schema)
            self.connection.commit()
            print("Schema de usuários configurado com sucesso.")
            return True
        except Exception as e:
            print(f"Erro ao configurar schema de usuários: {e}")
            return False
    
    def _criar_usuario_admin(self):
        """Cria o usuário administrador padrão"""
        from models.usuario import Usuario
        
        print("Criando usuário administrador padrão...")
        
        admin = Usuario(
            nome="Administrador",
            email="admin@sistema.local",
            nivel_permissao=Usuario.NIVEL_ADMIN,
            ativo=True
        )
        # Senha padrão: "admin123" (deve ser alterada no primeiro acesso)
        admin.definir_senha("admin123")
        
        if admin.save(self):
            print("Usuário administrador criado com sucesso.")
        else:
            print("Erro ao criar usuário administrador.")
    
    def _criar_dados_exemplo(self):
        """Cria dados de exemplo para o banco de dados"""
        print("Criando dados de exemplo...")
        
        # Cria alguns territórios de exemplo
        self.execute(
            "INSERT INTO territorios (nome, descricao) VALUES (?, ?)",
            ("Território 1", "Quadra 10 - Setor Central")
        )
        territorio_id = self.cursor.lastrowid
        
        # Cria algumas ruas para o território
        self.execute(
            "INSERT INTO ruas (territorio_id, nome) VALUES (?, ?)",
            (territorio_id, "Rua das Flores")
        )
        rua_id = self.cursor.lastrowid
        
        # Cria alguns imóveis para a rua
        imoveis = [
            (rua_id, "123", "residencial", None, None),
            (rua_id, "125", "comercial", None, None),
            (rua_id, "127", "predio", "Edifício Central", 12),
            (rua_id, "129", "vila", "Vila Aurora", 8)
        ]
        self.executemany(
            "INSERT INTO imoveis (rua_id, numero, tipo, nome, total_unidades) VALUES (?, ?, ?, ?, ?)",
            imoveis
        )
        
        # Cria saídas de campo
        saidas = [
            ("Saída 1", datetime.now().strftime('%Y-%m-%d'), "Terça-feira", "09:00", "João"),
            ("Saída 2", datetime.now().strftime('%Y-%m-%d'), "Quarta-feira", "19:30", "Maria"),
            ("Saída 3", datetime.now().strftime('%Y-%m-%d'), "Sexta-feira", "14:00", "Pedro")
        ]
        self.executemany(
            "INSERT INTO saidas_campo (nome, data, dia_semana, horario, dirigente) VALUES (?, ?, ?, ?, ?)",
            saidas
        )
        
        self.connection.commit()
        print("Dados de exemplo criados com sucesso.")
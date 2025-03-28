#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional, Dict, Any
import sqlite3
import hashlib
import os

class Usuario:
    """Modelo para representar um usuário do sistema"""
    
    # Níveis de permissão
    NIVEL_ADMIN = 3     # Acesso total ao sistema
    NIVEL_GESTOR = 2    # Pode gerenciar territórios, designações, etc.
    NIVEL_BASICO = 1    # Apenas registra atendimentos e consulta dados
    
    def __init__(self, id: int = None, nome: str = "", email: str = "",
                 senha_hash: str = None, nivel_permissao: int = NIVEL_BASICO,
                 ativo: bool = True, data_criacao: str = None):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.nivel_permissao = nivel_permissao
        self.ativo = ativo
        self.data_criacao = data_criacao
    
    @staticmethod
    def from_db_row(row: sqlite3.Row) -> 'Usuario':
        """Cria um objeto Usuario a partir de uma linha do banco de dados"""
        return Usuario(
            id=row['id'],
            nome=row['nome'],
            email=row['email'],
            senha_hash=row['senha_hash'],
            nivel_permissao=row['nivel_permissao'],
            ativo=bool(row['ativo']),
            data_criacao=row['data_criacao']
        )
    
    @staticmethod
    def get_all(db_manager) -> List['Usuario']:
        """Obtém todos os usuários do banco de dados"""
        cursor = db_manager.execute("SELECT * FROM usuarios ORDER BY nome")
        if cursor:
            return [Usuario.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def get_ativos(db_manager) -> List['Usuario']:
        """Obtém todos os usuários ativos do banco de dados"""
        cursor = db_manager.execute("SELECT * FROM usuarios WHERE ativo = 1 ORDER BY nome")
        if cursor:
            return [Usuario.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def get_by_id(db_manager, usuario_id: int) -> Optional['Usuario']:
        """Obtém um usuário pelo ID"""
        cursor = db_manager.execute(
            "SELECT * FROM usuarios WHERE id = ?", 
            (usuario_id,)
        )
        if cursor:
            row = cursor.fetchone()
            if row:
                return Usuario.from_db_row(row)
        return None
    
    @staticmethod
    def get_by_email(db_manager, email: str) -> Optional['Usuario']:
        """Obtém um usuário pelo email"""
        cursor = db_manager.execute(
            "SELECT * FROM usuarios WHERE email = ?", 
            (email,)
        )
        if cursor:
            row = cursor.fetchone()
            if row:
                return Usuario.from_db_row(row)
        return None
    
    @staticmethod
    def verificar_credenciais(db_manager, email: str, senha: str) -> Optional['Usuario']:
        """Verifica as credenciais de um usuário"""
        usuario = Usuario.get_by_email(db_manager, email)
        if usuario and usuario.verificar_senha(senha) and usuario.ativo:
            return usuario
        return None
    
    def definir_senha(self, senha: str) -> None:
        """Define a senha do usuário (faz o hash)"""
        # Gera um salt aleatório
        salt = os.urandom(32)
        # Gera o hash com o salt
        senha_hash = hashlib.pbkdf2_hmac(
            'sha256',
            senha.encode('utf-8'),
            salt,
            100000
        )
        # Armazena salt+hash
        self.senha_hash = salt.hex() + ":" + senha_hash.hex()
    
    def verificar_senha(self, senha: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado"""
        if not self.senha_hash:
            return False
        
        try:
            salt_str, hash_str = self.senha_hash.split(":")
            salt = bytes.fromhex(salt_str)
            hash_stored = bytes.fromhex(hash_str)
            
            # Calcula o hash da senha fornecida com o mesmo salt
            hash_senha = hashlib.pbkdf2_hmac(
                'sha256',
                senha.encode('utf-8'),
                salt,
                100000
            )
            
            return hash_senha == hash_stored
        except Exception:
            return False
    
    def save(self, db_manager) -> bool:
        """Salva o usuário no banco de dados"""
        if self.id is None:
            # Verificar se o email já existe
            if Usuario.get_by_email(db_manager, self.email):
                return False
                
            # Inserir novo usuário
            cursor = db_manager.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, nivel_permissao, ativo) "
                "VALUES (?, ?, ?, ?, ?)",
                (self.nome, self.email, self.senha_hash, self.nivel_permissao, int(self.ativo))
            )
            if cursor:
                self.id = cursor.lastrowid
                db_manager.commit()
                return True
        else:
            # Atualizar usuário existente
            cursor = db_manager.execute(
                "UPDATE usuarios SET nome = ?, email = ?, senha_hash = ?, "
                "nivel_permissao = ?, ativo = ? WHERE id = ?",
                (self.nome, self.email, self.senha_hash, self.nivel_permissao, 
                 int(self.ativo), self.id)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def delete(self, db_manager) -> bool:
        """Deleta o usuário do banco de dados"""
        if self.id is not None:
            cursor = db_manager.execute(
                "DELETE FROM usuarios WHERE id = ?",
                (self.id,)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def __str__(self) -> str:
        return f"{self.nome} ({self.email})"


class LogAtividade:
    """Modelo para representar um registro de atividade no sistema"""
    
    # Tipos de ação
    ACAO_LOGIN = "login"
    ACAO_LOGOUT = "logout"
    ACAO_CRIAR = "criar"
    ACAO_EDITAR = "editar"
    ACAO_EXCLUIR = "excluir"
    ACAO_VISUALIZAR = "visualizar"
    
    def __init__(self, id: int = None, usuario_id: int = None, 
                 tipo_acao: str = "", descricao: str = "",
                 data_hora: str = None, entidade: str = None,
                 entidade_id: int = None):
        self.id = id
        self.usuario_id = usuario_id
        self.tipo_acao = tipo_acao
        self.descricao = descricao
        self.data_hora = data_hora
        self.entidade = entidade  # tipo de entidade (território, designação, etc.)
        self.entidade_id = entidade_id  # id da entidade, se aplicável
    
    @staticmethod
    def from_db_row(row: sqlite3.Row) -> 'LogAtividade':
        """Cria um objeto LogAtividade a partir de uma linha do banco de dados"""
        return LogAtividade(
            id=row['id'],
            usuario_id=row['usuario_id'],
            tipo_acao=row['tipo_acao'],
            descricao=row['descricao'],
            data_hora=row['data_hora'],
            entidade=row['entidade'],
            entidade_id=row['entidade_id']
        )
    
    @staticmethod
    def get_all(db_manager, limit: int = 100) -> List['LogAtividade']:
        """Obtém todos os registros de atividade do banco de dados"""
        cursor = db_manager.execute(
            "SELECT * FROM log_atividades ORDER BY data_hora DESC LIMIT ?",
            (limit,)
        )
        if cursor:
            return [LogAtividade.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def get_by_usuario(db_manager, usuario_id: int, limit: int = 50) -> List['LogAtividade']:
        """Obtém os registros de atividade de um usuário específico"""
        cursor = db_manager.execute(
            "SELECT * FROM log_atividades WHERE usuario_id = ? "
            "ORDER BY data_hora DESC LIMIT ?",
            (usuario_id, limit)
        )
        if cursor:
            return [LogAtividade.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def registrar(db_manager, usuario_id: int, tipo_acao: str, 
                 descricao: str, entidade: str = None, entidade_id: int = None) -> bool:
        """Registra uma nova atividade no sistema"""
        cursor = db_manager.execute(
            "INSERT INTO log_atividades (usuario_id, tipo_acao, descricao, entidade, entidade_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (usuario_id, tipo_acao, descricao, entidade, entidade_id)
        )
        if cursor:
            db_manager.commit()
            return True
        return False
    
    def __str__(self) -> str:
        return f"{self.tipo_acao.capitalize()}: {self.descricao}"


class Notificacao:
    """Modelo para representar uma notificação para um usuário"""
    
    # Tipos de notificação
    TIPO_INFO = "info"
    TIPO_ALERTA = "alerta"
    TIPO_ERRO = "erro"
    
    # Status da notificação
    STATUS_NAO_LIDA = "nao_lida"
    STATUS_LIDA = "lida"
    STATUS_ARQUIVADA = "arquivada"
    
    def __init__(self, id: int = None, usuario_id: int = None,
                 tipo: str = TIPO_INFO, titulo: str = "",
                 mensagem: str = "", status: str = STATUS_NAO_LIDA,
                 data_criacao: str = None, data_leitura: str = None,
                 link: str = None, entidade: str = None, 
                 entidade_id: int = None):
        self.id = id
        self.usuario_id = usuario_id
        self.tipo = tipo
        self.titulo = titulo
        self.mensagem = mensagem
        self.status = status
        self.data_criacao = data_criacao
        self.data_leitura = data_leitura
        self.link = link  # link/ação relacionada à notificação
        self.entidade = entidade  # tipo de entidade relacionada
        self.entidade_id = entidade_id  # id da entidade, se aplicável
    
    @staticmethod
    def from_db_row(row: sqlite3.Row) -> 'Notificacao':
        """Cria um objeto Notificacao a partir de uma linha do banco de dados"""
        return Notificacao(
            id=row['id'],
            usuario_id=row['usuario_id'],
            tipo=row['tipo'],
            titulo=row['titulo'],
            mensagem=row['mensagem'],
            status=row['status'],
            data_criacao=row['data_criacao'],
            data_leitura=row['data_leitura'],
            link=row['link'],
            entidade=row['entidade'],
            entidade_id=row['entidade_id']
        )
    
    @staticmethod
    def get_by_usuario(db_manager, usuario_id: int, apenas_nao_lidas: bool = False) -> List['Notificacao']:
        """Obtém as notificações de um usuário específico"""
        query = "SELECT * FROM notificacoes WHERE usuario_id = ?"
        params = [usuario_id]
        
        if apenas_nao_lidas:
            query += " AND status = ?"
            params.append(Notificacao.STATUS_NAO_LIDA)
        
        query += " ORDER BY data_criacao DESC"
        
        cursor = db_manager.execute(query, params)
        if cursor:
            return [Notificacao.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def criar(db_manager, usuario_id: int, tipo: str, titulo: str, 
              mensagem: str, link: str = None, entidade: str = None, 
              entidade_id: int = None) -> bool:
        """Cria uma nova notificação para um usuário"""
        cursor = db_manager.execute(
            "INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, status, link, entidade, entidade_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (usuario_id, tipo, titulo, mensagem, Notificacao.STATUS_NAO_LIDA, link, entidade, entidade_id)
        )
        if cursor:
            db_manager.commit()
            return True
        return False
    
    @staticmethod
    def criar_para_todos(db_manager, tipo: str, titulo: str, 
                        mensagem: str, link: str = None, entidade: str = None, 
                        entidade_id: int = None) -> bool:
        """Cria uma notificação para todos os usuários ativos"""
        # Obtém todos os usuários ativos
        usuarios = Usuario.get_ativos(db_manager)
        if not usuarios:
            return False
        
        # Cria a notificação para cada usuário
        for usuario in usuarios:
            Notificacao.criar(
                db_manager, usuario.id, tipo, titulo, mensagem, 
                link, entidade, entidade_id
            )
        
        return True
    
    def marcar_como_lida(self, db_manager) -> bool:
        """Marca a notificação como lida"""
        if self.id is not None and self.status == Notificacao.STATUS_NAO_LIDA:
            cursor = db_manager.execute(
                "UPDATE notificacoes SET status = ?, data_leitura = CURRENT_TIMESTAMP "
                "WHERE id = ?",
                (Notificacao.STATUS_LIDA, self.id)
            )
            if cursor:
                self.status = Notificacao.STATUS_LIDA
                db_manager.commit()
                return True
        return False
    
    def arquivar(self, db_manager) -> bool:
        """Arquiva a notificação"""
        if self.id is not None:
            cursor = db_manager.execute(
                "UPDATE notificacoes SET status = ? WHERE id = ?",
                (Notificacao.STATUS_ARQUIVADA, self.id)
            )
            if cursor:
                self.status = Notificacao.STATUS_ARQUIVADA
                db_manager.commit()
                return True
        return False
    
    def __str__(self) -> str:
        return f"{self.titulo}: {self.mensagem}"
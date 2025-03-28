#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional, Dict, Any
import sqlite3

class Territorio:
    """Modelo para representar um território"""
    
    def __init__(self, id: int = None, nome: str = "", descricao: str = "", 
                 ultima_visita: str = None, data_criacao: str = None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.ultima_visita = ultima_visita
        self.data_criacao = data_criacao
        self.ruas = []
    
    @staticmethod
    def from_db_row(row: sqlite3.Row) -> 'Territorio':
        """Cria um objeto Territorio a partir de uma linha do banco de dados"""
        return Territorio(
            id=row['id'],
            nome=row['nome'],
            descricao=row['descricao'],
            ultima_visita=row['ultima_visita'],
            data_criacao=row['data_criacao']
        )
    
    @staticmethod
    def get_all(db_manager) -> List['Territorio']:
        """Obtém todos os territórios do banco de dados"""
        cursor = db_manager.execute("SELECT * FROM territorios ORDER BY nome")
        if cursor:
            return [Territorio.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def get_by_id(db_manager, territorio_id: int) -> Optional['Territorio']:
        """Obtém um território pelo ID"""
        cursor = db_manager.execute(
            "SELECT * FROM territorios WHERE id = ?", 
            (territorio_id,)
        )
        if cursor:
            row = cursor.fetchone()
            if row:
                return Territorio.from_db_row(row)
        return None
    
    def save(self, db_manager) -> bool:
        """Salva o território no banco de dados"""
        if self.id is None:
            # Inserir novo território
            cursor = db_manager.execute(
                "INSERT INTO territorios (nome, descricao, ultima_visita) VALUES (?, ?, ?)",
                (self.nome, self.descricao, self.ultima_visita)
            )
            if cursor:
                self.id = cursor.lastrowid
                db_manager.commit()
                return True
        else:
            # Atualizar território existente
            cursor = db_manager.execute(
                "UPDATE territorios SET nome = ?, descricao = ?, ultima_visita = ? WHERE id = ?",
                (self.nome, self.descricao, self.ultima_visita, self.id)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def delete(self, db_manager) -> bool:
        """Deleta o território do banco de dados"""
        if self.id is not None:
            cursor = db_manager.execute(
                "DELETE FROM territorios WHERE id = ?",
                (self.id,)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def get_ruas(self, db_manager) -> List[Dict[str, Any]]:
        """Obtém todas as ruas do território"""
        if self.id is not None:
            cursor = db_manager.execute(
                "SELECT * FROM ruas WHERE territorio_id = ? ORDER BY nome",
                (self.id,)
            )
            if cursor:
                return [dict(row) for row in cursor.fetchall()]
        return []
    
    def add_rua(self, db_manager, nome_rua: str) -> bool:
        """Adiciona uma nova rua ao território"""
        if self.id is not None:
            cursor = db_manager.execute(
                "INSERT INTO ruas (territorio_id, nome) VALUES (?, ?)",
                (self.id, nome_rua)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def __str__(self) -> str:
        return self.nome
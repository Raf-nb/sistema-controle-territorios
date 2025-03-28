#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional, Dict, Any
import sqlite3
from datetime import datetime

class SaidaCampo:
    """Modelo para representar uma saída de campo"""
    
    def __init__(self, id: int = None, nome: str = "", data: str = "", 
                 dia_semana: str = "", horario: str = "", dirigente: str = None,
                 data_criacao: str = None):
        self.id = id
        self.nome = nome
        self.data = data
        self.dia_semana = dia_semana
        self.horario = horario
        self.dirigente = dirigente
        self.data_criacao = data_criacao
    
    @staticmethod
    def from_db_row(row: sqlite3.Row) -> 'SaidaCampo':
        """Cria um objeto SaidaCampo a partir de uma linha do banco de dados"""
        return SaidaCampo(
            id=row['id'],
            nome=row['nome'],
            data=row['data'],
            dia_semana=row['dia_semana'],
            horario=row['horario'],
            dirigente=row['dirigente'],
            data_criacao=row['data_criacao']
        )
    
    @staticmethod
    def get_all(db_manager) -> List['SaidaCampo']:
        """Obtém todas as saídas de campo do banco de dados"""
        cursor = db_manager.execute("SELECT * FROM saidas_campo ORDER BY data DESC")
        if cursor:
            return [SaidaCampo.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def get_proximas(db_manager, limit: int = 5) -> List['SaidaCampo']:
        """Obtém as próximas saídas de campo"""
        hoje = datetime.now().strftime('%Y-%m-%d')
        cursor = db_manager.execute(
            "SELECT * FROM saidas_campo WHERE data >= ? ORDER BY data LIMIT ?",
            (hoje, limit)
        )
        if cursor:
            return [SaidaCampo.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def get_by_id(db_manager, saida_id: int) -> Optional['SaidaCampo']:
        """Obtém uma saída de campo pelo ID"""
        cursor = db_manager.execute(
            "SELECT * FROM saidas_campo WHERE id = ?", 
            (saida_id,)
        )
        if cursor:
            row = cursor.fetchone()
            if row:
                return SaidaCampo.from_db_row(row)
        return None
    
    def save(self, db_manager) -> bool:
        """Salva a saída de campo no banco de dados"""
        if self.id is None:
            # Inserir nova saída de campo
            cursor = db_manager.execute(
                "INSERT INTO saidas_campo (nome, data, dia_semana, horario, dirigente) VALUES (?, ?, ?, ?, ?)",
                (self.nome, self.data, self.dia_semana, self.horario, self.dirigente)
            )
            if cursor:
                self.id = cursor.lastrowid
                db_manager.commit()
                return True
        else:
            # Atualizar saída de campo existente
            cursor = db_manager.execute(
                "UPDATE saidas_campo SET nome = ?, data = ?, dia_semana = ?, horario = ?, dirigente = ? WHERE id = ?",
                (self.nome, self.data, self.dia_semana, self.horario, self.dirigente, self.id)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def delete(self, db_manager) -> bool:
        """Deleta a saída de campo do banco de dados"""
        if self.id is not None:
            cursor = db_manager.execute(
                "DELETE FROM saidas_campo WHERE id = ?",
                (self.id,)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def __str__(self) -> str:
        return f"{self.nome} - {self.data}"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional, Dict, Any
import sqlite3
from datetime import datetime

class Designacao:
    """Modelo para representar uma designação de território"""
    
    def __init__(self, id: int = None, territorio_id: int = None, 
                 saida_campo_id: int = None, data_designacao: str = "",
                 data_devolucao: str = None, responsavel: str = None,
                 status: str = "ativo"):
        self.id = id
        self.territorio_id = territorio_id
        self.saida_campo_id = saida_campo_id
        self.data_designacao = data_designacao
        self.data_devolucao = data_devolucao
        self.responsavel = responsavel
        self.status = status  # 'ativo', 'concluido'
        
        # Campos extras para exibição
        self.territorio_nome = None
        self.saida_campo_nome = None
    
    @staticmethod
    def from_db_row(row: sqlite3.Row) -> 'Designacao':
        """Cria um objeto Designacao a partir de uma linha do banco de dados"""
        designacao = Designacao(
            id=row['id'],
            territorio_id=row['territorio_id'],
            saida_campo_id=row['saida_campo_id'],
            data_designacao=row['data_designacao'],
            data_devolucao=row['data_devolucao'],
            responsavel=row['responsavel'],
            status=row['status']
        )
        
        # Adiciona campos extras se estiverem disponíveis
        if 'territorio_nome' in row.keys():
            designacao.territorio_nome = row['territorio_nome']
        if 'saida_campo_nome' in row.keys():
            designacao.saida_campo_nome = row['saida_campo_nome']
            
        return designacao
    
    @staticmethod
    def get_all(db_manager) -> List['Designacao']:
        """Obtém todas as designações do banco de dados"""
        cursor = db_manager.execute(
            "SELECT d.*, t.nome as territorio_nome, s.nome as saida_campo_nome "
            "FROM designacoes d "
            "JOIN territorios t ON d.territorio_id = t.id "
            "JOIN saidas_campo s ON d.saida_campo_id = s.id "
            "ORDER BY d.data_designacao DESC"
        )
        if cursor:
            return [Designacao.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def get_ativas(db_manager) -> List['Designacao']:
        """Obtém as designações ativas"""
        cursor = db_manager.execute(
            "SELECT d.*, t.nome as territorio_nome, s.nome as saida_campo_nome "
            "FROM designacoes d "
            "JOIN territorios t ON d.territorio_id = t.id "
            "JOIN saidas_campo s ON d.saida_campo_id = s.id "
            "WHERE d.status = 'ativo' "
            "ORDER BY d.data_designacao DESC"
        )
        if cursor:
            return [Designacao.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def get_by_id(db_manager, designacao_id: int) -> Optional['Designacao']:
        """Obtém uma designação pelo ID"""
        cursor = db_manager.execute(
            "SELECT d.*, t.nome as territorio_nome, s.nome as saida_campo_nome "
            "FROM designacoes d "
            "JOIN territorios t ON d.territorio_id = t.id "
            "JOIN saidas_campo s ON d.saida_campo_id = s.id "
            "WHERE d.id = ?", 
            (designacao_id,)
        )
        if cursor:
            row = cursor.fetchone()
            if row:
                return Designacao.from_db_row(row)
        return None
    
    @staticmethod
    def get_by_territorio(db_manager, territorio_id: int) -> List['Designacao']:
        """Obtém todas as designações de um território"""
        cursor = db_manager.execute(
            "SELECT d.*, t.nome as territorio_nome, s.nome as saida_campo_nome "
            "FROM designacoes d "
            "JOIN territorios t ON d.territorio_id = t.id "
            "JOIN saidas_campo s ON d.saida_campo_id = s.id "
            "WHERE d.territorio_id = ? "
            "ORDER BY d.data_designacao DESC",
            (territorio_id,)
        )
        if cursor:
            return [Designacao.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def get_designacao_do_dia(db_manager) -> Optional['Designacao']:
        """Obtém a designação para o dia atual"""
        hoje = datetime.now().strftime('%Y-%m-%d')
        cursor = db_manager.execute(
            "SELECT d.*, t.nome as territorio_nome, s.nome as saida_campo_nome "
            "FROM designacoes d "
            "JOIN territorios t ON d.territorio_id = t.id "
            "JOIN saidas_campo s ON d.saida_campo_id = s.id "
            "WHERE d.data_designacao <= ? AND (d.data_devolucao >= ? OR d.data_devolucao IS NULL) "
            "AND d.status = 'ativo' "
            "ORDER BY d.data_designacao DESC "
            "LIMIT 1",
            (hoje, hoje)
        )
        if cursor:
            row = cursor.fetchone()
            if row:
                return Designacao.from_db_row(row)
        return None
    
    def save(self, db_manager) -> bool:
        """Salva a designação no banco de dados"""
        if self.id is None:
            # Inserir nova designação
            cursor = db_manager.execute(
                "INSERT INTO designacoes (territorio_id, saida_campo_id, data_designacao, "
                "data_devolucao, responsavel, status) VALUES (?, ?, ?, ?, ?, ?)",
                (self.territorio_id, self.saida_campo_id, self.data_designacao,
                 self.data_devolucao, self.responsavel, self.status)
            )
            if cursor:
                self.id = cursor.lastrowid
                db_manager.commit()
                return True
        else:
            # Atualizar designação existente
            cursor = db_manager.execute(
                "UPDATE designacoes SET territorio_id = ?, saida_campo_id = ?, "
                "data_designacao = ?, data_devolucao = ?, responsavel = ?, status = ? "
                "WHERE id = ?",
                (self.territorio_id, self.saida_campo_id, self.data_designacao,
                 self.data_devolucao, self.responsavel, self.status, self.id)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def concluir(self, db_manager) -> bool:
        """Marca a designação como concluída"""
        if self.id is not None:
            self.status = "concluido"
            cursor = db_manager.execute(
                "UPDATE designacoes SET status = 'concluido' WHERE id = ?",
                (self.id,)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def delete(self, db_manager) -> bool:
        """Deleta a designação do banco de dados"""
        if self.id is not None:
            cursor = db_manager.execute(
                "DELETE FROM designacoes WHERE id = ?",
                (self.id,)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def __str__(self) -> str:
        return f"Designação {self.id}: {self.territorio_nome or f'Território {self.territorio_id}'}"


class DesignacaoPredioVila:
    """Modelo para representar uma designação específica de prédio/vila"""
    
    def __init__(self, id: int = None, imovel_id: int = None,
                 responsavel: str = "", saida_campo_id: int = None,
                 data_designacao: str = "", data_devolucao: str = None,
                 status: str = "ativo"):
        self.id = id
        self.imovel_id = imovel_id
        self.responsavel = responsavel
        self.saida_campo_id = saida_campo_id
        self.data_designacao = data_designacao
        self.data_devolucao = data_devolucao
        self.status = status  # 'ativo', 'concluido'
        
        # Campos extras para exibição
        self.imovel_numero = None
        self.imovel_nome = None
        self.imovel_tipo = None
        self.saida_campo_nome = None
        self.rua_nome = None
        self.territorio_nome = None
    
    @staticmethod
    def from_db_row(row: sqlite3.Row) -> 'DesignacaoPredioVila':
        """Cria um objeto DesignacaoPredioVila a partir de uma linha do banco de dados"""
        designacao = DesignacaoPredioVila(
            id=row['id'],
            imovel_id=row['imovel_id'],
            responsavel=row['responsavel'],
            saida_campo_id=row['saida_campo_id'],
            data_designacao=row['data_designacao'],
            data_devolucao=row['data_devolucao'],
            status=row['status']
        )
        
        # Adiciona campos extras se estiverem disponíveis
        for campo in ['imovel_numero', 'imovel_nome', 'imovel_tipo', 'saida_campo_nome', 
                      'rua_nome', 'territorio_nome']:
            if campo in row.keys():
                setattr(designacao, campo, row[campo])
            
        return designacao
    
    @staticmethod
    def get_all(db_manager) -> List['DesignacaoPredioVila']:
        """Obtém todas as designações de prédios/vilas do banco de dados"""
        cursor = db_manager.execute(
            "SELECT d.*, i.numero as imovel_numero, i.nome as imovel_nome, i.tipo as imovel_tipo, "
            "s.nome as saida_campo_nome, r.nome as rua_nome, t.nome as territorio_nome "
            "FROM designacoes_predios_vilas d "
            "JOIN imoveis i ON d.imovel_id = i.id "
            "JOIN saidas_campo s ON d.saida_campo_id = s.id "
            "JOIN ruas r ON i.rua_id = r.id "
            "JOIN territorios t ON r.territorio_id = t.id "
            "ORDER BY d.data_designacao DESC"
        )
        if cursor:
            return [DesignacaoPredioVila.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def get_ativas(db_manager) -> List['DesignacaoPredioVila']:
        """Obtém as designações ativas de prédios/vilas"""
        cursor = db_manager.execute(
            "SELECT d.*, i.numero as imovel_numero, i.nome as imovel_nome, i.tipo as imovel_tipo, "
            "s.nome as saida_campo_nome, r.nome as rua_nome, t.nome as territorio_nome "
            "FROM designacoes_predios_vilas d "
            "JOIN imoveis i ON d.imovel_id = i.id "
            "JOIN saidas_campo s ON d.saida_campo_id = s.id "
            "JOIN ruas r ON i.rua_id = r.id "
            "JOIN territorios t ON r.territorio_id = t.id "
            "WHERE d.status = 'ativo' "
            "ORDER BY d.data_designacao DESC"
        )
        if cursor:
            return [DesignacaoPredioVila.from_db_row(row) for row in cursor.fetchall()]
        return []
    
    @staticmethod
    def get_by_imovel(db_manager, imovel_id: int) -> Optional['DesignacaoPredioVila']:
        """Obtém a designação ativa de um prédio/vila específico"""
        cursor = db_manager.execute(
            "SELECT d.*, i.numero as imovel_numero, i.nome as imovel_nome, i.tipo as imovel_tipo, "
            "s.nome as saida_campo_nome, r.nome as rua_nome, t.nome as territorio_nome "
            "FROM designacoes_predios_vilas d "
            "JOIN imoveis i ON d.imovel_id = i.id "
            "JOIN saidas_campo s ON d.saida_campo_id = s.id "
            "JOIN ruas r ON i.rua_id = r.id "
            "JOIN territorios t ON r.territorio_id = t.id "
            "WHERE d.imovel_id = ? AND d.status = 'ativo'",
            (imovel_id,)
        )
        if cursor:
            row = cursor.fetchone()
            if row:
                return DesignacaoPredioVila.from_db_row(row)
        return None
    
    def save(self, db_manager) -> bool:
        """Salva a designação no banco de dados"""
        if self.id is None:
            # Inserir nova designação
            cursor = db_manager.execute(
                "INSERT INTO designacoes_predios_vilas (imovel_id, responsavel, saida_campo_id, "
                "data_designacao, data_devolucao, status) VALUES (?, ?, ?, ?, ?, ?)",
                (self.imovel_id, self.responsavel, self.saida_campo_id, 
                 self.data_designacao, self.data_devolucao, self.status)
            )
            if cursor:
                self.id = cursor.lastrowid
                db_manager.commit()
                return True
        else:
            # Atualizar designação existente
            cursor = db_manager.execute(
                "UPDATE designacoes_predios_vilas SET imovel_id = ?, responsavel = ?, "
                "saida_campo_id = ?, data_designacao = ?, data_devolucao = ?, status = ? "
                "WHERE id = ?",
                (self.imovel_id, self.responsavel, self.saida_campo_id,
                 self.data_designacao, self.data_devolucao, self.status, self.id)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def concluir(self, db_manager) -> bool:
        """Marca a designação como concluída"""
        if self.id is not None:
            self.status = "concluido"
            cursor = db_manager.execute(
                "UPDATE designacoes_predios_vilas SET status = 'concluido' WHERE id = ?",
                (self.id,)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def delete(self, db_manager) -> bool:
        """Deleta a designação do banco de dados"""
        if self.id is not None:
            cursor = db_manager.execute(
                "DELETE FROM designacoes_predios_vilas WHERE id = ?",
                (self.id,)
            )
            if cursor:
                db_manager.commit()
                return True
        return False
    
    def __str__(self) -> str:
        nome_imovel = self.imovel_nome if self.imovel_nome else f"Nº {self.imovel_numero}"
        return f"Designação: {nome_imovel} ({self.imovel_tipo.capitalize()})"
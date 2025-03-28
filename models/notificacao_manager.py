#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from models.usuario import Notificacao, Usuario
from models.designacao import Designacao, DesignacaoPredioVila

class NotificacaoManager:
    """Classe para gerenciar a geração de notificações"""
    
    @staticmethod
    def verificar_designacoes_proximas_vencimento(db_manager):
        """Verifica designações próximas do vencimento e gera notificações"""
        hoje = datetime.now().date()
        limite = hoje + timedelta(days=5)  # Alerta para 5 dias antes
        
        # Formatar datas para comparação no SQLite
        hoje_str = hoje.strftime('%Y-%m-%d')
        limite_str = limite.strftime('%Y-%m-%d')
        
        # Buscar designações próximas do vencimento
        cursor = db_manager.execute(
            "SELECT d.*, t.nome as territorio_nome FROM designacoes d "
            "JOIN territorios t ON d.territorio_id = t.id "
            "WHERE d.status = 'ativo' AND d.data_devolucao BETWEEN ? AND ? "
            "ORDER BY d.data_devolucao",
            (hoje_str, limite_str)
        )
        
        if cursor:
            designacoes = cursor.fetchall()
            
            # Buscar usuários gestores e administradores
            usuarios = [u for u in Usuario.get_ativos(db_manager) 
                       if u.nivel_permissao >= Usuario.NIVEL_GESTOR]
            
            # Gerar notificações para cada designação
            for designacao in designacoes:
                dias_restantes = (datetime.strptime(designacao['data_devolucao'], '%Y-%m-%d').date() - hoje).days
                
                titulo = f"Designação próxima do vencimento: {designacao['territorio_nome']}"
                mensagem = (f"A designação do território '{designacao['territorio_nome']}' "
                          f"vence em {dias_restantes} dias ({designacao['data_devolucao']}).")
                
                # Notificar todos os gestores e administradores
                for usuario in usuarios:
                    # Verificar se já existe notificação similar não lida
                    cursor = db_manager.execute(
                        "SELECT id FROM notificacoes "
                        "WHERE usuario_id = ? AND entidade = 'designacao' AND entidade_id = ? "
                        "AND status = ? AND tipo = ?",
                        (usuario.id, designacao['id'], Notificacao.STATUS_NAO_LIDA, Notificacao.TIPO_ALERTA)
                    )
                    
                    if cursor and not cursor.fetchone():
                        # Criar notificação
                        Notificacao.criar(
                            db_manager,
                            usuario.id,
                            Notificacao.TIPO_ALERTA,
                            titulo,
                            mensagem,
                            None,  # link
                            "designacao",
                            designacao['id']
                        )
    
    @staticmethod
    def verificar_predios_vilas_proximos_vencimento(db_manager):
        """Verifica designações de prédios/vilas próximas do vencimento"""
        hoje = datetime.now().date()
        limite = hoje + timedelta(days=5)  # Alerta para 5 dias antes
        
        # Formatar datas para comparação no SQLite
        hoje_str = hoje.strftime('%Y-%m-%d')
        limite_str = limite.strftime('%Y-%m-%d')
        
        # Buscar designações próximas do vencimento
        cursor = db_manager.execute(
            "SELECT d.*, i.nome as imovel_nome, i.numero, i.tipo "
            "FROM designacoes_predios_vilas d "
            "JOIN imoveis i ON d.imovel_id = i.id "
            "WHERE d.status = 'ativo' AND d.data_devolucao BETWEEN ? AND ? "
            "ORDER BY d.data_devolucao",
            (hoje_str, limite_str)
        )
        
        if cursor:
            designacoes = cursor.fetchall()
            
            # Buscar usuários gestores e administradores
            usuarios = [u for u in Usuario.get_ativos(db_manager) 
                       if u.nivel_permissao >= Usuario.NIVEL_GESTOR]
            
            # Gerar notificações para cada designação
            for designacao in designacoes:
                dias_restantes = (datetime.strptime(designacao['data_devolucao'], '%Y-%m-%d').date() - hoje).days
                
                nome_imovel = designacao['imovel_nome'] or f"Nº {designacao['numero']}"
                tipo_imovel = designacao['tipo'].capitalize()
                
                titulo = f"Designação próxima do vencimento: {nome_imovel}"
                mensagem = (f"A designação do {tipo_imovel} '{nome_imovel}' "
                          f"vence em {dias_restantes} dias ({designacao['data_devolucao']}).")
                
                # Notificar todos os gestores e administradores
                for usuario in usuarios:
                    # Verificar se já existe notificação similar não lida
                    cursor = db_manager.execute(
                        "SELECT id FROM notificacoes "
                        "WHERE usuario_id = ? AND entidade = 'designacao_predios_vilas' AND entidade_id = ? "
                        "AND status = ? AND tipo = ?",
                        (usuario.id, designacao['id'], Notificacao.STATUS_NAO_LIDA, Notificacao.TIPO_ALERTA)
                    )
                    
                    if cursor and not cursor.fetchone():
                        # Criar notificação
                        Notificacao.criar(
                            db_manager,
                            usuario.id,
                            Notificacao.TIPO_ALERTA,
                            titulo,
                            mensagem,
                            None,  # link
                            "designacao_predios_vilas",
                            designacao['id']
                        )
    
    @staticmethod
    def verificar_todas_notificacoes(db_manager):
        """Verifica todas as condições que podem gerar notificações"""
        NotificacaoManager.verificar_designacoes_proximas_vencimento(db_manager)
        NotificacaoManager.verificar_predios_vilas_proximos_vencimento(db_manager)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QProgressBar, QGridLayout, QScrollArea,
                             QSizePolicy, QFrame)
from PySide6.QtCore import Qt, Signal, Slot, QDate
from PySide6.QtGui import QColor, QIcon, QFont

from datetime import datetime
import random  # Apenas para dados de amostra, remover na implementação final

from models.territorio import Territorio
from models.designacao import Designacao
from models.saida_campo import SaidaCampo
from models.atendimento import Atendimento

class DashboardWidget(QWidget):
    """Widget para a tela de dashboard"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.update_data()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        main_layout = QVBoxLayout(self)
        
        # Título do Dashboard
        title_label = QLabel("Dashboard")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Scroll Area para conteúdo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        # Widget para conteúdo scrollável
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # === Seção 1: Cards com estatísticas rápidas ===
        stats_layout = QHBoxLayout()
        content_layout.addLayout(stats_layout)
        
        # Card: Total de Territórios
        self.territorios_card = self.create_stat_card(
            "Total de Territórios", 
            "0", 
            "background-color: #e6f2ff; border-radius: 8px;"
        )
        stats_layout.addWidget(self.territorios_card)
        
        # Card: Imóveis Atendidos
        self.imoveis_card = self.create_stat_card(
            "Imóveis Atendidos", 
            "0/0", 
            "background-color: #e6fff2; border-radius: 8px;"
        )
        stats_layout.addWidget(self.imoveis_card)
        
        # Card: Designações Ativas
        self.designacoes_card = self.create_stat_card(
            "Designações Ativas", 
            "0", 
            "background-color: #fffbe6; border-radius: 8px;"
        )
        stats_layout.addWidget(self.designacoes_card)
        
        # === Seção 2: Território designado para hoje e próximas designações ===
        row2_layout = QHBoxLayout()
        content_layout.addLayout(row2_layout)
        
        # Território designado para hoje
        self.territorio_hoje_group = QGroupBox("Território do Dia")
        self.territorio_hoje_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.territorio_hoje_layout = QVBoxLayout(self.territorio_hoje_group)
        
        self.territorio_hoje_label = QLabel("Nenhum território designado para hoje")
        self.territorio_hoje_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.territorio_hoje_label.setStyleSheet("padding: 20px;")
        self.territorio_hoje_layout.addWidget(self.territorio_hoje_label)
        
        self.territorio_detalhes_layout = QGridLayout()
        self.territorio_hoje_layout.addLayout(self.territorio_detalhes_layout)
        self.territorio_hoje_layout.addStretch()
        
        row2_layout.addWidget(self.territorio_hoje_group, 2)
        
        # Próximas designações
        self.proximas_designacoes_group = QGroupBox("Próximas Designações")
        self.proximas_designacoes_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.proximas_designacoes_layout = QVBoxLayout(self.proximas_designacoes_group)
        
        self.designacoes_table = QTableWidget(0, 4)
        self.designacoes_table.setHorizontalHeaderLabels(["Território", "Saída", "Designação", "Status"])
        self.designacoes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.designacoes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.designacoes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.proximas_designacoes_layout.addWidget(self.designacoes_table)
        
        row2_layout.addWidget(self.proximas_designacoes_group, 3)
        
        # === Seção 3: Próximas saídas de campo ===
        row3_layout = QHBoxLayout()
        content_layout.addLayout(row3_layout)
        
        # Próximas saídas de campo
        self.proximas_saidas_group = QGroupBox("Próximas Saídas de Campo")
        self.proximas_saidas_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.proximas_saidas_layout = QVBoxLayout(self.proximas_saidas_group)
        
        self.saidas_table = QTableWidget(0, 4)
        self.saidas_table.setHorizontalHeaderLabels(["Nome", "Data", "Dia", "Horário"])
        self.saidas_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.saidas_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.saidas_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.proximas_saidas_layout.addWidget(self.saidas_table)
        
        row3_layout.addWidget(self.proximas_saidas_group)
        
        # === Seção 4: Lembretes e Avisos ===
        self.lembretes_group = QGroupBox("Lembretes e Avisos")
        self.lembretes_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.lembretes_layout = QVBoxLayout(self.lembretes_group)
        
        # Adicionaria aqui um widget para lembretes, usando QListWidget
        self.lembretes_label = QLabel("Não há lembretes ativos.")
        self.lembretes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lembretes_layout.addWidget(self.lembretes_label)
        
        content_layout.addWidget(self.lembretes_group)
        
        content_layout.addStretch()
    
    def create_stat_card(self, title, value, style):
        """Cria um card para estatísticas"""
        card = QGroupBox()
        card.setStyleSheet(style)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold;")
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("font-size: 24px; margin: 10px 0;")
        
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setTextVisible(False)
        progress.setFixedHeight(8)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(progress)
        
        # Armazenar referências para atualização
        card.value_label = value_label
        card.progress = progress
        
        return card
    
    def update_data(self):
        """Atualiza os dados exibidos no dashboard"""
        # Estatísticas rápidas
        self.update_estatisticas()
        
        # Território designado para hoje
        self.update_territorio_hoje()
        
        # Próximas designações
        self.update_proximas_designacoes()
        
        # Próximas saídas de campo
        self.update_proximas_saidas()
    
    def update_estatisticas(self):
        """Atualiza os cards de estatísticas"""
        # Total de territórios
        territorios = Territorio.get_all(self.db_manager)
        self.territorios_card.value_label.setText(str(len(territorios)))
        self.territorios_card.progress.setValue(100)
        
        # Imóveis atendidos
        cursor = self.db_manager.execute(
            "SELECT COUNT(*) as total FROM imoveis WHERE tipo IN ('residencial', 'comercial')"
        )
        total_imoveis = cursor.fetchone()['total'] if cursor else 0
        
        cursor = self.db_manager.execute(
            "SELECT COUNT(DISTINCT imovel_id) as atendidos FROM atendimentos "
            "JOIN imoveis ON atendimentos.imovel_id = imoveis.id "
            "WHERE imoveis.tipo IN ('residencial', 'comercial')"
        )
        imoveis_atendidos = cursor.fetchone()['atendidos'] if cursor else 0
        
        self.imoveis_card.value_label.setText(f"{imoveis_atendidos}/{total_imoveis}")
        if total_imoveis > 0:
            percent = int((imoveis_atendidos / total_imoveis) * 100)
            self.imoveis_card.progress.setValue(percent)
        
        # Designações ativas
        designacoes = Designacao.get_ativas(self.db_manager)
        self.designacoes_card.value_label.setText(str(len(designacoes)))
        # O progresso poderia ser baseado em alguma métrica como % de territórios designados
        self.designacoes_card.progress.setValue(random.randint(50, 90))  # Exemplo
    
    def update_territorio_hoje(self):
        """Atualiza o card do território designado para hoje"""
        designacao = Designacao.get_designacao_do_dia(self.db_manager)
        
        # Limpar layout de detalhes atual
        while self.territorio_detalhes_layout.count():
            item = self.territorio_detalhes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if designacao:
            self.territorio_hoje_label.setText(f"<h2>{designacao.territorio_nome}</h2>")
            
            # Adicionar informações detalhadas
            labels = [
                ("Saída de Campo:", designacao.saida_campo_nome),
                ("Data de Designação:", designacao.data_designacao),
                ("Data de Devolução:", designacao.data_devolucao or "Não definida")
            ]
            
            for row, (label, value) in enumerate(labels):
                self.territorio_detalhes_layout.addWidget(QLabel(label), row, 0)
                self.territorio_detalhes_layout.addWidget(QLabel(value), row, 1)
            
            # Adicionar botão para visualizar território
            btn_visualizar = QPushButton("Ver Detalhes")
            btn_visualizar.setStyleSheet("background-color: #4CAF50; color: white;")
            self.territorio_hoje_layout.addWidget(btn_visualizar)
            
        else:
            self.territorio_hoje_label.setText("<h3>Nenhum território designado para hoje</h3>")
    
    def update_proximas_designacoes(self):
        """Atualiza a tabela de próximas designações"""
        designacoes = Designacao.get_ativas(self.db_manager)
        
        self.designacoes_table.setRowCount(0)
        
        for row, designacao in enumerate(designacoes[:5]):  # Limitar a 5 designações
            self.designacoes_table.insertRow(row)
            
            self.designacoes_table.setItem(row, 0, QTableWidgetItem(designacao.territorio_nome))
            self.designacoes_table.setItem(row, 1, QTableWidgetItem(designacao.saida_campo_nome))
            self.designacoes_table.setItem(row, 2, QTableWidgetItem(designacao.data_designacao))
            
            status_item = QTableWidgetItem("Ativo")
            status_item.setForeground(QColor("#4CAF50"))  # Verde
            self.designacoes_table.setItem(row, 3, status_item)
    
    def update_proximas_saidas(self):
        """Atualiza a tabela de próximas saídas de campo"""
        saidas = SaidaCampo.get_proximas(self.db_manager, 5)
        
        self.saidas_table.setRowCount(0)
        
        for row, saida in enumerate(saidas):
            self.saidas_table.insertRow(row)
            
            self.saidas_table.setItem(row, 0, QTableWidgetItem(saida.nome))
            
            # Formatar data
            try:
                data = QDate.fromString(saida.data, "yyyy-MM-dd").toString("dd/MM/yyyy")
            except:
                data = saida.data
                
            self.saidas_table.setItem(row, 1, QTableWidgetItem(data))
            self.saidas_table.setItem(row, 2, QTableWidgetItem(saida.dia_semana))
            self.saidas_table.setItem(row, 3, QTableWidgetItem(saida.horario))
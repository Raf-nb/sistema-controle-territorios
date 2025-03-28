#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QPushButton, QLineEdit, QComboBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QDialog, QFormLayout,
                             QDateEdit, QTimeEdit)
from PySide6.QtCore import Qt, Signal, Slot, QDate, QTime
from PySide6.QtGui import QIcon, QFont

from models.saida_campo import SaidaCampo
from datetime import datetime

class SaidasCampoWidget(QWidget):
    """Widget para cadastro e gerenciamento de saídas de campo"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.saidas = []
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        main_layout = QVBoxLayout(self)
        
        # Título da página
        title_label = QLabel("Cadastro de Saídas de Campo")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Form para adicionar saída de campo
        form_group = QGroupBox("Adicionar Nova Saída de Campo")
        form_layout = QFormLayout(form_group)
        
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Ex: Saída Matutina")
        form_layout.addRow("Nome da Saída:", self.nome_input)
        
        # Data
        self.data_input = QDateEdit(QDate.currentDate())
        self.data_input.setCalendarPopup(True)
        self.data_input.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Data:", self.data_input)
        
        # Dia da semana (será preenchido automaticamente)
        self.dia_semana_input = QLineEdit()
        self.dia_semana_input.setReadOnly(True)
        form_layout.addRow("Dia da Semana:", self.dia_semana_input)
        
        # Horário
        self.horario_input = QTimeEdit(QTime(9, 0))
        self.horario_input.setDisplayFormat("HH:mm")
        form_layout.addRow("Horário:", self.horario_input)
        
        # Dirigente
        self.dirigente_input = QLineEdit()
        self.dirigente_input.setPlaceholderText("Ex: João Silva")
        form_layout.addRow("Dirigente (opcional):", self.dirigente_input)
        
        # Botão para adicionar
        add_button = QPushButton("Adicionar Saída")
        add_button.setStyleSheet("background-color: #4CAF50; color: white;")
        add_button.clicked.connect(self.add_saida)
        form_layout.addRow("", add_button)
        
        main_layout.addWidget(form_group)
        
        # Tabela de saídas de campo
        table_group = QGroupBox("Saídas de Campo Cadastradas")
        table_layout = QVBoxLayout(table_group)
        
        self.table = QTableWidget(0, 6)  # 6 colunas: ID, Nome, Data, Dia, Horário, Dirigente
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Data", "Dia da Semana", "Horário", "Dirigente"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setColumnHidden(0, True)  # Esconder coluna ID
        self.table.verticalHeader().setVisible(False)
        table_layout.addWidget(self.table)
        
        # Botões para gerenciar as saídas
        buttons_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("Editar")
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.edit_saida)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Excluir")
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_button.clicked.connect(self.delete_saida)
        buttons_layout.addWidget(self.delete_button)
        
        table_layout.addLayout(buttons_layout)
        main_layout.addWidget(table_group)
        
        # Conectar sinais
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.data_input.dateChanged.connect(self.update_dia_semana)
        
        # Preencher o dia da semana inicial
        self.update_dia_semana()
    
    def load_data(self):
        """Carrega os dados das saídas de campo"""
        self.saidas = SaidaCampo.get_all(self.db_manager)
        self.update_table()
    
    def update_table(self):
        """Atualiza a tabela de saídas de campo"""
        self.table.setRowCount(0)
        
        for row, saida in enumerate(self.saidas):
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(saida.id)))
            self.table.setItem(row, 1, QTableWidgetItem(saida.nome))
            
            # Formatar data
            try:
                data = QDate.fromString(saida.data, "yyyy-MM-dd").toString("dd/MM/yyyy")
            except:
                data = saida.data
            
            self.table.setItem(row, 2, QTableWidgetItem(data))
            self.table.setItem(row, 3, QTableWidgetItem(saida.dia_semana))
            self.table.setItem(row, 4, QTableWidgetItem(saida.horario))
            self.table.setItem(row, 5, QTableWidgetItem(saida.dirigente or "-"))
    
    @Slot()
    def update_dia_semana(self):
        """Atualiza o dia da semana com base na data selecionada"""
        date = self.data_input.date()
        # Obter o nome do dia da semana em português
        dias = ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"]
        day_of_week = date.dayOfWeek() % 7  # 0 = Domingo, 1 = Segunda, ...
        self.dia_semana_input.setText(dias[day_of_week])
    
    @Slot()
    def add_saida(self):
        """Adiciona uma nova saída de campo"""
        nome = self.nome_input.text().strip()
        data = self.data_input.date().toString("yyyy-MM-dd")
        dia_semana = self.dia_semana_input.text()
        horario = self.horario_input.time().toString("HH:mm")
        dirigente = self.dirigente_input.text().strip() or None
        
        if not nome:
            QMessageBox.warning(self, "Atenção", "O nome da saída de campo é obrigatório.")
            return
        
        saida = SaidaCampo(nome=nome, data=data, dia_semana=dia_semana, 
                           horario=horario, dirigente=dirigente)
        
        if saida.save(self.db_manager):
            QMessageBox.information(self, "Sucesso", "Saída de campo adicionada com sucesso.")
            self.nome_input.clear()
            self.dirigente_input.clear()
            self.load_data()
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível adicionar a saída de campo.")
    
    @Slot()
    def edit_saida(self):
        """Edita a saída de campo selecionada"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        saida_id = int(self.table.item(row, 0).text())
        
        # Buscar a saída de campo pelo ID
        saida = None
        for s in self.saidas:
            if s.id == saida_id:
                saida = s
                break
        
        if not saida:
            QMessageBox.critical(self, "Erro", "Saída de campo não encontrada.")
            return
        
        # Criar diálogo para edição
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Saída de Campo")
        dialog.resize(400, 250)
        
        layout = QFormLayout(dialog)
        
        nome_input = QLineEdit(saida.nome)
        layout.addRow("Nome:", nome_input)
        
        # Data
        data_edit = QDateEdit()
        data_edit.setCalendarPopup(True)
        data_edit.setDisplayFormat("dd/MM/yyyy")
        data_edit.setDate(QDate.fromString(saida.data, "yyyy-MM-dd"))
        layout.addRow("Data:", data_edit)
        
        # Dia da semana (calculado automaticamente)
        dia_semana_input = QLineEdit(saida.dia_semana)
        dia_semana_input.setReadOnly(True)
        layout.addRow("Dia da Semana:", dia_semana_input)
        
        # Atualizar dia da semana quando a data mudar
        def update_dia_semana_dialog():
            date = data_edit.date()
            dias = ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"]
            day_of_week = date.dayOfWeek() % 7
            dia_semana_input.setText(dias[day_of_week])
        
        data_edit.dateChanged.connect(update_dia_semana_dialog)
        
        # Horário
        horario_edit = QTimeEdit()
        horario_edit.setDisplayFormat("HH:mm")
        time_parts = saida.horario.split(":")
        if len(time_parts) == 2:
            horario_edit.setTime(QTime(int(time_parts[0]), int(time_parts[1])))
        layout.addRow("Horário:", horario_edit)
        
        # Dirigente
        dirigente_input = QLineEdit(saida.dirigente or "")
        layout.addRow("Dirigente (opcional):", dirigente_input)
        
        # Botões
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = QPushButton("Salvar")
        save_button.setStyleSheet("background-color: #4CAF50; color: white;")
        save_button.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        layout.addRow("", buttons_layout)
        
        if dialog.exec():
            nome = nome_input.text().strip()
            data = data_edit.date().toString("yyyy-MM-dd")
            dia_semana = dia_semana_input.text()
            horario = horario_edit.time().toString("HH:mm")
            dirigente = dirigente_input.text().strip() or None
            
            if not nome:
                QMessageBox.warning(self, "Atenção", "O nome da saída de campo é obrigatório.")
                return
            
            saida.nome = nome
            saida.data = data
            saida.dia_semana = dia_semana
            saida.horario = horario
            saida.dirigente = dirigente
            
            if saida.save(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Saída de campo atualizada com sucesso.")
                self.load_data()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível atualizar a saída de campo.")
    
    @Slot()
    def delete_saida(self):
        """Exclui a saída de campo selecionada"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        saida_id = int(self.table.item(row, 0).text())
        saida_nome = self.table.item(row, 1).text()
        
        # Confirmar exclusão
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a saída de campo '{saida_nome}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Buscar e excluir a saída
            for saida in self.saidas:
                if saida.id == saida_id:
                    if saida.delete(self.db_manager):
                        QMessageBox.information(self, "Sucesso", "Saída de campo excluída com sucesso.")
                        self.load_data()
                        self.edit_button.setEnabled(False)
                        self.delete_button.setEnabled(False)
                    else:
                        QMessageBox.critical(self, "Erro", "Não foi possível excluir a saída de campo.")
                    break
    
    @Slot()
    def on_selection_changed(self):
        """Atualiza o estado dos botões quando a seleção muda"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
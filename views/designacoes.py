#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QPushButton, QLineEdit, QComboBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QDialog, QFormLayout, QDateEdit,
                             QTabWidget, QSplitter)
from PySide6.QtCore import Qt, Signal, Slot, QDate
from PySide6.QtGui import QIcon, QFont, QColor

from models.territorio import Territorio
from models.designacao import Designacao, DesignacaoPredioVila
from models.saida_campo import SaidaCampo
from models.imovel import Imovel

from datetime import datetime, timedelta

class DesignacoesWidget(QWidget):
    """Widget para gerenciamento de designações de territórios"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.territorios = []
        self.saidas_campo = []
        self.designacoes = []
        self.predios_vilas = []
        self.designacoes_predios_vilas = []
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        main_layout = QVBoxLayout(self)
        
        # Título da página
        title_label = QLabel("Designação de Territórios")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Tabs para tipos de designação
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Tab para designação de territórios
        territorios_tab = QWidget()
        self.tabs.addTab(territorios_tab, "Territórios")
        
        # Tab para designação de prédios e vilas
        predios_vilas_tab = QWidget()
        self.tabs.addTab(predios_vilas_tab, "Prédios e Vilas")
        
        # === Tab de Territórios ===
        territorios_layout = QVBoxLayout(territorios_tab)
        
        # Form para designar território
        form_group = QGroupBox("Designar Território")
        form_layout = QFormLayout(form_group)
        
        # Combobox de territórios
        self.territorio_select = QComboBox()
        form_layout.addRow("Território:", self.territorio_select)
        
        # Combobox de saídas de campo
        self.saida_campo_select = QComboBox()
        form_layout.addRow("Saída de Campo:", self.saida_campo_select)
        
        # Data de designação
        self.data_designacao_input = QDateEdit(QDate.currentDate())
        self.data_designacao_input.setCalendarPopup(True)
        self.data_designacao_input.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Data de Designação:", self.data_designacao_input)
        
        # Data de devolução (opcional)
        self.data_devolucao_input = QDateEdit(QDate.currentDate().addDays(15))
        self.data_devolucao_input.setCalendarPopup(True)
        self.data_devolucao_input.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Data de Devolução (opcional):", self.data_devolucao_input)
        
        # Responsável (opcional)
        self.responsavel_input = QLineEdit()
        self.responsavel_input.setPlaceholderText("Ex: João Silva")
        form_layout.addRow("Responsável (opcional):", self.responsavel_input)
        
        # Botão para designar
        designar_button = QPushButton("Designar Território")
        designar_button.setStyleSheet("background-color: #4CAF50; color: white;")
        designar_button.clicked.connect(self.designar_territorio)
        form_layout.addRow("", designar_button)
        
        territorios_layout.addWidget(form_group)
        
        # Tabela de designações
        territorios_layout.addWidget(QLabel("Designações Registradas"))
        
        self.designacoes_table = QTableWidget(0, 7)  # ID, Território, Saída, Data Des., Data Dev., Responsável, Status
        self.designacoes_table.setHorizontalHeaderLabels([
            "ID", "Território", "Saída de Campo", "Data de Designação", 
            "Data de Devolução", "Responsável", "Status"
        ])
        self.designacoes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.designacoes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.designacoes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.designacoes_table.setColumnHidden(0, True)  # Esconder coluna ID
        self.designacoes_table.verticalHeader().setVisible(False)
        self.designacoes_table.itemSelectionChanged.connect(self.on_designacao_selection_changed)
        territorios_layout.addWidget(self.designacoes_table)
        
        # Botões para gerenciar designações
        buttons_layout = QHBoxLayout()
        
        self.ver_territorio_button = QPushButton("Ver Território")
        self.ver_territorio_button.setEnabled(False)
        buttons_layout.addWidget(self.ver_territorio_button)
        
        self.editar_designacao_button = QPushButton("Editar")
        self.editar_designacao_button.setEnabled(False)
        self.editar_designacao_button.clicked.connect(self.editar_designacao)
        buttons_layout.addWidget(self.editar_designacao_button)
        
        self.concluir_designacao_button = QPushButton("Concluir")
        self.concluir_designacao_button.setEnabled(False)
        self.concluir_designacao_button.setStyleSheet("background-color: #2196F3; color: white;")
        self.concluir_designacao_button.clicked.connect(self.concluir_designacao)
        buttons_layout.addWidget(self.concluir_designacao_button)
        
        self.excluir_designacao_button = QPushButton("Excluir")
        self.excluir_designacao_button.setEnabled(False)
        self.excluir_designacao_button.setStyleSheet("background-color: #f44336; color: white;")
        self.excluir_designacao_button.clicked.connect(self.excluir_designacao)
        buttons_layout.addWidget(self.excluir_designacao_button)
        
        territorios_layout.addLayout(buttons_layout)
        
        # === Tab de Prédios e Vilas ===
        predios_vilas_layout = QVBoxLayout(predios_vilas_tab)
        
        # Form para designar prédio/vila
        pv_form_group = QGroupBox("Designar Prédio/Vila")
        pv_form_layout = QFormLayout(pv_form_group)
        
        # Combobox de prédios/vilas
        self.predio_vila_select = QComboBox()
        pv_form_layout.addRow("Prédio/Vila:", self.predio_vila_select)
        
        # Combobox de saídas de campo
        self.pv_saida_campo_select = QComboBox()
        pv_form_layout.addRow("Saída de Campo:", self.pv_saida_campo_select)
        
        # Responsável
        self.pv_responsavel_input = QLineEdit()
        self.pv_responsavel_input.setPlaceholderText("Ex: João Silva")
        pv_form_layout.addRow("Responsável:", self.pv_responsavel_input)
        
        # Data de designação
        self.pv_data_designacao_input = QDateEdit(QDate.currentDate())
        self.pv_data_designacao_input.setCalendarPopup(True)
        self.pv_data_designacao_input.setDisplayFormat("dd/MM/yyyy")
        pv_form_layout.addRow("Data de Designação:", self.pv_data_designacao_input)
        
        # Data de devolução (opcional)
        self.pv_data_devolucao_input = QDateEdit(QDate.currentDate().addDays(15))
        self.pv_data_devolucao_input.setCalendarPopup(True)
        self.pv_data_devolucao_input.setDisplayFormat("dd/MM/yyyy")
        pv_form_layout.addRow("Data de Devolução (opcional):", self.pv_data_devolucao_input)
        
        # Botão para designar
        pv_designar_button = QPushButton("Designar Prédio/Vila")
        pv_designar_button.setStyleSheet("background-color: #4CAF50; color: white;")
        pv_designar_button.clicked.connect(self.designar_predio_vila)
        pv_form_layout.addRow("", pv_designar_button)
        
        predios_vilas_layout.addWidget(pv_form_group)
        
        # Tabela de designações de prédios/vilas
        predios_vilas_layout.addWidget(QLabel("Designações de Prédios/Vilas Registradas"))
        
        self.pv_designacoes_table = QTableWidget(0, 8)  # ID, Prédio/Vila, Tipo, Local, Saída, Resp., Data Des., Status
        self.pv_designacoes_table.setHorizontalHeaderLabels([
            "ID", "Prédio/Vila", "Tipo", "Localização", "Saída de Campo", 
            "Responsável", "Data de Designação", "Status"
        ])
        self.pv_designacoes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pv_designacoes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.pv_designacoes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.pv_designacoes_table.setColumnHidden(0, True)  # Esconder coluna ID
        self.pv_designacoes_table.setHorizontalHeaderLabels([
            "ID", "Prédio/Vila", "Tipo", "Localização", "Saída de Campo", 
            "Responsável", "Data de Designação", "Status"
        ])
        self.pv_designacoes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pv_designacoes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.pv_designacoes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.pv_designacoes_table.setColumnHidden(0, True)  # Esconder coluna ID
        self.pv_designacoes_table.verticalHeader().setVisible(False)
        self.pv_designacoes_table.itemSelectionChanged.connect(self.on_pv_designacao_selection_changed)
        predios_vilas_layout.addWidget(self.pv_designacoes_table)
        
        # Botões para gerenciar designações de prédios/vilas
        pv_buttons_layout = QHBoxLayout()
        
        self.pv_ver_button = QPushButton("Ver Detalhes")
        self.pv_ver_button.setEnabled(False)
        pv_buttons_layout.addWidget(self.pv_ver_button)
        
        self.pv_editar_button = QPushButton("Editar")
        self.pv_editar_button.setEnabled(False)
        self.pv_editar_button.clicked.connect(self.editar_pv_designacao)
        pv_buttons_layout.addWidget(self.pv_editar_button)
        
        self.pv_concluir_button = QPushButton("Concluir")
        self.pv_concluir_button.setEnabled(False)
        self.pv_concluir_button.setStyleSheet("background-color: #2196F3; color: white;")
        self.pv_concluir_button.clicked.connect(self.concluir_pv_designacao)
        pv_buttons_layout.addWidget(self.pv_concluir_button)
        
        self.pv_excluir_button = QPushButton("Excluir")
        self.pv_excluir_button.setEnabled(False)
        self.pv_excluir_button.setStyleSheet("background-color: #f44336; color: white;")
        self.pv_excluir_button.clicked.connect(self.excluir_pv_designacao)
        pv_buttons_layout.addWidget(self.pv_excluir_button)
        
        predios_vilas_layout.addLayout(pv_buttons_layout)
    
    def load_data(self):
        """Carrega os dados necessários para a interface"""
        # Carregar territórios
        self.territorios = Territorio.get_all(self.db_manager)
        self.territorio_select.clear()
        for territorio in self.territorios:
            self.territorio_select.addItem(territorio.nome, territorio.id)
        
        # Carregar saídas de campo
        self.saidas_campo = SaidaCampo.get_all(self.db_manager)
        self.saida_campo_select.clear()
        self.pv_saida_campo_select.clear()
        for saida in self.saidas_campo:
            self.saida_campo_select.addItem(saida.nome, saida.id)
            self.pv_saida_campo_select.addItem(saida.nome, saida.id)
        
        # Carregar designações
        self.designacoes = Designacao.get_all(self.db_manager)
        self.update_designacoes_table()
        
        # Carregar prédios e vilas
        self.predios_vilas = Imovel.get_predios_vilas(self.db_manager)
        self.predio_vila_select.clear()
        for imovel in self.predios_vilas:
            nome = imovel.nome if imovel.nome else f"Nº {imovel.numero}"
            texto = f"{nome} ({imovel.tipo.capitalize()}) - {imovel.rua_nome}"
            self.predio_vila_select.addItem(texto, imovel.id)
        
        # Carregar designações de prédios e vilas
        self.designacoes_predios_vilas = DesignacaoPredioVila.get_all(self.db_manager)
        self.update_pv_designacoes_table()
    
    def update_designacoes_table(self):
        """Atualiza a tabela de designações"""
        self.designacoes_table.setRowCount(0)
        
        for row, designacao in enumerate(self.designacoes):
            self.designacoes_table.insertRow(row)
            
            self.designacoes_table.setItem(row, 0, QTableWidgetItem(str(designacao.id)))
            self.designacoes_table.setItem(row, 1, QTableWidgetItem(designacao.territorio_nome))
            self.designacoes_table.setItem(row, 2, QTableWidgetItem(designacao.saida_campo_nome))
            
            # Formatar datas
            try:
                data_des = QDate.fromString(designacao.data_designacao, "yyyy-MM-dd").toString("dd/MM/yyyy")
            except:
                data_des = designacao.data_designacao
            
            self.designacoes_table.setItem(row, 3, QTableWidgetItem(data_des))
            
            if designacao.data_devolucao:
                try:
                    data_dev = QDate.fromString(designacao.data_devolucao, "yyyy-MM-dd").toString("dd/MM/yyyy")
                except:
                    data_dev = designacao.data_devolucao
            else:
                data_dev = "Não definida"
            
            self.designacoes_table.setItem(row, 4, QTableWidgetItem(data_dev))
            self.designacoes_table.setItem(row, 5, QTableWidgetItem(designacao.responsavel or "-"))
            
            # Status com cor
            status_item = QTableWidgetItem(designacao.status.capitalize())
            if designacao.status == "ativo":
                status_item.setForeground(QColor("#4CAF50"))  # Verde
            else:
                status_item.setForeground(QColor("#9E9E9E"))  # Cinza
            
            self.designacoes_table.setItem(row, 6, status_item)
    
    def update_pv_designacoes_table(self):
        """Atualiza a tabela de designações de prédios e vilas"""
        self.pv_designacoes_table.setRowCount(0)
        
        for row, designacao in enumerate(self.designacoes_predios_vilas):
            self.pv_designacoes_table.insertRow(row)
            
            self.pv_designacoes_table.setItem(row, 0, QTableWidgetItem(str(designacao.id)))
            
            nome = designacao.imovel_nome if designacao.imovel_nome else f"Nº {designacao.imovel_numero}"
            self.pv_designacoes_table.setItem(row, 1, QTableWidgetItem(nome))
            self.pv_designacoes_table.setItem(row, 2, QTableWidgetItem(designacao.imovel_tipo.capitalize()))
            self.pv_designacoes_table.setItem(row, 3, QTableWidgetItem(f"{designacao.rua_nome}, {designacao.territorio_nome}"))
            self.pv_designacoes_table.setItem(row, 4, QTableWidgetItem(designacao.saida_campo_nome))
            self.pv_designacoes_table.setItem(row, 5, QTableWidgetItem(designacao.responsavel))
            
            # Formatar data
            try:
                data_des = QDate.fromString(designacao.data_designacao, "yyyy-MM-dd").toString("dd/MM/yyyy")
            except:
                data_des = designacao.data_designacao
            
            self.pv_designacoes_table.setItem(row, 6, QTableWidgetItem(data_des))
            
            # Status com cor
            status_item = QTableWidgetItem(designacao.status.capitalize())
            if designacao.status == "ativo":
                status_item.setForeground(QColor("#4CAF50"))  # Verde
            else:
                status_item.setForeground(QColor("#9E9E9E"))  # Cinza
            
            self.pv_designacoes_table.setItem(row, 7, status_item)
    
    @Slot()
    def designar_territorio(self):
        """Designa um território"""
        territorio_id = self.territorio_select.currentData()
        saida_campo_id = self.saida_campo_select.currentData()
        data_designacao = self.data_designacao_input.date().toString("yyyy-MM-dd")
        data_devolucao = self.data_devolucao_input.date().toString("yyyy-MM-dd")
        responsavel = self.responsavel_input.text().strip() or None
        
        if not territorio_id:
            QMessageBox.warning(self, "Atenção", "Selecione um território.")
            return
        
        if not saida_campo_id:
            QMessageBox.warning(self, "Atenção", "Selecione uma saída de campo.")
            return
        
        # Verificar se o território já está designado
        territorio_ativo = False
        for d in self.designacoes:
            if d.territorio_id == territorio_id and d.status == "ativo":
                territorio_ativo = True
                break
        
        if territorio_ativo:
            reply = QMessageBox.question(
                self, "Território já designado",
                "Este território já possui uma designação ativa. Deseja criar uma nova designação mesmo assim?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Criar a designação
        designacao = Designacao(
            territorio_id=territorio_id,
            saida_campo_id=saida_campo_id,
            data_designacao=data_designacao,
            data_devolucao=data_devolucao,
            responsavel=responsavel,
            status="ativo"
        )
        
        if designacao.save(self.db_manager):
            QMessageBox.information(self, "Sucesso", "Território designado com sucesso.")
            self.responsavel_input.clear()
            # Atualizar a tabela
            self.load_data()
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível designar o território.")
    
    @Slot()
    def designar_predio_vila(self):
        """Designa um prédio ou vila"""
        imovel_id = self.predio_vila_select.currentData()
        saida_campo_id = self.pv_saida_campo_select.currentData()
        responsavel = self.pv_responsavel_input.text().strip()
        data_designacao = self.pv_data_designacao_input.date().toString("yyyy-MM-dd")
        data_devolucao = self.pv_data_devolucao_input.date().toString("yyyy-MM-dd")
        
        if not imovel_id:
            QMessageBox.warning(self, "Atenção", "Selecione um prédio ou vila.")
            return
        
        if not saida_campo_id:
            QMessageBox.warning(self, "Atenção", "Selecione uma saída de campo.")
            return
        
        if not responsavel:
            QMessageBox.warning(self, "Atenção", "Informe o responsável pela designação.")
            return
        
        # Verificar se o prédio/vila já está designado
        imovel_ativo = False
        for d in self.designacoes_predios_vilas:
            if d.imovel_id == imovel_id and d.status == "ativo":
                imovel_ativo = True
                break
        
        if imovel_ativo:
            reply = QMessageBox.question(
                self, "Prédio/Vila já designado",
                "Este prédio/vila já possui uma designação ativa. Deseja criar uma nova designação mesmo assim?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Criar a designação
        designacao = DesignacaoPredioVila(
            imovel_id=imovel_id,
            responsavel=responsavel,
            saida_campo_id=saida_campo_id,
            data_designacao=data_designacao,
            data_devolucao=data_devolucao,
            status="ativo"
        )
        
        if designacao.save(self.db_manager):
            QMessageBox.information(self, "Sucesso", "Prédio/Vila designado com sucesso.")
            self.pv_responsavel_input.clear()
            # Atualizar a tabela
            self.load_data()
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível designar o prédio/vila.")
    
    @Slot()
    def editar_designacao(self):
        """Edita a designação selecionada"""
        selected_items = self.designacoes_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        designacao_id = int(self.designacoes_table.item(row, 0).text())
        
        # Buscar a designação
        designacao = None
        for d in self.designacoes:
            if d.id == designacao_id:
                designacao = d
                break
        
        if not designacao:
            QMessageBox.critical(self, "Erro", "Designação não encontrada.")
            return
        
        # Criar diálogo para edição
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Designação")
        dialog.resize(400, 300)
        
        layout = QFormLayout(dialog)
        
        # Território (somente leitura)
        territorio_label = QLabel(designacao.territorio_nome)
        layout.addRow("Território:", territorio_label)
        
        # Saída de campo
        saida_select = QComboBox()
        for saida in self.saidas_campo:
            saida_select.addItem(saida.nome, saida.id)
            if saida.id == designacao.saida_campo_id:
                saida_select.setCurrentText(saida.nome)
        layout.addRow("Saída de Campo:", saida_select)
        
        # Data de designação
        data_des_edit = QDateEdit()
        data_des_edit.setCalendarPopup(True)
        data_des_edit.setDisplayFormat("dd/MM/yyyy")
        data_des_edit.setDate(QDate.fromString(designacao.data_designacao, "yyyy-MM-dd"))
        layout.addRow("Data de Designação:", data_des_edit)
        
        # Data de devolução
        data_dev_edit = QDateEdit()
        data_dev_edit.setCalendarPopup(True)
        data_dev_edit.setDisplayFormat("dd/MM/yyyy")
        if designacao.data_devolucao:
            data_dev_edit.setDate(QDate.fromString(designacao.data_devolucao, "yyyy-MM-dd"))
        else:
            data_dev_edit.setDate(QDate.currentDate().addDays(15))
        layout.addRow("Data de Devolução:", data_dev_edit)
        
        # Responsável
        responsavel_input = QLineEdit(designacao.responsavel or "")
        layout.addRow("Responsável:", responsavel_input)
        
        # Status
        status_select = QComboBox()
        status_select.addItems(["Ativo", "Concluído"])
        status_select.setCurrentText(designacao.status.capitalize())
        layout.addRow("Status:", status_select)
        
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
            # Atualizar a designação
            designacao.saida_campo_id = saida_select.currentData()
            designacao.data_designacao = data_des_edit.date().toString("yyyy-MM-dd")
            designacao.data_devolucao = data_dev_edit.date().toString("yyyy-MM-dd")
            designacao.responsavel = responsavel_input.text().strip() or None
            designacao.status = status_select.currentText().lower()
            
            if designacao.save(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Designação atualizada com sucesso.")
                self.load_data()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível atualizar a designação.")
    
    @Slot()
    def concluir_designacao(self):
        """Conclui a designação selecionada"""
        selected_items = self.designacoes_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        designacao_id = int(self.designacoes_table.item(row, 0).text())
        
        # Buscar a designação
        designacao = None
        for d in self.designacoes:
            if d.id == designacao_id:
                designacao = d
                break
        
        if not designacao:
            QMessageBox.critical(self, "Erro", "Designação não encontrada.")
            return
        
        reply = QMessageBox.question(
            self, "Confirmar Conclusão",
            f"Tem certeza que deseja concluir a designação do território '{designacao.territorio_nome}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if designacao.concluir(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Designação concluída com sucesso.")
                self.load_data()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível concluir a designação.")
    
    @Slot()
    def excluir_designacao(self):
        """Exclui a designação selecionada"""
        selected_items = self.designacoes_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        designacao_id = int(self.designacoes_table.item(row, 0).text())
        territorio_nome = self.designacoes_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a designação do território '{territorio_nome}'?\n"
            f"Esta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Buscar e excluir a designação
            for designacao in self.designacoes:
                if designacao.id == designacao_id:
                    if designacao.delete(self.db_manager):
                        QMessageBox.information(self, "Sucesso", "Designação excluída com sucesso.")
                        self.load_data()
                        self.editar_designacao_button.setEnabled(False)
                        self.concluir_designacao_button.setEnabled(False)
                        self.excluir_designacao_button.setEnabled(False)
                    else:
                        QMessageBox.critical(self, "Erro", "Não foi possível excluir a designação.")
                    break
    
    @Slot()
    def editar_pv_designacao(self):
        """Edita a designação de prédio/vila selecionada"""
        selected_items = self.pv_designacoes_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        designacao_id = int(self.pv_designacoes_table.item(row, 0).text())
        
        # Buscar a designação
        designacao = None
        for d in self.designacoes_predios_vilas:
            if d.id == designacao_id:
                designacao = d
                break
        
        if not designacao:
            QMessageBox.critical(self, "Erro", "Designação não encontrada.")
            return
        
        # Criar diálogo para edição
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Designação de Prédio/Vila")
        dialog.resize(400, 300)
        
        layout = QFormLayout(dialog)
        
        # Prédio/Vila (somente leitura)
        nome = designacao.imovel_nome if designacao.imovel_nome else f"Nº {designacao.imovel_numero}"
        imovel_label = QLabel(f"{nome} ({designacao.imovel_tipo.capitalize()})")
        layout.addRow("Prédio/Vila:", imovel_label)
        
        # Saída de campo
        saida_select = QComboBox()
        for saida in self.saidas_campo:
            saida_select.addItem(saida.nome, saida.id)
            if saida.id == designacao.saida_campo_id:
                saida_select.setCurrentText(saida.nome)
        layout.addRow("Saída de Campo:", saida_select)
        
        # Responsável
        responsavel_input = QLineEdit(designacao.responsavel)
        layout.addRow("Responsável:", responsavel_input)
        
        # Data de designação
        data_des_edit = QDateEdit()
        data_des_edit.setCalendarPopup(True)
        data_des_edit.setDisplayFormat("dd/MM/yyyy")
        data_des_edit.setDate(QDate.fromString(designacao.data_designacao, "yyyy-MM-dd"))
        layout.addRow("Data de Designação:", data_des_edit)
        
        # Data de devolução
        data_dev_edit = QDateEdit()
        data_dev_edit.setCalendarPopup(True)
        data_dev_edit.setDisplayFormat("dd/MM/yyyy")
        if designacao.data_devolucao:
            data_dev_edit.setDate(QDate.fromString(designacao.data_devolucao, "yyyy-MM-dd"))
        else:
            data_dev_edit.setDate(QDate.currentDate().addDays(15))
        layout.addRow("Data de Devolução:", data_dev_edit)
        
        # Status
        status_select = QComboBox()
        status_select.addItems(["Ativo", "Concluído"])
        status_select.setCurrentText(designacao.status.capitalize())
        layout.addRow("Status:", status_select)
        
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
            # Atualizar a designação
            designacao.saida_campo_id = saida_select.currentData()
            designacao.responsavel = responsavel_input.text().strip()
            designacao.data_designacao = data_des_edit.date().toString("yyyy-MM-dd")
            designacao.data_devolucao = data_dev_edit.date().toString("yyyy-MM-dd")
            designacao.status = status_select.currentText().lower()
            
            if not designacao.responsavel:
                QMessageBox.warning(self, "Atenção", "O responsável é obrigatório.")
                return
            
            if designacao.save(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Designação atualizada com sucesso.")
                self.load_data()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível atualizar a designação.")
    
    @Slot()
    def concluir_pv_designacao(self):
        """Conclui a designação de prédio/vila selecionada"""
        selected_items = self.pv_designacoes_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        designacao_id = int(self.pv_designacoes_table.item(row, 0).text())
        nome_pv = self.pv_designacoes_table.item(row, 1).text()
        
        # Buscar a designação
        designacao = None
        for d in self.designacoes_predios_vilas:
            if d.id == designacao_id:
                designacao = d
                break
        
        if not designacao:
            QMessageBox.critical(self, "Erro", "Designação não encontrada.")
            return
        
        reply = QMessageBox.question(
            self, "Confirmar Conclusão",
            f"Tem certeza que deseja concluir a designação do prédio/vila '{nome_pv}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if designacao.concluir(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Designação concluída com sucesso.")
                self.load_data()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível concluir a designação.")
    
    @Slot()
    def excluir_pv_designacao(self):
        """Exclui a designação de prédio/vila selecionada"""
        selected_items = self.pv_designacoes_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        designacao_id = int(self.pv_designacoes_table.item(row, 0).text())
        nome_pv = self.pv_designacoes_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a designação do prédio/vila '{nome_pv}'?\n"
            f"Esta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Buscar e excluir a designação
            for designacao in self.designacoes_predios_vilas:
                if designacao.id == designacao_id:
                    if designacao.delete(self.db_manager):
                        QMessageBox.information(self, "Sucesso", "Designação excluída com sucesso.")
                        self.load_data()
                        self.pv_editar_button.setEnabled(False)
                        self.pv_concluir_button.setEnabled(False)
                        self.pv_excluir_button.setEnabled(False)
                    else:
                        QMessageBox.critical(self, "Erro", "Não foi possível excluir a designação.")
                    break
    
    @Slot()
    def on_designacao_selection_changed(self):
        """Atualiza o estado dos botões quando a seleção na tabela de designações muda"""
        has_selection = len(self.designacoes_table.selectedItems()) > 0
        self.ver_territorio_button.setEnabled(has_selection)
        self.editar_designacao_button.setEnabled(has_selection)
        self.concluir_designacao_button.setEnabled(has_selection)
        self.excluir_designacao_button.setEnabled(has_selection)
        
        if has_selection:
            row = self.designacoes_table.selectedItems()[0].row()
            status = self.designacoes_table.item(row, 6).text().lower()
            self.concluir_designacao_button.setEnabled(status == "ativo")
    
    @Slot()
    def on_pv_designacao_selection_changed(self):
        """Atualiza o estado dos botões quando a seleção na tabela de designações de prédios/vilas muda"""
        has_selection = len(self.pv_designacoes_table.selectedItems()) > 0
        self.pv_ver_button.setEnabled(has_selection)
        self.pv_editar_button.setEnabled(has_selection)
        self.pv_concluir_button.setEnabled(has_selection)
        self.pv_excluir_button.setEnabled(has_selection)
        
        if has_selection:
            row = self.pv_designacoes_table.selectedItems()[0].row()
            status = self.pv_designacoes_table.item(row, 7).text().lower()
            self.pv_concluir_button.setEnabled(status == "ativo")#!/usr/bin/env python3
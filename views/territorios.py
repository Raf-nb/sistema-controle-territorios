#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QPushButton, QLineEdit, QComboBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QDialog, QFormLayout, QTextEdit,
                             QTreeWidget, QTreeWidgetItem, QSplitter, QFrame,
                             QStackedWidget, QTabWidget, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QFont

from models.territorio import Territorio

class TerritoriosWidget(QWidget):
    """Widget para cadastro e gerenciamento de territórios"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.territorios = []
        self.current_territorio = None
        self.current_rua = None
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        main_layout = QVBoxLayout(self)
        
        # Título da página
        title_label = QLabel("Cadastro de Territórios")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Splitter para dividir a árvore de territórios e os detalhes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Painel esquerdo: Árvore de territórios
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Form para adicionar território
        form_group = QGroupBox("Adicionar Novo Território")
        form_layout = QFormLayout(form_group)
        
        self.territorio_nome_input = QLineEdit()
        self.territorio_nome_input.setPlaceholderText("Ex: Quadra 12 ou Setor Norte Quadra 5")
        form_layout.addRow("Nome do Território:", self.territorio_nome_input)
        
        self.territorio_desc_input = QLineEdit()
        self.territorio_desc_input.setPlaceholderText("Descrição (opcional)")
        form_layout.addRow("Descrição:", self.territorio_desc_input)
        
        add_button = QPushButton("Adicionar Território")
        add_button.setStyleSheet("background-color: #4CAF50; color: white;")
        add_button.clicked.connect(self.add_territorio)
        form_layout.addRow("", add_button)
        
        left_layout.addWidget(form_group)
        
        # Árvore de territórios
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Territórios"])
        self.tree.itemClicked.connect(self.on_item_clicked)
        left_layout.addWidget(self.tree)
        
        # Botões para gerenciar o território selecionado
        buttons_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("Editar")
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.edit_territorio)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Excluir")
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_button.clicked.connect(self.delete_territorio)
        buttons_layout.addWidget(self.delete_button)
        
        left_layout.addLayout(buttons_layout)
        
        # Painel direito: Detalhes do território selecionado
        right_panel = QWidget()
        self.right_layout = QVBoxLayout(right_panel)
        
        # Título do território selecionado
        self.detail_title = QLabel("Selecione um território")
        self.detail_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.right_layout.addWidget(self.detail_title)
        
        # Tabs para ruas e imóveis
        self.tabs = QTabWidget()
        self.right_layout.addWidget(self.tabs)
        
        # Tab de Ruas
        self.ruas_tab = QWidget()
        ruas_layout = QVBoxLayout(self.ruas_tab)
        
        # Form para adicionar rua
        rua_form_group = QGroupBox("Adicionar Nova Rua")
        rua_form_layout = QFormLayout(rua_form_group)
        
        self.rua_nome_input = QLineEdit()
        self.rua_nome_input.setPlaceholderText("Ex: Rua das Flores")
        rua_form_layout.addRow("Nome da Rua:", self.rua_nome_input)
        
        add_rua_button = QPushButton("Adicionar Rua")
        add_rua_button.setStyleSheet("background-color: #2196F3; color: white;")
        add_rua_button.clicked.connect(self.add_rua)
        rua_form_layout.addRow("", add_rua_button)
        
        ruas_layout.addWidget(rua_form_group)
        
        # Lista de ruas
        self.ruas_list = QListWidget()
        self.ruas_list.itemClicked.connect(self.on_rua_clicked)
        ruas_layout.addWidget(self.ruas_list)
        
        # Botões para gerenciar a rua selecionada
        rua_buttons_layout = QHBoxLayout()
        
        self.edit_rua_button = QPushButton("Editar Rua")
        self.edit_rua_button.setEnabled(False)
        self.edit_rua_button.clicked.connect(self.edit_rua)
        rua_buttons_layout.addWidget(self.edit_rua_button)
        
        self.delete_rua_button = QPushButton("Excluir Rua")
        self.delete_rua_button.setEnabled(False)
        self.delete_rua_button.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_rua_button.clicked.connect(self.delete_rua)
        rua_buttons_layout.addWidget(self.delete_rua_button)
        
        ruas_layout.addLayout(rua_buttons_layout)
        
        # Tab de Imóveis
        self.imoveis_tab = QWidget()
        imoveis_layout = QVBoxLayout(self.imoveis_tab)
        
        # Form para adicionar imóvel
        imovel_form_group = QGroupBox("Adicionar Novo Imóvel")
        imovel_form_layout = QFormLayout(imovel_form_group)
        
        self.rua_select = QComboBox()
        imovel_form_layout.addRow("Rua:", self.rua_select)
        
        self.imovel_numero_input = QLineEdit()
        self.imovel_numero_input.setPlaceholderText("Ex: 123")
        imovel_form_layout.addRow("Número:", self.imovel_numero_input)
        
        self.imovel_tipo_select = QComboBox()
        self.imovel_tipo_select.addItems(["Residencial", "Comercial", "Prédio", "Vila"])
        imovel_form_layout.addRow("Tipo:", self.imovel_tipo_select)
        
        add_imovel_button = QPushButton("Adicionar Imóvel")
        add_imovel_button.setStyleSheet("background-color: #9C27B0; color: white;")
        add_imovel_button.clicked.connect(self.add_imovel)
        imovel_form_layout.addRow("", add_imovel_button)
        
        imoveis_layout.addWidget(imovel_form_group)
        
        # Tabela de imóveis
        self.imoveis_table = QTableWidget(0, 4)
        self.imoveis_table.setHorizontalHeaderLabels(["ID", "Número", "Tipo", "Rua"])
        self.imoveis_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.imoveis_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.imoveis_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.imoveis_table.itemClicked.connect(self.on_imovel_clicked)
        self.imoveis_table.verticalHeader().setVisible(False)
        self.imoveis_table.setColumnHidden(0, True)  # Esconder coluna ID
        imoveis_layout.addWidget(self.imoveis_table)
        
        # Botões para gerenciar o imóvel selecionado
        imovel_buttons_layout = QHBoxLayout()
        
        self.edit_imovel_button = QPushButton("Editar Imóvel")
        self.edit_imovel_button.setEnabled(False)
        self.edit_imovel_button.clicked.connect(self.edit_imovel)
        imovel_buttons_layout.addWidget(self.edit_imovel_button)
        
        self.delete_imovel_button = QPushButton("Excluir Imóvel")
        self.delete_imovel_button.setEnabled(False)
        self.delete_imovel_button.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_imovel_button.clicked.connect(self.delete_imovel)
        imovel_buttons_layout.addWidget(self.delete_imovel_button)
        
        imoveis_layout.addLayout(imovel_buttons_layout)
        
        # Adicionar as tabs
        self.tabs.addTab(self.ruas_tab, "Ruas")
        self.tabs.addTab(self.imoveis_tab, "Imóveis")
        
        # Desativar até que um território seja selecionado
        self.tabs.setEnabled(False)
        
        # Adicionar os painéis ao splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])
    
    def load_data(self):
        """Carrega os dados dos territórios"""
        self.territorios = Territorio.get_all(self.db_manager)
        self.update_tree()
    
    def update_tree(self):
        """Atualiza a árvore de territórios"""
        self.tree.clear()
        
        for territorio in self.territorios:
            item = QTreeWidgetItem(self.tree)
            item.setText(0, territorio.nome)
            item.setData(0, Qt.ItemDataRole.UserRole, territorio.id)
            
            # Adicionar ruas como filhos
            ruas = territorio.get_ruas(self.db_manager)
            for rua in ruas:
                rua_item = QTreeWidgetItem(item)
                rua_item.setText(0, rua['nome'])
                rua_item.setData(0, Qt.ItemDataRole.UserRole, rua['id'])
        
        self.tree.expandAll()
    
    def update_ruas_list(self):
        """Atualiza a lista de ruas do território selecionado"""
        self.ruas_list.clear()
        
        if not self.current_territorio:
            return
        
        ruas = self.current_territorio.get_ruas(self.db_manager)
        for rua in ruas:
            item = QListWidgetItem(rua['nome'])
            item.setData(Qt.ItemDataRole.UserRole, rua['id'])
            self.ruas_list.addItem(item)
    
    def update_rua_select(self):
        """Atualiza o combobox de seleção de ruas"""
        self.rua_select.clear()
        
        if not self.current_territorio:
            return
        
        ruas = self.current_territorio.get_ruas(self.db_manager)
        for rua in ruas:
            self.rua_select.addItem(rua['nome'], rua['id'])
    
    def update_imoveis_table(self):
        """Atualiza a tabela de imóveis"""
        self.imoveis_table.setRowCount(0)
        
        if not self.current_territorio:
            return
        
        ruas = self.current_territorio.get_ruas(self.db_manager)
        row = 0
        
        for rua in ruas:
            cursor = self.db_manager.execute(
                "SELECT * FROM imoveis WHERE rua_id = ? ORDER BY numero",
                (rua['id'],)
            )
            if cursor:
                for imovel in cursor.fetchall():
                    self.imoveis_table.insertRow(row)
                    self.imoveis_table.setItem(row, 0, QTableWidgetItem(str(imovel['id'])))
                    self.imoveis_table.setItem(row, 1, QTableWidgetItem(imovel['numero']))
                    self.imoveis_table.setItem(row, 2, QTableWidgetItem(imovel['tipo'].capitalize()))
                    self.imoveis_table.setItem(row, 3, QTableWidgetItem(rua['nome']))
                    row += 1
    
    @Slot()
    def add_territorio(self):
        """Adiciona um novo território"""
        nome = self.territorio_nome_input.text().strip()
        descricao = self.territorio_desc_input.text().strip()
        
        if not nome:
            QMessageBox.warning(self, "Atenção", "O nome do território é obrigatório.")
            return
        
        territorio = Territorio(nome=nome, descricao=descricao)
        if territorio.save(self.db_manager):
            QMessageBox.information(self, "Sucesso", "Território adicionado com sucesso.")
            self.territorio_nome_input.clear()
            self.territorio_desc_input.clear()
            self.load_data()
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível adicionar o território.")
    
    @Slot()
    def edit_territorio(self):
        """Edita o território selecionado"""
        if not self.current_territorio:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Território")
        dialog.resize(400, 200)
        
        layout = QFormLayout(dialog)
        
        nome_input = QLineEdit(self.current_territorio.nome)
        layout.addRow("Nome:", nome_input)
        
        desc_input = QLineEdit(self.current_territorio.descricao or "")
        layout.addRow("Descrição:", desc_input)
        
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
            descricao = desc_input.text().strip()
            
            if not nome:
                QMessageBox.warning(self, "Atenção", "O nome do território é obrigatório.")
                return
            
            self.current_territorio.nome = nome
            self.current_territorio.descricao = descricao
            
            if self.current_territorio.save(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Território atualizado com sucesso.")
                self.load_data()
                
                # Atualizar título dos detalhes
                self.detail_title.setText(nome)
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível atualizar o território.")
    
    @Slot()
    def delete_territorio(self):
        """Exclui o território selecionado"""
        if not self.current_territorio:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o território '{self.current_territorio.nome}'?\n"
            f"Esta ação excluirá todas as ruas e imóveis associados.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.current_territorio.delete(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Território excluído com sucesso.")
                self.current_territorio = None
                self.current_rua = None
                self.detail_title.setText("Selecione um território")
                self.tabs.setEnabled(False)
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                self.load_data()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível excluir o território.")
    
    @Slot()
    def add_rua(self):
        """Adiciona uma nova rua ao território selecionado"""
        if not self.current_territorio:
            QMessageBox.warning(self, "Atenção", "Selecione um território primeiro.")
            return
        
        nome = self.rua_nome_input.text().strip()
        
        if not nome:
            QMessageBox.warning(self, "Atenção", "O nome da rua é obrigatório.")
            return
        
        if self.current_territorio.add_rua(self.db_manager, nome):
            QMessageBox.information(self, "Sucesso", "Rua adicionada com sucesso.")
            self.rua_nome_input.clear()
            self.update_ruas_list()
            self.update_rua_select()
            self.update_tree()
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível adicionar a rua.")
    
    @Slot()
    def edit_rua(self):
        """Edita a rua selecionada"""
        if not self.current_rua:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Rua")
        dialog.resize(400, 150)
        
        layout = QFormLayout(dialog)
        
        nome_input = QLineEdit(self.current_rua['nome'])
        layout.addRow("Nome:", nome_input)
        
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
            
            if not nome:
                QMessageBox.warning(self, "Atenção", "O nome da rua é obrigatório.")
                return
            
            cursor = self.db_manager.execute(
                "UPDATE ruas SET nome = ? WHERE id = ?",
                (nome, self.current_rua['id'])
            )
            
            if cursor:
                self.db_manager.commit()
                QMessageBox.information(self, "Sucesso", "Rua atualizada com sucesso.")
                self.update_ruas_list()
                self.update_rua_select()
                self.update_tree()
                self.update_imoveis_table()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível atualizar a rua.")
    
    @Slot()
    def delete_rua(self):
        """Exclui a rua selecionada"""
        if not self.current_rua:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a rua '{self.current_rua['nome']}'?\n"
            f"Esta ação excluirá todos os imóveis associados.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db_manager.execute(
                "DELETE FROM ruas WHERE id = ?",
                (self.current_rua['id'],)
            )
            
            if cursor:
                self.db_manager.commit()
                QMessageBox.information(self, "Sucesso", "Rua excluída com sucesso.")
                self.current_rua = None
                self.edit_rua_button.setEnabled(False)
                self.delete_rua_button.setEnabled(False)
                self.update_ruas_list()
                self.update_rua_select()
                self.update_tree()
                self.update_imoveis_table()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível excluir a rua.")
    
    @Slot()
    def add_imovel(self):
        """Adiciona um novo imóvel"""
        if self.rua_select.count() == 0:
            QMessageBox.warning(self, "Atenção", "Cadastre uma rua primeiro.")
            return
        
        rua_id = self.rua_select.currentData()
        numero = self.imovel_numero_input.text().strip()
        tipo = self.imovel_tipo_select.currentText().lower()
        
        if not numero:
            QMessageBox.warning(self, "Atenção", "O número do imóvel é obrigatório.")
            return
        
        # Se for prédio ou vila, pedir mais informações
        total_unidades = None
        tipo_portaria = None
        tipo_acesso = None
        nome = None
        observacoes = None
        
        if tipo in ('prédio', 'vila'):
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Detalhes do {'Prédio' if tipo == 'prédio' else 'Vila'}")
            dialog.resize(400, 300)
            
            layout = QFormLayout(dialog)
            
            nome_input = QLineEdit()
            nome_input.setPlaceholderText(f"Ex: {'Edifício Aurora' if tipo == 'prédio' else 'Vila das Flores'}")
            layout.addRow("Nome (opcional):", nome_input)
            
            unidades_input = QLineEdit()
            unidades_input.setPlaceholderText("Ex: 12")
            layout.addRow("Total de Unidades:", unidades_input)
            
            portaria_select = QComboBox()
            portaria_select.addItems(["24 horas", "Eletrônica", "Diurna", "Sem Portaria", "Outro"])
            layout.addRow("Tipo de Portaria:", portaria_select)
            
            acesso_select = QComboBox()
            acesso_select.addItems(["Fácil (Sem Restrições)", "Restrito (Com Autorização)", "Via Interfone", "Difícil"])
            layout.addRow("Tipo de Acesso:", acesso_select)
            
            obs_input = QTextEdit()
            obs_input.setPlaceholderText("Observações sobre o imóvel...")
            layout.addRow("Observações:", obs_input)
            
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
                nome = nome_input.text().strip() or None
                total_unidades_text = unidades_input.text().strip()
                tipo_portaria = portaria_select.currentText().lower().replace(" ", "-")
                tipo_acesso = acesso_select.currentText().split(" ")[0].lower()
                observacoes = obs_input.toPlainText().strip() or None
                
                if not total_unidades_text or not total_unidades_text.isdigit():
                    QMessageBox.warning(self, "Atenção", "O total de unidades deve ser um número válido.")
                    return
                
                total_unidades = int(total_unidades_text)
        
        # Inserir o imóvel
        cursor = self.db_manager.execute(
            "INSERT INTO imoveis (rua_id, numero, tipo, nome, total_unidades, "
            "tipo_portaria, tipo_acesso, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (rua_id, numero, tipo, nome, total_unidades, tipo_portaria, tipo_acesso, observacoes)
        )
        
        if cursor:
            self.db_manager.commit()
            
            # Se for prédio ou vila, criar as unidades automaticamente
            if tipo in ('prédio', 'vila') and total_unidades and total_unidades > 0:
                imovel_id = cursor.lastrowid
                
                unidades = []
                prefix = "Apto" if tipo == "prédio" else "Casa"
                
                for i in range(1, total_unidades + 1):
                    unidades.append((imovel_id, f"{prefix} {i:02d}", None))
                
                self.db_manager.executemany(
                    "INSERT INTO unidades (imovel_id, numero, observacoes) VALUES (?, ?, ?)",
                    unidades
                )
                self.db_manager.commit()
            
            QMessageBox.information(self, "Sucesso", "Imóvel adicionado com sucesso.")
            self.imovel_numero_input.clear()
            self.update_imoveis_table()
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível adicionar o imóvel.")
    
    @Slot()
    def edit_imovel(self):
        """Edita o imóvel selecionado"""
        selected_rows = self.imoveis_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        imovel_id = int(self.imoveis_table.item(row, 0).text())
        
        # Buscar dados do imóvel
        cursor = self.db_manager.execute(
            "SELECT * FROM imoveis WHERE id = ?", 
            (imovel_id,)
        )
        if not cursor:
            QMessageBox.critical(self, "Erro", "Não foi possível carregar os dados do imóvel.")
            return
        
        imovel = cursor.fetchone()
        if not imovel:
            QMessageBox.critical(self, "Erro", "Imóvel não encontrado.")
            return
        
        # Dialog para edição
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Imóvel")
        dialog.resize(400, 300)
        
        layout = QFormLayout(dialog)
        
        # Combobox de ruas
        rua_select = QComboBox()
        for rua in self.current_territorio.get_ruas(self.db_manager):
            rua_select.addItem(rua['nome'], rua['id'])
            if rua['id'] == imovel['rua_id']:
                rua_select.setCurrentText(rua['nome'])
        layout.addRow("Rua:", rua_select)
        
        # Número do imóvel
        numero_input = QLineEdit(imovel['numero'])
        layout.addRow("Número:", numero_input)
        
        # Tipo de imóvel
        tipo_select = QComboBox()
        tipos = ["Residencial", "Comercial", "Prédio", "Vila"]
        tipo_select.addItems(tipos)
        tipo_select.setCurrentText(imovel['tipo'].capitalize())
        layout.addRow("Tipo:", tipo_select)
        
        # Campos extras para prédios e vilas
        nome_input = QLineEdit(imovel['nome'] or "")
        layout.addRow("Nome (opcional):", nome_input)
        
        unidades_input = QLineEdit(str(imovel['total_unidades']) if imovel['total_unidades'] else "")
        layout.addRow("Total de Unidades:", unidades_input)
        
        portaria_select = QComboBox()
        portarias = ["24 horas", "Eletrônica", "Diurna", "Sem Portaria", "Outro"]
        portaria_select.addItems(portarias)
        if imovel['tipo_portaria']:
            portaria_text = imovel['tipo_portaria'].replace("-", " ").capitalize()
            for i, p in enumerate(portarias):
                if p.lower() == portaria_text.lower():
                    portaria_select.setCurrentIndex(i)
                    break
        layout.addRow("Tipo de Portaria:", portaria_select)
        
        acesso_select = QComboBox()
        acessos = ["Fácil (Sem Restrições)", "Restrito (Com Autorização)", "Via Interfone", "Difícil"]
        acesso_select.addItems(acessos)
        if imovel['tipo_acesso']:
            for i, a in enumerate(acessos):
                if a.lower().startswith(imovel['tipo_acesso'].lower()):
                    acesso_select.setCurrentIndex(i)
                    break
        layout.addRow("Tipo de Acesso:", acesso_select)
        
        obs_input = QTextEdit(imovel['observacoes'] or "")
        layout.addRow("Observações:", obs_input)
        
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
            rua_id = rua_select.currentData()
            numero = numero_input.text().strip()
            tipo = tipo_select.currentText().lower()
            nome = nome_input.text().strip() or None
            total_unidades_text = unidades_input.text().strip()
            tipo_portaria = portaria_select.currentText().lower().replace(" ", "-")
            tipo_acesso = acesso_select.currentText().split(" ")[0].lower()
            observacoes = obs_input.toPlainText().strip() or None
            
            # Validações
            if not numero:
                QMessageBox.warning(self, "Atenção", "O número do imóvel é obrigatório.")
                return
            
            total_unidades = None
            if tipo in ('prédio', 'vila'):
                if not total_unidades_text or not total_unidades_text.isdigit():
                    QMessageBox.warning(self, "Atenção", "O total de unidades deve ser um número válido.")
                    return
                total_unidades = int(total_unidades_text)
            
            # Atualizar o imóvel
            cursor = self.db_manager.execute(
                "UPDATE imoveis SET rua_id = ?, numero = ?, tipo = ?, nome = ?, "
                "total_unidades = ?, tipo_portaria = ?, tipo_acesso = ?, observacoes = ? "
                "WHERE id = ?",
                (rua_id, numero, tipo, nome, total_unidades, tipo_portaria, 
                 tipo_acesso, observacoes, imovel_id)
            )
            
            if cursor:
                self.db_manager.commit()
                QMessageBox.information(self, "Sucesso", "Imóvel atualizado com sucesso.")
                self.update_imoveis_table()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível atualizar o imóvel.")
    
    @Slot()
    def delete_imovel(self):
        """Exclui o imóvel selecionado"""
        selected_rows = self.imoveis_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        imovel_id = int(self.imoveis_table.item(row, 0).text())
        numero = self.imoveis_table.item(row, 1).text()
        tipo = self.imoveis_table.item(row, 2).text()
        
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o imóvel Nº {numero} ({tipo})?\n"
            f"Esta ação excluirá todos os dados associados a este imóvel.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db_manager.execute(
                "DELETE FROM imoveis WHERE id = ?",
                (imovel_id,)
            )
            
            if cursor:
                self.db_manager.commit()
                QMessageBox.information(self, "Sucesso", "Imóvel excluído com sucesso.")
                self.edit_imovel_button.setEnabled(False)
                self.delete_imovel_button.setEnabled(False)
                self.update_imoveis_table()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível excluir o imóvel.")
    
    @Slot(QTreeWidgetItem, int)
    def on_item_clicked(self, item, column):
        """Ao clicar em um item da árvore"""
        parent = item.parent()
        
        if parent is None:
            # Item é um território
            territorio_id = item.data(0, Qt.ItemDataRole.UserRole)
            self.current_territorio = Territorio.get_by_id(self.db_manager, territorio_id)
            self.current_rua = None
            
            if self.current_territorio:
                self.detail_title.setText(self.current_territorio.nome)
                self.tabs.setEnabled(True)
                self.edit_button.setEnabled(True)
                self.delete_button.setEnabled(True)
                
                # Atualizar dados das ruas
                self.update_ruas_list()
                self.update_rua_select()
                self.update_imoveis_table()
                
                # Resetar seleção de rua
                self.edit_rua_button.setEnabled(False)
                self.delete_rua_button.setEnabled(False)
                
                # Mostrar aba de ruas
                self.tabs.setCurrentIndex(0)
        else:
            # Item é uma rua
            rua_id = item.data(0, Qt.ItemDataRole.UserRole)
            territorio_id = parent.data(0, Qt.ItemDataRole.UserRole)
            
            # Recuperar o território
            self.current_territorio = Territorio.get_by_id(self.db_manager, territorio_id)
            
            if self.current_territorio:
                # Recuperar a rua
                cursor = self.db_manager.execute(
                    "SELECT * FROM ruas WHERE id = ?",
                    (rua_id,)
                )
                if cursor:
                    self.current_rua = cursor.fetchone()
                
                self.detail_title.setText(f"{self.current_territorio.nome} - {item.text(0)}")
                self.tabs.setEnabled(True)
                self.edit_button.setEnabled(True)
                self.delete_button.setEnabled(True)
                
                # Atualizar dados das ruas
                self.update_ruas_list()
                self.update_rua_select()
                self.update_imoveis_table()
                
                # Selecionar a rua na lista
                for i in range(self.ruas_list.count()):
                    list_item = self.ruas_list.item(i)
                    if list_item.data(Qt.ItemDataRole.UserRole) == rua_id:
                        self.ruas_list.setCurrentItem(list_item)
                        break
                
                # Mostrar aba de imóveis
                self.tabs.setCurrentIndex(1)
                
                # Selecionar a rua no combo de imóveis
                for i in range(self.rua_select.count()):
                    if self.rua_select.itemData(i) == rua_id:
                        self.rua_select.setCurrentIndex(i)
                        break
    
    @Slot(QListWidgetItem)
    def on_rua_clicked(self, item):
        """Ao clicar em uma rua na lista"""
        if not item:
            return
        
        rua_id = item.data(Qt.ItemDataRole.UserRole)
        
        # Recuperar a rua
        cursor = self.db_manager.execute(
            "SELECT * FROM ruas WHERE id = ?",
            (rua_id,)
        )
        if cursor:
            self.current_rua = cursor.fetchone()
            self.edit_rua_button.setEnabled(True)
            self.delete_rua_button.setEnabled(True)
    
    @Slot()
    def on_imovel_clicked(self):
        """Ao clicar em um imóvel na tabela"""
        selected_rows = self.imoveis_table.selectedItems()
        if selected_rows:
            self.edit_imovel_button.setEnabled(True)
            self.delete_imovel_button.setEnabled(True)
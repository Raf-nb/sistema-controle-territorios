#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QPushButton, QLineEdit, QComboBox,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QMessageBox, QDialog, QFormLayout, QTextEdit,
                              QTreeWidget, QTreeWidgetItem, QSplitter, QFrame,
                              QStackedWidget, QTabWidget, QListWidget, QListWidgetItem,
                              QCheckBox, QProgressBar, QDateEdit)
from PySide6.QtCore import Qt, Signal, Slot, QDate
from PySide6.QtGui import QIcon, QFont, QColor

from models.territorio import Territorio
from models.atendimento import Atendimento

from datetime import datetime

class ViewTerritoriosWidget(QWidget):
    """Widget para visualização e controle de atendimentos em territórios"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.territorios = []
        self.atendimentos = {}
        self.current_territorio = None
        self.current_imovel = None
        self.filtro_residencial = True
        self.filtro_comercial = True
        self.filtro_atendidos = False
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        main_layout = QVBoxLayout(self)
        
        # Título da página
        title_label = QLabel("Controle de Atendimentos")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Filtros
        filtros_group = QGroupBox("Filtros")
        filtros_group.setStyleSheet("QGroupBox { background-color: #f8f9fa; }")
        filtros_layout = QHBoxLayout(filtros_group)
        
        self.cb_residencial = QCheckBox("Mostrar Residenciais")
        self.cb_residencial.setChecked(True)
        self.cb_residencial.stateChanged.connect(self.on_filtro_changed)
        filtros_layout.addWidget(self.cb_residencial)
        
        self.cb_comercial = QCheckBox("Mostrar Comerciais")
        self.cb_comercial.setChecked(True)
        self.cb_comercial.stateChanged.connect(self.on_filtro_changed)
        filtros_layout.addWidget(self.cb_comercial)
        
        self.cb_atendidos = QCheckBox("Apenas Não Atendidos")
        self.cb_atendidos.stateChanged.connect(self.on_filtro_changed)
        filtros_layout.addWidget(self.cb_atendidos)
        
        main_layout.addWidget(filtros_group)
        
        # Barra de progresso
        progresso_layout = QHBoxLayout()
        progresso_layout.addWidget(QLabel("Progresso de Atendimentos:"))
        self.progresso_bar = QProgressBar()
        self.progresso_bar.setRange(0, 100)
        self.progresso_bar.setTextVisible(True)
        progresso_layout.addWidget(self.progresso_bar)
        
        main_layout.addLayout(progresso_layout)
        
        # Splitter para dividir a árvore de territórios e os detalhes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Painel esquerdo: Árvore de territórios
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Árvore de territórios
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Territórios"])
        self.tree.itemClicked.connect(self.on_item_clicked)
        left_layout.addWidget(self.tree)
        
        # Painel direito: Lista de imóveis
        right_panel = QWidget()
        self.right_layout = QVBoxLayout(right_panel)
        
        # Título do território selecionado
        self.detail_title = QLabel("Selecione um território")
        self.detail_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.right_layout.addWidget(self.detail_title)
        
        # Lista de imóveis
        self.imoveis_list = QListWidget()
        self.imoveis_list.itemClicked.connect(self.on_imovel_clicked)
        self.right_layout.addWidget(self.imoveis_list)
        
        # Botões para registrar atendimento
        buttons_layout = QHBoxLayout()
        
        self.registrar_button = QPushButton("Registrar Atendimento")
        self.registrar_button.setEnabled(False)
        self.registrar_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.registrar_button.clicked.connect(self.registrar_atendimento)
        buttons_layout.addWidget(self.registrar_button)
        
        self.remover_button = QPushButton("Remover Atendimento")
        self.remover_button.setEnabled(False)
        self.remover_button.setStyleSheet("background-color: #f44336; color: white;")
        self.remover_button.clicked.connect(self.remover_atendimento)
        buttons_layout.addWidget(self.remover_button)
        
        self.right_layout.addLayout(buttons_layout)
        
        # Adicionar os painéis ao splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])
    
    def load_data(self):
        """Carrega os dados dos territórios e atendimentos"""
        self.territorios = Territorio.get_all(self.db_manager)
        self.carregar_atendimentos()
        self.update_tree()
        self.atualizar_progresso()
    
    def carregar_atendimentos(self):
        """Carrega os atendimentos do banco de dados"""
        self.atendimentos = {}
        
        cursor = self.db_manager.execute(
            "SELECT imovel_id, id, data, observacoes FROM atendimentos WHERE unidade_id IS NULL"
        )
        
        if cursor:
            for row in cursor.fetchall():
                self.atendimentos[row['imovel_id']] = {
                    'id': row['id'],
                    'data': row['data'],
                    'observacoes': row['observacoes']
                }
    
    def update_tree(self):
        """Atualiza a árvore de territórios"""
        self.tree.clear()
        
        for territorio in self.territorios:
            # Verificar se o território tem imóveis residenciais ou comerciais após a filtragem
            tem_imoveis_validos = False
            ruas = territorio.get_ruas(self.db_manager)
            
            for rua in ruas:
                cursor = self.db_manager.execute(
                    "SELECT COUNT(*) as total FROM imoveis "
                    "WHERE rua_id = ? AND tipo IN ('residencial', 'comercial')",
                    (rua['id'],)
                )
                if cursor and cursor.fetchone()['total'] > 0:
                    tem_imoveis_validos = True
                    break
            
            if tem_imoveis_validos:
                item = QTreeWidgetItem(self.tree)
                item.setText(0, territorio.nome)
                item.setData(0, Qt.ItemDataRole.UserRole, territorio.id)
                
                # Adicionar ruas como filhos
                for rua in ruas:
                    rua_item = QTreeWidgetItem(item)
                    rua_item.setText(0, rua['nome'])
                    rua_item.setData(0, Qt.ItemDataRole.UserRole, rua['id'])
        
        self.tree.expandAll()
    
    def atualizar_progresso(self):
        """Atualiza a barra de progresso de atendimentos"""
        total_imoveis = 0
        atendidos = 0
        
        for territorio in self.territorios:
            ruas = territorio.get_ruas(self.db_manager)
            for rua in ruas:
                cursor = self.db_manager.execute(
                    "SELECT id, tipo FROM imoveis WHERE rua_id = ? AND tipo IN ('residencial', 'comercial')",
                    (rua['id'],)
                )
                if cursor:
                    for imovel in cursor.fetchall():
                        filtro_tipo = (imovel['tipo'] == 'residencial' and self.filtro_residencial) or \
                                     (imovel['tipo'] == 'comercial' and self.filtro_comercial)
                        
                        if filtro_tipo:
                            total_imoveis += 1
                            if imovel['id'] in self.atendimentos:
                                atendidos += 1
        
        if total_imoveis > 0:
            percentual = int((atendidos / total_imoveis) * 100)
            self.progresso_bar.setValue(percentual)
            self.progresso_bar.setFormat(f"{percentual}% ({atendidos}/{total_imoveis})")
        else:
            self.progresso_bar.setValue(0)
            self.progresso_bar.setFormat("0% (0/0)")
    
    def update_imoveis_list(self, rua_id=None, territorio_id=None):
        """Atualiza a lista de imóveis de acordo com os filtros"""
        self.imoveis_list.clear()
        self.current_imovel = None
        self.registrar_button.setEnabled(False)
        self.remover_button.setEnabled(False)
        
        if not rua_id and not territorio_id:
            return
        
        # Query base
        query = "SELECT i.id, i.numero, i.tipo, r.nome as rua_nome, t.nome as territorio_nome "
        query += "FROM imoveis i "
        query += "JOIN ruas r ON i.rua_id = r.id "
        query += "JOIN territorios t ON r.territorio_id = t.id "
        query += "WHERE i.tipo IN ('residencial', 'comercial') "
        
        params = []
        
        # Filtro por rua ou território
        if rua_id:
            query += "AND i.rua_id = ? "
            params.append(rua_id)
        elif territorio_id:
            query += "AND t.id = ? "
            params.append(territorio_id)
        
        # Filtro por tipo de imóvel
        tipos = []
        if self.filtro_residencial:
            tipos.append("'residencial'")
        if self.filtro_comercial:
            tipos.append("'comercial'")
        
        if tipos:
            query += f"AND i.tipo IN ({','.join(tipos)}) "
        
        # Ordem
        query += "ORDER BY r.nome, i.numero"
        
        cursor = self.db_manager.execute(query, params)
        if not cursor:
            return
        
        imoveis = cursor.fetchall()
        
        # Filtrar por atendimento se necessário
        if self.filtro_atendidos:
            imoveis = [i for i in imoveis if i['id'] not in self.atendimentos]
        
        # Preencher a lista
        for imovel in imoveis:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, imovel['id'])
            
            # Texto do item
            texto = f"Nº {imovel['numero']} - {imovel['tipo'].capitalize()}"
            if imovel['id'] in self.atendimentos:
                data_formatada = self.formatar_data(self.atendimentos[imovel['id']]['data'])
                texto += f" [Atendido em {data_formatada}]"
                item.setBackground(QColor("#d4edda"))  # Verde claro para atendidos
            
            item.setText(texto)
            self.imoveis_list.addItem(item)
    
    def formatar_data(self, data_str):
        """Formata a data para exibição"""
        try:
            return QDate.fromString(data_str, "yyyy-MM-dd").toString("dd/MM/yyyy")
        except:
            return data_str
    
    @Slot(QTreeWidgetItem, int)
    def on_item_clicked(self, item, column):
        """Ao clicar em um item da árvore"""
        parent = item.parent()
        
        if parent is None:
            # Item é um território
            territorio_id = item.data(0, Qt.ItemDataRole.UserRole)
            self.current_territorio = Territorio.get_by_id(self.db_manager, territorio_id)
            
            if self.current_territorio:
                self.detail_title.setText(f"Território: {self.current_territorio.nome}")
                self.update_imoveis_list(territorio_id=territorio_id)
        else:
            # Item é uma rua
            rua_id = item.data(0, Qt.ItemDataRole.UserRole)
            territorio_id = parent.data(0, Qt.ItemDataRole.UserRole)
            
            # Recuperar o território
            self.current_territorio = Territorio.get_by_id(self.db_manager, territorio_id)
            
            if self.current_territorio:
                self.detail_title.setText(f"Rua: {item.text(0)} - {self.current_territorio.nome}")
                self.update_imoveis_list(rua_id=rua_id)
    
    @Slot(QListWidgetItem)
    def on_imovel_clicked(self, item):
        """Ao clicar em um imóvel da lista"""
        if not item:
            return
        
        imovel_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_imovel = imovel_id
        
        # Verificar se o imóvel já foi atendido
        atendido = imovel_id in self.atendimentos
        
        # Habilitar botões apropriados
        self.registrar_button.setEnabled(True)
        self.remover_button.setEnabled(atendido)
    
    @Slot()
    def on_filtro_changed(self):
        """Ao alterar os filtros"""
        self.filtro_residencial = self.cb_residencial.isChecked()
        self.filtro_comercial = self.cb_comercial.isChecked()
        self.filtro_atendidos = self.cb_atendidos.isChecked()
        
        # Atualizar a lista e a barra de progresso
        if self.current_territorio:
            selected_items = self.tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                parent = item.parent()
                
                if parent is None:
                    # Item é um território
                    self.update_imoveis_list(territorio_id=self.current_territorio.id)
                else:
                    # Item é uma rua
                    rua_id = item.data(0, Qt.ItemDataRole.UserRole)
                    self.update_imoveis_list(rua_id=rua_id)
        
        self.atualizar_progresso()
    
    @Slot()
    def registrar_atendimento(self):
        """Registra um atendimento para o imóvel selecionado"""
        if not self.current_imovel:
            return
        
        # Buscar dados do imóvel
        cursor = self.db_manager.execute(
            "SELECT i.numero, i.tipo, r.nome as rua_nome "
            "FROM imoveis i "
            "JOIN ruas r ON i.rua_id = r.id "
            "WHERE i.id = ?",
            (self.current_imovel,)
        )
        
        if not cursor:
            QMessageBox.critical(self, "Erro", "Não foi possível carregar os dados do imóvel.")
            return
        
        imovel = cursor.fetchone()
        if not imovel:
            QMessageBox.critical(self, "Erro", "Imóvel não encontrado.")
            return
        
        # Verificar se já existe um atendimento
        atendimento_existente = self.current_imovel in self.atendimentos
        
        # Criar diálogo para registrar atendimento
        dialog = QDialog(self)
        dialog.setWindowTitle("Registrar Atendimento")
        dialog.resize(400, 300)
        
        layout = QFormLayout(dialog)
        
        # Informações do imóvel
        info_label = QLabel(f"Nº {imovel['numero']} ({imovel['tipo'].capitalize()}) - {imovel['rua_nome']}")
        layout.addRow("Imóvel:", info_label)
        
        # Data do atendimento
        data_edit = QDateEdit(QDate.currentDate())
        data_edit.setCalendarPopup(True)
        data_edit.setDisplayFormat("dd/MM/yyyy")
        data_edit.setDate(QDate.currentDate())
        layout.addRow("Data do Atendimento:", data_edit)
        
        # Observações
        obs_edit = QTextEdit()
        obs_edit.setPlaceholderText("Observações sobre o atendimento...")
        
        if atendimento_existente:
            data_edit.setDate(QDate.fromString(self.atendimentos[self.current_imovel]['data'], "yyyy-MM-dd"))
            obs_edit.setText(self.atendimentos[self.current_imovel]['observacoes'] or "")
        
        layout.addRow("Observações (opcional):", obs_edit)
        
        # Botões
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = QPushButton("Confirmar Atendimento")
        save_button.setStyleSheet("background-color: #4CAF50; color: white;")
        save_button.clicked.connect(dialog.accept)
        
        remove_button = None
        if atendimento_existente:
            remove_button = QPushButton("Remover Atendimento")
            remove_button.setStyleSheet("background-color: #f44336; color: white;")
            
            def on_remove():
                dialog.done(2)  # Código personalizado para remover
            
            remove_button.clicked.connect(on_remove)
        
        buttons_layout.addWidget(cancel_button)
        if remove_button:
            buttons_layout.addWidget(remove_button)
        buttons_layout.addWidget(save_button)
        
        layout.addRow("", buttons_layout)
        
        result = dialog.exec()
        if result == 1:  # QDialog.Accepted
            # Salvar o atendimento
            data = data_edit.date().toString("yyyy-MM-dd")
            observacoes = obs_edit.toPlainText().strip() or None
            
            if atendimento_existente:
                # Atualizar atendimento existente
                atendimento_id = self.atendimentos[self.current_imovel]['id']
                cursor = self.db_manager.execute(
                    "UPDATE atendimentos SET data = ?, observacoes = ? WHERE id = ?",
                    (data, observacoes, atendimento_id)
                )
            else:
                # Criar novo atendimento
                cursor = self.db_manager.execute(
                    "INSERT INTO atendimentos (imovel_id, data, observacoes) VALUES (?, ?, ?)",
                    (self.current_imovel, data, observacoes)
                )
            
            if cursor:
                self.db_manager.commit()
                QMessageBox.information(self, "Sucesso", "Atendimento registrado com sucesso.")
                self.carregar_atendimentos()
                
                # Atualizar a lista e botões
                selected_items = self.tree.selectedItems()
                if selected_items:
                    item = selected_items[0]
                    parent = item.parent()
                    
                    if parent is None:
                        # Item é um território
                        self.update_imoveis_list(territorio_id=self.current_territorio.id)
                    else:
                        # Item é uma rua
                        rua_id = item.data(0, Qt.ItemDataRole.UserRole)
                        self.update_imoveis_list(rua_id=rua_id)
                
                self.atualizar_progresso()
                self.remover_button.setEnabled(True)
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível registrar o atendimento.")
        
        elif result == 2:  # Código para remover atendimento
            self.remover_atendimento()
    
    @Slot()
    def remover_atendimento(self):
        """Remove o atendimento do imóvel selecionado"""
        if not self.current_imovel or self.current_imovel not in self.atendimentos:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar Remoção",
            "Tem certeza que deseja remover o atendimento registrado para este imóvel?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            atendimento_id = self.atendimentos[self.current_imovel]['id']
            
            cursor = self.db_manager.execute(
                "DELETE FROM atendimentos WHERE id = ?",
                (atendimento_id,)
            )
            
            if cursor:
                self.db_manager.commit()
                QMessageBox.information(self, "Sucesso", "Atendimento removido com sucesso.")
                self.carregar_atendimentos()
                
                # Atualizar a lista e botões
                selected_items = self.tree.selectedItems()
                if selected_items:
                    item = selected_items[0]
                    parent = item.parent()
                    
                    if parent is None:
                        # Item é um território
                        self.update_imoveis_list(territorio_id=self.current_territorio.id)
                    else:
                        # Item é uma rua
                        rua_id = item.data(0, Qt.ItemDataRole.UserRole)
                        self.update_imoveis_list(rua_id=rua_id)
                
                self.atualizar_progresso()
                self.remover_button.setEnabled(False)
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível remover o atendimento.")
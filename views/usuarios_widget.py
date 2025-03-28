#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QPushButton, QLineEdit, QComboBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QDialog, QFormLayout, QTabWidget,
                             QCheckBox)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QFont

from models.usuario import Usuario, LogAtividade

class UsuariosWidget(QWidget):
    """Widget para gerenciamento de usuários"""
    
    def __init__(self, db_manager, usuario_atual):
        super().__init__()
        self.db_manager = db_manager
        self.usuario_atual = usuario_atual
        self.usuarios = []
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        main_layout = QVBoxLayout(self)
        
        # Título da página
        title_label = QLabel("Gerenciamento de Usuários")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Tabs para diferentes seções
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Tab para lista de usuários
        usuarios_tab = QWidget()
        self.tabs.addTab(usuarios_tab, "Usuários")
        
        # Tab para registro de atividades
        log_tab = QWidget()
        self.tabs.addTab(log_tab, "Registro de Atividades")
        
        # === Tab de Usuários ===
        usuarios_layout = QVBoxLayout(usuarios_tab)
        
        # Formulário para adicionar usuário
        form_group = QGroupBox("Adicionar Novo Usuário")
        form_layout = QFormLayout(form_group)
        
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome completo")
        form_layout.addRow("Nome:", self.nome_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("exemplo@email.com")
        form_layout.addRow("Email:", self.email_input)
        
        self.senha_input = QLineEdit()
        self.senha_input.setPlaceholderText("Senha")
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Senha:", self.senha_input)
        
        self.confirmar_senha_input = QLineEdit()
        self.confirmar_senha_input.setPlaceholderText("Confirme a senha")
        self.confirmar_senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Confirmar Senha:", self.confirmar_senha_input)
        
        self.nivel_input = QComboBox()
        self.nivel_input.addItem("Básico (Apenas registrar atendimentos)", Usuario.NIVEL_BASICO)
        self.nivel_input.addItem("Gestor (Gerenciar territórios e designações)", Usuario.NIVEL_GESTOR)
        self.nivel_input.addItem("Administrador (Acesso total)", Usuario.NIVEL_ADMIN)
        form_layout.addRow("Nível de Permissão:", self.nivel_input)
        
        self.ativo_checkbox = QCheckBox("Usuário ativo")
        self.ativo_checkbox.setChecked(True)
        form_layout.addRow("Status:", self.ativo_checkbox)
        
        add_button = QPushButton("Adicionar Usuário")
        add_button.setStyleSheet("background-color: #4CAF50; color: white;")
        add_button.clicked.connect(self.add_usuario)
        form_layout.addRow("", add_button)
        
        usuarios_layout.addWidget(form_group)
        
        # Tabela de usuários
        usuarios_layout.addWidget(QLabel("Usuários Cadastrados"))
        
        self.table = QTableWidget(0, 5)  # ID, Nome, Email, Nível, Ativo
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Email", "Nível", "Ativo"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setColumnHidden(0, True)  # Esconder coluna ID
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        usuarios_layout.addWidget(self.table)
        
        # Botões para gerenciar usuários
        buttons_layout = QHBoxLayout()
        
        self.editar_button = QPushButton("Editar")
        self.editar_button.setEnabled(False)
        self.editar_button.clicked.connect(self.edit_usuario)
        buttons_layout.addWidget(self.editar_button)
        
        self.resetar_senha_button = QPushButton("Resetar Senha")
        self.resetar_senha_button.setEnabled(False)
        self.resetar_senha_button.clicked.connect(self.reset_senha)
        buttons_layout.addWidget(self.resetar_senha_button)
        
        self.ativar_desativar_button = QPushButton("Ativar/Desativar")
        self.ativar_desativar_button.setEnabled(False)
        self.ativar_desativar_button.clicked.connect(self.toggle_ativo)
        buttons_layout.addWidget(self.ativar_desativar_button)
        
        self.excluir_button = QPushButton("Excluir")
        self.excluir_button.setEnabled(False)
        self.excluir_button.setStyleSheet("background-color: #f44336; color: white;")
        self.excluir_button.clicked.connect(self.delete_usuario)
        buttons_layout.addWidget(self.excluir_button)
        
        usuarios_layout.addLayout(buttons_layout)
        
        # === Tab de Registro de Atividades ===
        log_layout = QVBoxLayout(log_tab)
        
        # Tabela de atividades
        self.log_table = QTableWidget(0, 5)  # ID, Usuário, Ação, Descrição, Data/Hora
        self.log_table.setHorizontalHeaderLabels(["ID", "Usuário", "Ação", "Descrição", "Data/Hora"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.log_table.setColumnHidden(0, True)  # Esconder coluna ID
        self.log_table.verticalHeader().setVisible(False)
        log_layout.addWidget(self.log_table)
        
        # Botão para atualizar logs
        refresh_log_button = QPushButton("Atualizar Registros")
        refresh_log_button.clicked.connect(self.load_logs)
        log_layout.addWidget(refresh_log_button)
    
    def load_data(self):
        """Carrega os dados dos usuários"""
        self.usuarios = Usuario.get_all(self.db_manager)
        self.update_table()
        self.load_logs()
    
    def update_table(self):
        """Atualiza a tabela de usuários"""
        self.table.setRowCount(0)
        
        for row, usuario in enumerate(self.usuarios):
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(usuario.id)))
            self.table.setItem(row, 1, QTableWidgetItem(usuario.nome))
            self.table.setItem(row, 2, QTableWidgetItem(usuario.email))
            
            # Nível de permissão
            nivel_texto = "Básico"
            if usuario.nivel_permissao == Usuario.NIVEL_GESTOR:
                nivel_texto = "Gestor"
            elif usuario.nivel_permissao == Usuario.NIVEL_ADMIN:
                nivel_texto = "Administrador"
            
            self.table.setItem(row, 3, QTableWidgetItem(nivel_texto))
            
            # Status ativo
            status_item = QTableWidgetItem("Sim" if usuario.ativo else "Não")
            self.table.setItem(row, 4, status_item)
    
    def load_logs(self):
        """Carrega os registros de atividades"""
        from models.usuario import LogAtividade
        
        logs = LogAtividade.get_all(self.db_manager)
        self.log_table.setRowCount(0)
        
        for row, log in enumerate(logs):
            self.log_table.insertRow(row)
            
            self.log_table.setItem(row, 0, QTableWidgetItem(str(log.id)))
            
            # Buscar nome do usuário
            usuario = Usuario.get_by_id(self.db_manager, log.usuario_id)
            nome_usuario = usuario.nome if usuario else "Usuário Desconhecido"
            self.log_table.setItem(row, 1, QTableWidgetItem(nome_usuario))
            
            # Ação
            acao_item = QTableWidgetItem(log.tipo_acao.capitalize())
            self.log_table.setItem(row, 2, acao_item)
            
            # Descrição
            self.log_table.setItem(row, 3, QTableWidgetItem(log.descricao))
            
            # Data/Hora
            self.log_table.setItem(row, 4, QTableWidgetItem(log.data_hora))
    
    @Slot()
    def add_usuario(self):
        """Adiciona um novo usuário"""
        nome = self.nome_input.text().strip()
        email = self.email_input.text().strip()
        senha = self.senha_input.text()
        confirmar_senha = self.confirmar_senha_input.text()
        nivel_permissao = self.nivel_input.currentData()
        ativo = self.ativo_checkbox.isChecked()
        
        # Validações
        if not nome or not email or not senha:
            QMessageBox.warning(self, "Atenção", "Por favor, preencha todos os campos obrigatórios.")
            return
        
        if senha != confirmar_senha:
            QMessageBox.warning(self, "Atenção", "As senhas não coincidem.")
            return
        
        # Verificar se o email já existe
        if Usuario.get_by_email(self.db_manager, email):
            QMessageBox.warning(self, "Atenção", "Já existe um usuário com este email.")
            return
        
        # Criar o usuário
        usuario = Usuario(
            nome=nome,
            email=email,
            nivel_permissao=nivel_permissao,
            ativo=ativo
        )
        usuario.definir_senha(senha)
        
        if usuario.save(self.db_manager):
            QMessageBox.information(self, "Sucesso", "Usuário adicionado com sucesso.")
            
            # Registrar atividade
            LogAtividade.registrar(
                self.db_manager,
                self.usuario_atual.id,
                LogAtividade.ACAO_CRIAR,
                f"Criou usuário: {nome} ({email})",
                "usuario",
                usuario.id
            )
            
            # Limpar campos e atualizar tabela
            self.nome_input.clear()
            self.email_input.clear()
            self.senha_input.clear()
            self.confirmar_senha_input.clear()
            self.nivel_input.setCurrentIndex(0)
            self.ativo_checkbox.setChecked(True)
            self.load_data()
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível adicionar o usuário.")
    
    @Slot()
    def edit_usuario(self):
        """Edita o usuário selecionado"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        usuario_id = int(self.table.item(row, 0).text())
        
        # Buscar o usuário pelo ID
        usuario = None
        for u in self.usuarios:
            if u.id == usuario_id:
                usuario = u
                break
        
        if not usuario:
            QMessageBox.critical(self, "Erro", "Usuário não encontrado.")
            return
        
        # Impedir edição do próprio usuário (exceto senha)
        if usuario.id == self.usuario_atual.id:
            QMessageBox.warning(
                self, 
                "Atenção", 
                "Você não pode editar seu próprio usuário aqui.\n"
                "Use a opção de Perfil para atualizar seus dados."
            )
            return
        
        # Criar diálogo para edição
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Usuário")
        dialog.resize(400, 250)
        
        layout = QFormLayout(dialog)
        
        nome_input = QLineEdit(usuario.nome)
        layout.addRow("Nome:", nome_input)
        
        email_input = QLineEdit(usuario.email)
        layout.addRow("Email:", email_input)
        
        nivel_select = QComboBox()
        nivel_select.addItem("Básico (Apenas registrar atendimentos)", Usuario.NIVEL_BASICO)
        nivel_select.addItem("Gestor (Gerenciar territórios e designações)", Usuario.NIVEL_GESTOR)
        nivel_select.addItem("Administrador (Acesso total)", Usuario.NIVEL_ADMIN)
        
        # Selecionar o nível atual
        for i in range(nivel_select.count()):
            if nivel_select.itemData(i) == usuario.nivel_permissao:
                nivel_select.setCurrentIndex(i)
                break
        
        layout.addRow("Nível de Permissão:", nivel_select)
        
        ativo_checkbox = QCheckBox("Usuário ativo")
        ativo_checkbox.setChecked(usuario.ativo)
        layout.addRow("Status:", ativo_checkbox)
        
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
            email = email_input.text().strip()
            nivel_permissao = nivel_select.currentData()
            ativo = ativo_checkbox.isChecked()
            
            # Validações
            if not nome or not email:
                QMessageBox.warning(self, "Atenção", "Por favor, preencha todos os campos obrigatórios.")
                return
            
            # Verificar se mudou o email e se já existe
            if email != usuario.email and Usuario.get_by_email(self.db_manager, email):
                QMessageBox.warning(self, "Atenção", "Já existe um usuário com este email.")
                return
            
            # Atualizar os dados
            usuario.nome = nome
            usuario.email = email
            usuario.nivel_permissao = nivel_permissao
            usuario.ativo = ativo
            
            if usuario.save(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Usuário atualizado com sucesso.")
                
                # Registrar atividade
                LogAtividade.registrar(
                    self.db_manager,
                    self.usuario_atual.id,
                    LogAtividade.ACAO_EDITAR,
                    f"Editou usuário: {nome} ({email})",
                    "usuario",
                    usuario.id
                )
                
                # Atualizar tabela
                self.load_data()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível atualizar o usuário.")
    
    @Slot()
    def reset_senha(self):
        """Redefine a senha do usuário selecionado"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        usuario_id = int(self.table.item(row, 0).text())
        nome_usuario = self.table.item(row, 1).text()
        
        # Buscar o usuário pelo ID
        usuario = None
        for u in self.usuarios:
            if u.id == usuario_id:
                usuario = u
                break
        
        if not usuario:
            QMessageBox.critical(self, "Erro", "Usuário não encontrado.")
            return
        
        # Pedir a nova senha
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Redefinir Senha - {nome_usuario}")
        dialog.resize(400, 150)
        
        layout = QFormLayout(dialog)
        
        senha_input = QLineEdit()
        senha_input.setPlaceholderText("Nova senha")
        senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Nova Senha:", senha_input)
        
        confirmar_senha_input = QLineEdit()
        confirmar_senha_input.setPlaceholderText("Confirme a nova senha")
        confirmar_senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Confirmar Senha:", confirmar_senha_input)
        
        # Botões
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = QPushButton("Redefinir Senha")
        save_button.setStyleSheet("background-color: #4CAF50; color: white;")
        save_button.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        layout.addRow("", buttons_layout)
        
        if dialog.exec():
            senha = senha_input.text()
            confirmar_senha = confirmar_senha_input.text()
            
            # Validações
            if not senha:
                QMessageBox.warning(self, "Atenção", "Por favor, preencha a nova senha.")
                return
            
            if senha != confirmar_senha:
                QMessageBox.warning(self, "Atenção", "As senhas não coincidem.")
                return
            
            # Atualizar a senha
            usuario.definir_senha(senha)
            
            if usuario.save(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Senha redefinida com sucesso.")
                
                # Registrar atividade
                LogAtividade.registrar(
                    self.db_manager,
                    self.usuario_atual.id,
                    LogAtividade.ACAO_EDITAR,
                    f"Redefiniu senha do usuário: {nome_usuario}",
                    "usuario",
                    usuario.id
                )
                
                self.load_data()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível redefinir a senha.")
    
    @Slot()
    def toggle_ativo(self):
        """Ativa ou desativa o usuário selecionado"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        usuario_id = int(self.table.item(row, 0).text())
        nome_usuario = self.table.item(row, 1).text()
        
        # Buscar o usuário pelo ID
        usuario = None
        for u in self.usuarios:
            if u.id == usuario_id:
                usuario = u
                break
        
        if not usuario:
            QMessageBox.critical(self, "Erro", "Usuário não encontrado.")
            return
        
        # Impedir desativação do próprio usuário
        if usuario.id == self.usuario_atual.id:
            QMessageBox.warning(self, "Atenção", "Você não pode desativar seu próprio usuário.")
            return
        
        # Confirmar ação
        acao = "desativar" if usuario.ativo else "ativar"
        reply = QMessageBox.question(
            self, 
            f"Confirmar {acao}",
            f"Tem certeza que deseja {acao} o usuário '{nome_usuario}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Atualizar o status
            usuario.ativo = not usuario.ativo
            
            if usuario.save(self.db_manager):
                status = "ativado" if usuario.ativo else "desativado"
                QMessageBox.information(self, "Sucesso", f"Usuário {status} com sucesso.")
                
                # Registrar atividade
                LogAtividade.registrar(
                    self.db_manager,
                    self.usuario_atual.id,
                    LogAtividade.ACAO_EDITAR,
                    f"{status.capitalize()} usuário: {nome_usuario}",
                    "usuario",
                    usuario.id
                )
                
                self.load_data()
            else:
                QMessageBox.critical(self, "Erro", f"Não foi possível {acao} o usuário.")
    
    @Slot()
    def delete_usuario(self):
        """Exclui o usuário selecionado"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        usuario_id = int(self.table.item(row, 0).text())
        nome_usuario = self.table.item(row, 1).text()
        
        # Buscar o usuário pelo ID
        usuario = None
        for u in self.usuarios:
            if u.id == usuario_id:
                usuario = u
                break
        
        if not usuario:
            QMessageBox.critical(self, "Erro", "Usuário não encontrado.")
            return
        
        # Impedir exclusão do próprio usuário
        if usuario.id == self.usuario_atual.id:
            QMessageBox.warning(self, "Atenção", "Você não pode excluir seu próprio usuário.")
            return
        
        # Confirmar exclusão
        reply = QMessageBox.question(
            self, 
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o usuário '{nome_usuario}'?\n"
            f"Esta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if usuario.delete(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Usuário excluído com sucesso.")
                
                # Registrar atividade
                LogAtividade.registrar(
                    self.db_manager,
                    self.usuario_atual.id,
                    LogAtividade.ACAO_EXCLUIR,
                    f"Excluiu usuário: {nome_usuario}",
                    "usuario",
                    usuario_id
                )
                
                self.load_data()
                self.editar_button.setEnabled(False)
                self.resetar_senha_button.setEnabled(False)
                self.ativar_desativar_button.setEnabled(False)
                self.excluir_button.setEnabled(False)
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível excluir o usuário.")
    
    @Slot()
    def on_selection_changed(self):
        """Atualiza o estado dos botões quando a seleção muda"""
        has_selection = len(self.table.selectedItems()) > 0
        self.editar_button.setEnabled(has_selection)
        self.resetar_senha_button.setEnabled(has_selection)
        self.ativar_desativar_button.setEnabled(has_selection)
        self.excluir_button.setEnabled(has_selection)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QMessageBox, QCheckBox,
                              QFormLayout, QWidget, QGroupBox)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QPixmap

from models.usuario import Usuario, LogAtividade

class LoginDialog(QDialog):
    """Diálogo de login para o sistema"""
    
    login_success = Signal(Usuario)  # Sinal emitido quando o login é bem-sucedido
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Login - Sistema de Controle de Territórios")
        self.setMinimumSize(400, 300)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        layout = QVBoxLayout(self)
        
        # Título/Logo
        title_label = QLabel("Sistema de Controle de Territórios")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Mensagem de boas-vindas
        welcome_label = QLabel("Faça login para acessar o sistema")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Formulário de login
        login_group = QGroupBox("Credenciais")
        login_layout = QFormLayout(login_group)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("seu.email@exemplo.com")
        login_layout.addRow("Email:", self.email_input)
        
        self.senha_input = QLineEdit()
        self.senha_input.setPlaceholderText("Sua senha")
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addRow("Senha:", self.senha_input)
        
        self.lembrar_checkbox = QCheckBox("Lembrar email")
        login_layout.addRow("", self.lembrar_checkbox)
        
        layout.addWidget(login_group)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.sair_button = QPushButton("Sair")
        self.sair_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.sair_button)
        
        self.login_button = QPushButton("Entrar")
        self.login_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.login_button.clicked.connect(self.fazer_login)
        buttons_layout.addWidget(self.login_button)
        
        layout.addLayout(buttons_layout)
        
        # Conectar sinais
        self.email_input.returnPressed.connect(self.senha_input.setFocus)
        self.senha_input.returnPressed.connect(self.fazer_login)
        
        # Carregar configurações salvas
        self.carregar_configuracoes()
    
    def carregar_configuracoes(self):
        """Carrega configurações salvas, como email lembrado"""
        # Implementação futura: carregar de um arquivo de configuração
        pass
    
    def salvar_configuracoes(self):
        """Salva configurações, como email lembrado"""
        # Implementação futura: salvar em um arquivo de configuração
        pass
    
    @Slot()
    def fazer_login(self):
        """Verifica as credenciais e faz login se forem válidas"""
        email = self.email_input.text().strip()
        senha = self.senha_input.text()
        
        if not email or not senha:
            QMessageBox.warning(self, "Atenção", "Por favor, preencha todos os campos.")
            return
        
        # Verificar credenciais
        usuario = Usuario.verificar_credenciais(self.db_manager, email, senha)
        
        if usuario:
            # Registrar atividade de login
            LogAtividade.registrar(
                self.db_manager, 
                usuario.id, 
                LogAtividade.ACAO_LOGIN, 
                f"Login realizado por {usuario.nome}"
            )
            
            # Salvar configurações se marcado "lembrar"
            if self.lembrar_checkbox.isChecked():
                self.salvar_configuracoes()
            
            # Emitir sinal de sucesso com o usuário logado
            self.login_success.emit(usuario)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", "Email ou senha incorretos.")
            self.senha_input.clear()
            self.senha_input.setFocus()
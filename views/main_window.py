#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PySide6.QtWidgets import (QMainWindow, QStackedWidget, QToolBar, QStatusBar,
                             QLabel, QWidget, QVBoxLayout, QHBoxLayout, QDialog,
                             QPushButton, QLineEdit, QMessageBox, QFormLayout,
                             QMenu, QApplication, QSizePolicy)
from PySide6.QtGui import QAction, QIcon, QPixmap, QActionGroup
from PySide6.QtCore import QSize, Qt, Signal, Slot, QTimer, QProcess

from views.dashboard import DashboardWidget
from views.territorios import TerritoriosWidget
from views.saidas_campo import SaidasCampoWidget
from views.designacoes import DesignacoesWidget
from views.view_territorios import ViewTerritoriosWidget
from views.predios_vilas import PrediosVilasWidget
from views.usuarios_widget import UsuariosWidget
from views.login_dialog import LoginDialog
from views.notificacoes_widget import NotificacoesWidget

from models.usuario import Usuario, LogAtividade
from models.notificacao_manager import NotificacaoManager

class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    def __init__(self, db_manager):
        super().__init__()
        
        self.db_manager = db_manager
        self.usuario = None  # Usuário logado
        
        self.setWindowTitle("Sistema de Controle de Territórios")
        self.setMinimumSize(1000, 700)
        
        # Configurar barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Widget central com páginas empilhadas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Autenticar o usuário
        self.mostrar_login()
    
    def mostrar_login(self):
        """Exibe o diálogo de login"""
        dialog = LoginDialog(self.db_manager)
        dialog.login_success.connect(self.autenticar_usuario)
        
        # Se o login for cancelado, fechar a aplicação
        if dialog.exec() != QDialog.Accepted:
            QApplication.quit()
    
    @Slot(Usuario)
    def autenticar_usuario(self, usuario):
        """Configura a aplicação para o usuário logado"""
        self.usuario = usuario
        
        # Mostrar mensagem de boas-vindas
        self.status_bar.showMessage(f"Bem-vindo ao Sistema de Controle de Territórios, {usuario.nome}!")
        
        # Inicializar interface
        self.setup_widgets()
        self.setup_sidebar()
        
        # Verificar notificações periodicamente
        self.setup_notificacoes()
    
    def setup_widgets(self):
        """Inicializa os widgets de cada página"""
        
        # Dashboard
        self.dashboard_widget = DashboardWidget(self.db_manager)
        self.stacked_widget.addWidget(self.dashboard_widget)
        
        # Territórios
        self.territorios_widget = TerritoriosWidget(self.db_manager)
        self.stacked_widget.addWidget(self.territorios_widget)
        
        # Saídas de Campo
        self.saidas_campo_widget = SaidasCampoWidget(self.db_manager)
        self.stacked_widget.addWidget(self.saidas_campo_widget)
        
        # Designações
        self.designacoes_widget = DesignacoesWidget(self.db_manager)
        self.stacked_widget.addWidget(self.designacoes_widget)
        
        # Controle de Atendimentos
        self.view_territorios_widget = ViewTerritoriosWidget(self.db_manager)
        self.stacked_widget.addWidget(self.view_territorios_widget)
        
        # Prédios e Vilas
        self.predios_vilas_widget = PrediosVilasWidget(self.db_manager)
        self.stacked_widget.addWidget(self.predios_vilas_widget)
        
        # Usuários (apenas para gestores e administradores)
        if self.usuario.nivel_permissao >= Usuario.NIVEL_GESTOR:
            self.usuarios_widget = UsuariosWidget(self.db_manager, self.usuario)
            self.stacked_widget.addWidget(self.usuarios_widget)
        
        # Notificações
        self.notificacoes_widget = NotificacoesWidget(self.db_manager, self.usuario)
        self.stacked_widget.addWidget(self.notificacoes_widget)
    
    def setup_sidebar(self):
        """Configura a barra lateral com menu"""
        # Cria a barra de ferramentas lateral
        self.sidebar = QToolBar("Menu Principal")
        self.sidebar.setMovable(False)
        self.sidebar.setIconSize(QSize(24, 24))
        self.sidebar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.sidebar.setOrientation(Qt.Orientation.Vertical)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.sidebar)
        
        # Adicionar informações do usuário
        user_widget = QWidget()
        user_layout = QVBoxLayout(user_widget)
        user_layout.setContentsMargins(10, 5, 10, 5)
        
        # Nome do usuário
        user_name = QLabel(self.usuario.nome)
        user_name.setStyleSheet("font-weight: bold;")
        user_layout.addWidget(user_name)
        
        # Tipo de conta
        nivel_texto = "Usuário Básico"
        if self.usuario.nivel_permissao == Usuario.NIVEL_GESTOR:
            nivel_texto = "Gestor"
        elif self.usuario.nivel_permissao == Usuario.NIVEL_ADMIN:
            nivel_texto = "Administrador"
        
        user_level = QLabel(nivel_texto)
        user_level.setStyleSheet("font-size: 9pt; color: #666;")
        user_layout.addWidget(user_level)
        
        self.sidebar.addWidget(user_widget)
        self.sidebar.addSeparator()
        
        # Ações do menu
        self.setup_actions()
        
        # Adiciona separadores
        self.sidebar.addSeparator()
        
        label = QLabel("Controle de Atendimentos")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-weight: bold; color: #555; margin-top: 10px;")
        self.sidebar.addWidget(label)
        
        self.sidebar.addAction(self.action_view_territorios)
        self.sidebar.addAction(self.action_predios_vilas)
        
        # Adicionar seção administrativa para gestores e administradores
        if self.usuario.nivel_permissao >= Usuario.NIVEL_GESTOR:
            self.sidebar.addSeparator()
            
            label = QLabel("Administração")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-weight: bold; color: #555; margin-top: 10px;")
            self.sidebar.addWidget(label)
            
            self.sidebar.addAction(self.action_usuarios)
        
        # Perfil de usuário e notificações na parte inferior
        self.sidebar.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.sidebar.addWidget(spacer)
        
        # Botão de notificações
        self.sidebar.addAction(self.action_notificacoes)
        
        # Botão de perfil / logout
        self.sidebar.addAction(self.action_perfil)
    
    def setup_actions(self):
        """Configura as ações do menu"""
        # Dashboard
        self.action_dashboard = QAction("Dashboard", self)
        self.action_dashboard.setIcon(QIcon.fromTheme("go-home", QIcon()))
        self.action_dashboard.triggered.connect(self.show_dashboard)
        self.sidebar.addAction(self.action_dashboard)
        
        # Territórios (apenas para gestor e admin)
        self.action_territorios = QAction("Cadastro de Territórios", self)
        self.action_territorios.setIcon(QIcon.fromTheme("map", QIcon()))
        self.action_territorios.triggered.connect(self.show_territorios)
        
        if self.usuario.nivel_permissao >= Usuario.NIVEL_GESTOR:
            self.sidebar.addAction(self.action_territorios)
        
        # Saídas de Campo (apenas para gestor e admin)
        self.action_saidas_campo = QAction("Saídas de Campo", self)
        self.action_saidas_campo.setIcon(QIcon.fromTheme("x-office-calendar", QIcon()))
        self.action_saidas_campo.triggered.connect(self.show_saidas_campo)
        
        if self.usuario.nivel_permissao >= Usuario.NIVEL_GESTOR:
            self.sidebar.addAction(self.action_saidas_campo)
        
        # Designações (apenas para gestor e admin)
        self.action_designacoes = QAction("Designação", self)
        self.action_designacoes.setIcon(QIcon.fromTheme("task-due", QIcon()))
        self.action_designacoes.triggered.connect(self.show_designacoes)
        
        if self.usuario.nivel_permissao >= Usuario.NIVEL_GESTOR:
            self.sidebar.addAction(self.action_designacoes)
        
        # Controle de Atendimentos
        self.action_view_territorios = QAction("Residenciais/Comerciais", self)
        self.action_view_territorios.setIcon(QIcon.fromTheme("user-home", QIcon()))
        self.action_view_territorios.triggered.connect(self.show_view_territorios)
        
        # Prédios e Vilas
        self.action_predios_vilas = QAction("Prédios e Vilas", self)
        self.action_predios_vilas.setIcon(QIcon.fromTheme("view-list-details", QIcon()))
        self.action_predios_vilas.triggered.connect(self.show_predios_vilas)
        
        # Usuários (para administração)
        if self.usuario.nivel_permissao >= Usuario.NIVEL_GESTOR:
            self.action_usuarios = QAction("Usuários", self)
            self.action_usuarios.setIcon(QIcon.fromTheme("system-users", QIcon()))
            self.action_usuarios.triggered.connect(self.show_usuarios)
        
        # Notificações
        self.action_notificacoes = QAction("Notificações", self)
        self.action_notificacoes.setIcon(QIcon.fromTheme("notifications", QIcon()))
        self.action_notificacoes.triggered.connect(self.show_notificacoes)
        
        # Perfil / Logout
        self.action_perfil = QAction("Meu Perfil / Logout", self)
        self.action_perfil.setIcon(QIcon.fromTheme("system-users", QIcon()))
        self.action_perfil.triggered.connect(self.show_perfil_menu)
    
    def setup_notificacoes(self):
        """Configura o sistema de notificações"""
        # Verificar notificações no início
        NotificacaoManager.verificar_todas_notificacoes(self.db_manager)
        
        # Configurar o timer para verificação periódica (a cada 15 minutos)
        self.notificacao_timer = QTimer(self)
        self.notificacao_timer.timeout.connect(self.verificar_notificacoes)
        self.notificacao_timer.start(900000)  # 15 minutos = 900000 ms
        
        # Verificar se há notificações não lidas
        self.atualizar_icone_notificacoes()
    
    def atualizar_icone_notificacoes(self):
        """Atualiza o ícone de notificações com contador, se houver não lidas"""
        from models.usuario import Notificacao
        
        # Verificar quantas notificações não lidas existem
        cursor = self.db_manager.execute(
            "SELECT COUNT(*) as total FROM notificacoes "
            "WHERE usuario_id = ? AND status = ?",
            (self.usuario.id, Notificacao.STATUS_NAO_LIDA)
        )
        
        nao_lidas = 0
        if cursor:
            row = cursor.fetchone()
            if row:
                nao_lidas = row['total']
        
        # Atualizar o texto da ação
        if nao_lidas > 0:
            self.action_notificacoes.setText(f"Notificações ({nao_lidas})")
            self.action_notificacoes.setIcon(QIcon.fromTheme("notifications-new", QIcon()))
        else:
            self.action_notificacoes.setText("Notificações")
            self.action_notificacoes.setIcon(QIcon.fromTheme("notifications", QIcon()))
    
    @Slot()
    def verificar_notificacoes(self):
        """Verifica por novas notificações periodicamente"""
        NotificacaoManager.verificar_todas_notificacoes(self.db_manager)
        self.atualizar_icone_notificacoes()
    
    @Slot()
    def show_dashboard(self):
        """Mostra a página do dashboard"""
        self.dashboard_widget.update_data()
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)
        self.status_bar.showMessage("Dashboard")
        
        # Registrar atividade
        LogAtividade.registrar(
            self.db_manager,
            self.usuario.id,
            LogAtividade.ACAO_VISUALIZAR,
            "Acessou o Dashboard"
        )
    
    @Slot()
    def show_territorios(self):
        """Mostra a página de cadastro de territórios"""
        self.territorios_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.territorios_widget)
        self.status_bar.showMessage("Cadastro de Territórios")
        
        # Registrar atividade
        LogAtividade.registrar(
            self.db_manager,
            self.usuario.id,
            LogAtividade.ACAO_VISUALIZAR,
            "Acessou o Cadastro de Territórios"
        )
    
    @Slot()
    def show_saidas_campo(self):
        """Mostra a página de saídas de campo"""
        self.saidas_campo_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.saidas_campo_widget)
        self.status_bar.showMessage("Saídas de Campo")
        
        # Registrar atividade
        LogAtividade.registrar(
            self.db_manager,
            self.usuario.id,
            LogAtividade.ACAO_VISUALIZAR,
            "Acessou as Saídas de Campo"
        )
    
    @Slot()
    def show_designacoes(self):
        """Mostra a página de designações"""
        self.designacoes_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.designacoes_widget)
        self.status_bar.showMessage("Designação de Territórios")
        
        # Registrar atividade
        LogAtividade.registrar(
            self.db_manager,
            self.usuario.id,
            LogAtividade.ACAO_VISUALIZAR,
            "Acessou as Designações"
        )
    
    @Slot()
    def show_view_territorios(self):
        """Mostra a página de controle de atendimentos de territórios"""
        self.view_territorios_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.view_territorios_widget)
        self.status_bar.showMessage("Controle de Atendimentos - Residenciais/Comerciais")
        
        # Registrar atividade
        LogAtividade.registrar(
            self.db_manager,
            self.usuario.id,
            LogAtividade.ACAO_VISUALIZAR,
            "Acessou o Controle de Atendimentos - Residenciais/Comerciais"
        )
    
    @Slot()
    def show_predios_vilas(self):
        """Mostra a página de prédios e vilas"""
        self.predios_vilas_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.predios_vilas_widget)
        self.status_bar.showMessage("Controle de Atendimentos - Prédios e Vilas")
        
        # Registrar atividade
        LogAtividade.registrar(
            self.db_manager,
            self.usuario.id,
            LogAtividade.ACAO_VISUALIZAR,
            "Acessou o Controle de Atendimentos - Prédios e Vilas"
        )
    
    @Slot()
    def show_usuarios(self):
        """Mostra a página de gerenciamento de usuários"""
        if self.usuario.nivel_permissao >= Usuario.NIVEL_GESTOR:
            self.usuarios_widget.load_data()
            self.stacked_widget.setCurrentWidget(self.usuarios_widget)
            self.status_bar.showMessage("Gerenciamento de Usuários")
            
            # Registrar atividade
            LogAtividade.registrar(
                self.db_manager,
                self.usuario.id,
                LogAtividade.ACAO_VISUALIZAR,
                "Acessou o Gerenciamento de Usuários"
            )
    
    @Slot()
    def show_notificacoes(self):
        """Mostra a página de notificações"""
        self.notificacoes_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.notificacoes_widget)
        self.status_bar.showMessage("Minhas Notificações")
        
        # Registrar atividade
        LogAtividade.registrar(
            self.db_manager,
            self.usuario.id,
            LogAtividade.ACAO_VISUALIZAR,
            "Acessou as Notificações"
        )
    
    @Slot()
    def show_perfil_menu(self):
        """Exibe o menu de perfil/logout"""
        menu = QMenu(self)
        
        editar_perfil = QAction("Editar Meu Perfil", self)
        editar_perfil.triggered.connect(self.editar_perfil)
        menu.addAction(editar_perfil)
        
        alterar_senha = QAction("Alterar Minha Senha", self)
        alterar_senha.triggered.connect(self.alterar_senha)
        menu.addAction(alterar_senha)
        
        menu.addSeparator()
        
        logout = QAction("Sair (Logout)", self)
        logout.triggered.connect(self.fazer_logout)
        menu.addAction(logout)
        
        # Posicionar o menu abaixo do botão na barra lateral
        action_pos = self.sidebar.actionGeometry(self.action_perfil)
        global_pos = self.sidebar.mapToGlobal(action_pos.bottomLeft())
        menu.exec(global_pos)
    
    def editar_perfil(self):
        """Abre o diálogo para edição de perfil"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Meu Perfil")
        dialog.resize(400, 200)
        
        layout = QFormLayout(dialog)
        
        nome_input = QLineEdit(self.usuario.nome)
        layout.addRow("Nome:", nome_input)
        
        email_input = QLineEdit(self.usuario.email)
        layout.addRow("Email:", email_input)
        
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
            
            # Validações
            if not nome or not email:
                QMessageBox.warning(self, "Atenção", "Por favor, preencha todos os campos.")
                return
            
            # Verificar se o email já existe (para outro usuário)
            if email != self.usuario.email:
                outro_usuario = Usuario.get_by_email(self.db_manager, email)
                if outro_usuario and outro_usuario.id != self.usuario.id:
                    QMessageBox.warning(self, "Atenção", "Este email já está em uso por outro usuário.")
                    return
            
            # Atualizar os dados
            self.usuario.nome = nome
            self.usuario.email = email
            
            if self.usuario.save(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Perfil atualizado com sucesso.")
                
                # Registrar atividade
                LogAtividade.registrar(
                    self.db_manager,
                    self.usuario.id,
                    LogAtividade.ACAO_EDITAR,
                    "Atualizou seu perfil"
                )
                
                # Atualizar sidebar
                self.atualizar_sidebar_usuario()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível atualizar o perfil.")
    
    def alterar_senha(self):
        """Abre o diálogo para alteração de senha"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Alterar Minha Senha")
        dialog.resize(400, 200)
        
        layout = QFormLayout(dialog)
        
        senha_atual_input = QLineEdit()
        senha_atual_input.setPlaceholderText("Senha atual")
        senha_atual_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Senha Atual:", senha_atual_input)
        
        nova_senha_input = QLineEdit()
        nova_senha_input.setPlaceholderText("Nova senha")
        nova_senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Nova Senha:", nova_senha_input)
        
        confirmar_senha_input = QLineEdit()
        confirmar_senha_input.setPlaceholderText("Confirme a nova senha")
        confirmar_senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Confirmar Senha:", confirmar_senha_input)
        
        # Botões
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = QPushButton("Alterar Senha")
        save_button.setStyleSheet("background-color: #4CAF50; color: white;")
        save_button.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        layout.addRow("", buttons_layout)
        
        if dialog.exec():
            senha_atual = senha_atual_input.text()
            nova_senha = nova_senha_input.text()
            confirmar_senha = confirmar_senha_input.text()
            
            # Validações
            if not senha_atual or not nova_senha or not confirmar_senha:
                QMessageBox.warning(self, "Atenção", "Por favor, preencha todos os campos.")
                return
            
            if not self.usuario.verificar_senha(senha_atual):
                QMessageBox.warning(self, "Atenção", "Senha atual incorreta.")
                return
            
            if nova_senha != confirmar_senha:
                QMessageBox.warning(self, "Atenção", "As senhas não coincidem.")
                return
            
            # Atualizar a senha
            self.usuario.definir_senha(nova_senha)
            
            if self.usuario.save(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Senha alterada com sucesso.")
                
                # Registrar atividade
                LogAtividade.registrar(
                    self.db_manager,
                    self.usuario.id,
                    LogAtividade.ACAO_EDITAR,
                    "Alterou sua senha"
                )
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível alterar a senha.")
    
    def atualizar_sidebar_usuario(self):
        """Atualiza as informações do usuário na sidebar"""
        # Implementação posterior: Atualizar o nome do usuário na sidebar
        pass
    
    def fazer_logout(self):
        """Realiza o logout do usuário"""
        # Registrar atividade
        LogAtividade.registrar(
            self.db_manager,
            self.usuario.id,
            LogAtividade.ACAO_LOGOUT,
            f"Logout realizado por {self.usuario.nome}"
        )
        
        # Fechar todas as conexões e widgets atuais
        self.db_manager.close()
        self.close()
        
        # Reiniciar a aplicação (abrir novo processo)
        QApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)
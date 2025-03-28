#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QMainWindow, QStackedWidget, QToolBar, QStatusBar,
                             QLabel, QWidget, QVBoxLayout)
from PySide6.QtGui import QAction
from PySide6.QtGui import QIcon, QAction, QPixmap
from PySide6.QtCore import QSize, Qt, Signal, Slot

from views.dashboard import DashboardWidget
from views.territorios import TerritoriosWidget
from views.saidas_campo import SaidasCampoWidget
from views.designacoes import DesignacoesWidget
from views.view_territorios import ViewTerritoriosWidget
from views.predios_vilas import PrediosVilasWidget

class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    def __init__(self, db_manager):
        super().__init__()
        
        self.db_manager = db_manager
        self.setWindowTitle("Sistema de Controle de Territórios")
        self.setMinimumSize(1000, 700)
        
        # Configurar a barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Bem-vindo ao Sistema de Controle de Territórios")
        
        # Widget central com páginas empilhadas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Inicializar widgets
        self.setup_widgets()
        
        # Configurar a barra lateral com menu
        self.setup_sidebar()
    
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
    
    def setup_sidebar(self):
        """Configura a barra lateral com menu"""
        # Cria a barra de ferramentas lateral
        self.sidebar = QToolBar("Menu Principal")
        self.sidebar.setMovable(False)
        self.sidebar.setIconSize(QSize(24, 24))
        self.sidebar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.sidebar.setOrientation(Qt.Orientation.Vertical)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.sidebar)
        
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
    
    def setup_actions(self):
        """Configura as ações do menu"""
        # Dashboard
        self.action_dashboard = QAction("Dashboard", self)
        self.action_dashboard.setIcon(QIcon.fromTheme("go-home", QIcon()))
        self.action_dashboard.triggered.connect(self.show_dashboard)
        self.sidebar.addAction(self.action_dashboard)
        
        # Territórios
        self.action_territorios = QAction("Cadastro de Territórios", self)
        self.action_territorios.setIcon(QIcon.fromTheme("map", QIcon()))
        self.action_territorios.triggered.connect(self.show_territorios)
        self.sidebar.addAction(self.action_territorios)
        
        # Saídas de Campo
        self.action_saidas_campo = QAction("Saídas de Campo", self)
        self.action_saidas_campo.setIcon(QIcon.fromTheme("x-office-calendar", QIcon()))
        self.action_saidas_campo.triggered.connect(self.show_saidas_campo)
        self.sidebar.addAction(self.action_saidas_campo)
        
        # Designações
        self.action_designacoes = QAction("Designação", self)
        self.action_designacoes.setIcon(QIcon.fromTheme("task-due", QIcon()))
        self.action_designacoes.triggered.connect(self.show_designacoes)
        self.sidebar.addAction(self.action_designacoes)
        
        # Controle de Atendimentos
        self.action_view_territorios = QAction("Residenciais/Comerciais", self)
        self.action_view_territorios.setIcon(QIcon.fromTheme("user-home", QIcon()))
        self.action_view_territorios.triggered.connect(self.show_view_territorios)
        
        # Prédios e Vilas
        self.action_predios_vilas = QAction("Prédios e Vilas", self)
        self.action_predios_vilas.setIcon(QIcon.fromTheme("view-list-details", QIcon()))
        self.action_predios_vilas.triggered.connect(self.show_predios_vilas)
    
    @Slot()
    def show_dashboard(self):
        """Mostra a página do dashboard"""
        self.dashboard_widget.update_data()
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)
        self.status_bar.showMessage("Dashboard")
    
    @Slot()
    def show_territorios(self):
        """Mostra a página de cadastro de territórios"""
        self.territorios_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.territorios_widget)
        self.status_bar.showMessage("Cadastro de Territórios")
    
    @Slot()
    def show_saidas_campo(self):
        """Mostra a página de saídas de campo"""
        self.saidas_campo_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.saidas_campo_widget)
        self.status_bar.showMessage("Saídas de Campo")
    
    @Slot()
    def show_designacoes(self):
        """Mostra a página de designações"""
        self.designacoes_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.designacoes_widget)
        self.status_bar.showMessage("Designação de Territórios")
    
    @Slot()
    def show_view_territorios(self):
        """Mostra a página de controle de atendimentos de territórios"""
        self.view_territorios_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.view_territorios_widget)
        self.status_bar.showMessage("Controle de Atendimentos - Residenciais/Comerciais")
    
    @Slot()
    def show_predios_vilas(self):
        """Mostra a página de prédios e vilas"""
        self.predios_vilas_widget.load_data()
        self.stacked_widget.setCurrentWidget(self.predios_vilas_widget)
        self.status_bar.showMessage("Controle de Atendimentos - Prédios e Vilas")
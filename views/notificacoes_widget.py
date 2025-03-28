#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QMenu, QMessageBox, QDialog, QTextEdit,
                             QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QColor, QFont, QAction

from models.usuario import Notificacao
from datetime import datetime

class NotificacaoItem(QListWidgetItem):
    """Item personalizado para a lista de notificações"""
    
    def __init__(self, notificacao):
        super().__init__()
        self.notificacao = notificacao
        self.setSizeHint(QSize(0, 50))  # Altura maior para melhor visualização
        self.update_display()
    
    def update_display(self):
        """Atualiza a exibição do item de acordo com a notificação"""
        if self.notificacao.status == Notificacao.STATUS_NAO_LIDA:
            self.setIcon(QIcon.fromTheme("mail-unread", QIcon()))
            self.setBackground(QColor("#f0f8ff"))  # Azul claro para destacar
            self.setFont(QFont("", -1, QFont.Bold))
        else:
            self.setIcon(QIcon.fromTheme("mail-read", QIcon()))
        
        # Formatar data
        data_formatada = self.notificacao.data_criacao
        try:
            data_dt = datetime.strptime(self.notificacao.data_criacao, "%Y-%m-%d %H:%M:%S")
            data_formatada = data_dt.strftime("%d/%m/%Y %H:%M")
        except:
            pass
        
        # Texto para exibição
        self.setText(f"{self.notificacao.titulo} - {data_formatada}")
        
        # Tooltip com a mensagem completa
        self.setToolTip(self.notificacao.mensagem)
        
        # Definir cor conforme o tipo de notificação
        if self.notificacao.tipo == Notificacao.TIPO_ALERTA:
            self.setForeground(QColor("#e67e22"))  # Laranja para alertas
        elif self.notificacao.tipo == Notificacao.TIPO_ERRO:
            self.setForeground(QColor("#e74c3c"))  # Vermelho para erros


class NotificacoesWidget(QWidget):
    """Widget para exibir e gerenciar notificações"""
    
    def __init__(self, db_manager, usuario_atual):
        super().__init__()
        self.db_manager = db_manager
        self.usuario_atual = usuario_atual
        self.notificacoes = []
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        layout = QVBoxLayout(self)
        
        # Título
        title_layout = QHBoxLayout()
        title_label = QLabel("Minhas Notificações")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_layout.addWidget(title_label)
        
        # Contador de notificações não lidas
        self.count_label = QLabel()
        self.count_label.setStyleSheet("color: #3498db;")
        title_layout.addWidget(self.count_label)
        title_layout.addStretch()
        
        # Botões de ação
        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon.fromTheme("view-refresh", QIcon()))
        refresh_button.setToolTip("Atualizar notificações")
        refresh_button.clicked.connect(self.load_data)
        title_layout.addWidget(refresh_button)
        
        mark_all_button = QPushButton()
        mark_all_button.setIcon(QIcon.fromTheme("mail-mark-read", QIcon()))
        mark_all_button.setToolTip("Marcar todas como lidas")
        mark_all_button.clicked.connect(self.marcar_todas_como_lidas)
        title_layout.addWidget(mark_all_button)
        
        layout.addLayout(title_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Lista de notificações
        self.notificacoes_list = QListWidget()
        self.notificacoes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notificacoes_list.customContextMenuRequested.connect(self.show_context_menu)
        self.notificacoes_list.itemDoubleClicked.connect(self.ver_notificacao)
        self.notificacoes_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.notificacoes_list)
    
    def load_data(self):
        """Carrega as notificações do usuário"""
        self.notificacoes = Notificacao.get_by_usuario(self.db_manager, self.usuario_atual.id)
        self.update_list()
    
    def update_list(self):
        """Atualiza a lista de notificações"""
        self.notificacoes_list.clear()
        
        # Contador de não lidas
        nao_lidas = sum(1 for n in self.notificacoes if n.status == Notificacao.STATUS_NAO_LIDA)
        self.count_label.setText(f"{nao_lidas} não lida(s)" if nao_lidas > 0 else "")
        
        # Adicionar itens à lista
        for notificacao in self.notificacoes:
            if notificacao.status != Notificacao.STATUS_ARQUIVADA:  # Não exibir arquivadas
                item = NotificacaoItem(notificacao)
                self.notificacoes_list.addItem(item)
        
        # Mensagem se não houver notificações
        if self.notificacoes_list.count() == 0:
            self.notificacoes_list.addItem("Nenhuma notificação disponível.")
    
    def show_context_menu(self, position):
        """Exibe o menu de contexto para um item da lista"""
        item = self.notificacoes_list.itemAt(position)
        if item and hasattr(item, 'notificacao'):
            menu = QMenu(self)
            
            ver_action = QAction("Ver detalhes", self)
            ver_action.triggered.connect(lambda: self.ver_notificacao(item))
            menu.addAction(ver_action)
            
            if item.notificacao.status == Notificacao.STATUS_NAO_LIDA:
                ler_action = QAction("Marcar como lida", self)
                ler_action.triggered.connect(lambda: self.marcar_como_lida(item))
                menu.addAction(ler_action)
            
            arquivar_action = QAction("Arquivar", self)
            arquivar_action.triggered.connect(lambda: self.arquivar_notificacao(item))
            menu.addAction(arquivar_action)
            
            menu.exec(self.notificacoes_list.mapToGlobal(position))
    
    def ver_notificacao(self, item):
        """Exibe os detalhes de uma notificação"""
        if not hasattr(item, 'notificacao'):
            return
        
        notificacao = item.notificacao
        
        # Criar diálogo para exibir detalhes
        dialog = QDialog(self)
        dialog.setWindowTitle(notificacao.titulo)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Mensagem
        mensagem_text = QTextEdit()
        mensagem_text.setReadOnly(True)
        mensagem_text.setText(notificacao.mensagem)
        layout.addWidget(mensagem_text)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        
        # Marcar como lida se ainda não foi lida
        if notificacao.status == Notificacao.STATUS_NAO_LIDA:
            self.marcar_como_lida(item)
        
        dialog.exec()
    
    def marcar_como_lida(self, item):
        """Marca uma notificação como lida"""
        if hasattr(item, 'notificacao'):
            if item.notificacao.marcar_como_lida(self.db_manager):
                item.update_display()
                self.load_data()  # Atualizar contador
    
    def arquivar_notificacao(self, item):
        """Arquiva uma notificação"""
        if hasattr(item, 'notificacao'):
            if item.notificacao.arquivar(self.db_manager):
                row = self.notificacoes_list.row(item)
                self.notificacoes_list.takeItem(row)
                self.load_data()  # Atualizar contador
    
    def marcar_todas_como_lidas(self):
        """Marca todas as notificações como lidas"""
        # Confirmar ação
        reply = QMessageBox.question(
            self, 
            "Confirmar",
            "Deseja marcar todas as notificações como lidas?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for i in range(self.notificacoes_list.count()):
                item = self.notificacoes_list.item(i)
                if hasattr(item, 'notificacao') and item.notificacao.status == Notificacao.STATUS_NAO_LIDA:
                    item.notificacao.marcar_como_lida(self.db_manager)
            
            # Atualizar lista
            self.load_data()
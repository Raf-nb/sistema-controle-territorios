#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream, Qt
from PySide6.QtGui import QIcon

from database.db_manager import DatabaseManager
from views.main_window import MainWindow

def setup_database():
    """Inicializa o banco de dados"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'territorios.db')
    db_manager = DatabaseManager(db_path)
    db_manager.setup_database()
    return db_manager

def main():
    """Função principal que inicializa a aplicação"""
    # Cria a aplicação
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema de Controle de Territórios")
    
    # Configura estilo visual
    app.setStyle("Fusion")
    
    # Inicializa o banco de dados
    db_manager = setup_database()
    
    # Cria a janela principal
    window = MainWindow(db_manager)
    window.show()
    
    # Inicia o loop de eventos
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
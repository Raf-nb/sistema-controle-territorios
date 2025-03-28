#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QPushButton, QLineEdit, QComboBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QDialog, QFormLayout, QTextEdit,
                             QListWidget, QListWidgetItem, QCheckBox,
                             QTabWidget, QDateEdit, QGridLayout, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal, Slot, QDate
from PySide6.QtGui import QIcon, QFont, QColor

from models.imovel import Imovel
from models.atendimento import Atendimento
from models.designacao import DesignacaoPredioVila

from datetime import datetime

class PrediosVilasWidget(QWidget):
    """Widget para gerenciamento de prédios e vilas"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.predios_vilas = []
        self.current_imovel = None
        self.current_unidade = None
        self.filtro_predios = True
        self.filtro_vilas = True
        self.filtro_concluidos = False
        self.filtro_designados = False
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        main_layout = QVBoxLayout(self)
        
        # Título da página
        title_label = QLabel("Cadastro e Controle de Prédios e Vilas")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Tabs para as telas
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Tab de Lista de prédios e vilas
        self.lista_tab = QWidget()
        self.tabs.addTab(self.lista_tab, "Lista de Prédios e Vilas")
        
        # Tab de Cadastro
        self.cadastro_tab = QWidget()
        self.tabs.addTab(self.cadastro_tab, "Novo Cadastro")
        
        # === Tab de Lista ===
        lista_layout = QVBoxLayout(self.lista_tab)
        
        # Filtros
        filtros_group = QGroupBox("Filtros")
        filtros_group.setStyleSheet("QGroupBox { background-color: #f8f9fa; }")
        filtros_layout = QGridLayout(filtros_group)
        
        self.cb_predios = QCheckBox("Mostrar Prédios")
        self.cb_predios.setChecked(True)
        self.cb_predios.stateChanged.connect(self.on_filtro_changed)
        filtros_layout.addWidget(self.cb_predios, 0, 0)
        
        self.cb_vilas = QCheckBox("Mostrar Vilas")
        self.cb_vilas.setChecked(True)
        self.cb_vilas.stateChanged.connect(self.on_filtro_changed)
        filtros_layout.addWidget(self.cb_vilas, 0, 1)
        
        self.cb_concluidos = QCheckBox("Apenas Não Concluídos")
        self.cb_concluidos.stateChanged.connect(self.on_filtro_changed)
        filtros_layout.addWidget(self.cb_concluidos, 0, 2)
        
        self.cb_designados = QCheckBox("Apenas Designados")
        self.cb_designados.stateChanged.connect(self.on_filtro_changed)
        filtros_layout.addWidget(self.cb_designados, 0, 3)
        
        lista_layout.addWidget(filtros_group)
        
        # Grid de prédios e vilas
        self.grid_layout = QGridLayout()
        
        # Usar QScrollArea para rolagem
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        lista_layout.addWidget(scroll)
        
        scroll_content = QWidget()
        scroll.setWidget(scroll_content)
        scroll_content.setLayout(self.grid_layout)
        
        # Mensagem de carregamento ou sem dados
        self.loading_label = QLabel("Carregando prédios e vilas...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lista_layout.addWidget(self.loading_label)
        
        # === Tab de Cadastro ===
        cadastro_layout = QVBoxLayout(self.cadastro_tab)
        
        form_group = QGroupBox("Adicionar Novo Prédio/Vila")
        form_layout = QFormLayout(form_group)
        
        # Território
        self.territorio_select = QComboBox()
        form_layout.addRow("Território:", self.territorio_select)
        
        # Rua
        self.rua_select = QComboBox()
        self.rua_select.setEnabled(False)
        form_layout.addRow("Rua:", self.rua_select)
        
        # Número
        self.numero_input = QLineEdit()
        self.numero_input.setPlaceholderText("Ex: 123")
        form_layout.addRow("Número:", self.numero_input)
        
        # Tipo
        self.tipo_select = QComboBox()
        self.tipo_select.addItems(["Prédio", "Vila"])
        form_layout.addRow("Tipo:", self.tipo_select)
        
        # Nome (opcional)
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Ex: Edifício Primavera")
        form_layout.addRow("Nome (opcional):", self.nome_input)
        
        # Total de unidades
        self.unidades_input = QLineEdit()
        self.unidades_input.setPlaceholderText("Ex: 12")
        form_layout.addRow("Total de Unidades:", self.unidades_input)
        
        # Tipo de portaria
        self.portaria_select = QComboBox()
        self.portaria_select.addItems(["24 horas", "Eletrônica", "Diurna", "Sem Portaria", "Outro"])
        form_layout.addRow("Tipo de Portaria:", self.portaria_select)
        
        # Tipo de acesso
        self.acesso_select = QComboBox()
        self.acesso_select.addItems(["Fácil (Sem Restrições)", "Restrito (Com Autorização)", "Via Interfone", "Difícil"])
        form_layout.addRow("Tipo de Acesso:", self.acesso_select)
        
        # Observações
        self.observacoes_input = QTextEdit()
        self.observacoes_input.setPlaceholderText("Observações sobre o imóvel...")
        form_layout.addRow("Observações:", self.observacoes_input)
        
        # Botão para cadastrar
        cadastrar_button = QPushButton("Cadastrar")
        cadastrar_button.setStyleSheet("background-color: #4CAF50; color: white;")
        cadastrar_button.clicked.connect(self.cadastrar_predio_vila)
        form_layout.addRow("", cadastrar_button)
        
        cadastro_layout.addWidget(form_group)
        
        # Conectar sinais
        self.territorio_select.currentIndexChanged.connect(self.on_territorio_changed)
        
        # Carregar territórios no combobox
        self.carregar_territorios()
    
    def carregar_territorios(self):
        """Carrega a lista de territórios para o combobox"""
        self.territorio_select.clear()
        self.territorio_select.addItem("Selecione um território...", None)
        
        cursor = self.db_manager.execute("SELECT id, nome FROM territorios ORDER BY nome")
        if cursor:
            for row in cursor.fetchall():
                self.territorio_select.addItem(row['nome'], row['id'])
    
    def on_territorio_changed(self, index):
        """Atualiza o combobox de ruas ao mudar o território"""
        self.rua_select.clear()
        territorio_id = self.territorio_select.currentData()
        
        if territorio_id:
            self.rua_select.setEnabled(True)
            self.rua_select.addItem("Selecione uma rua...", None)
            
            cursor = self.db_manager.execute(
                "SELECT id, nome FROM ruas WHERE territorio_id = ? ORDER BY nome",
                (territorio_id,)
            )
            if cursor:
                for row in cursor.fetchall():
                    self.rua_select.addItem(row['nome'], row['id'])
        else:
            self.rua_select.setEnabled(False)
    
    def load_data(self):
        """Carrega os dados dos prédios e vilas"""
        self.loading_label.setText("Carregando prédios e vilas...")
        self.loading_label.setVisible(True)
        
        # Limpar grid existente
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Carregar prédios e vilas
        self.predios_vilas = Imovel.get_predios_vilas(self.db_manager)
        
        # Filtrar itens conforme os checkboxes
        filtered_items = []
        
        for imovel in self.predios_vilas:
            tipo_ok = (imovel.tipo == 'predio' and self.filtro_predios) or \
                     (imovel.tipo == 'vila' and self.filtro_vilas)
            
            # Verificar se tem designação ativa
            if self.filtro_designados:
                designacao = DesignacaoPredioVila.get_by_imovel(self.db_manager, imovel.id)
                designado = designacao is not None
                if not designado:
                    continue
            
            if tipo_ok:
                filtered_items.append(imovel)
        
        if filtered_items:
            self.loading_label.setVisible(False)
            self.mostrar_cards(filtered_items)
        else:
            self.loading_label.setText("Nenhum prédio ou vila encontrado com os filtros selecionados.")
    
    def mostrar_cards(self, items):
        """Cria e exibe os cards dos prédios e vilas"""
        row, col = 0, 0
        max_columns = 3
        
        for imovel in items:
            card = self.criar_card_imovel(imovel)
            self.grid_layout.addWidget(card, row, col)
            
            # Avançar para a próxima coluna ou linha
            col += 1
            if col >= max_columns:
                col = 0
                row += 1
    
    def criar_card_imovel(self, imovel):
        """Cria um card para exibir um prédio ou vila"""
        card = QGroupBox(imovel.nome or f"Nº {imovel.numero}")
        
        # Cor de fundo do título conforme o tipo
        if imovel.tipo == 'predio':
            card.setStyleSheet("QGroupBox { border: 1px solid #6f42c1; border-radius: 5px; margin-top: 1.5em; font-weight: bold; } "
                              "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; "
                              "padding: 5px 15px; background-color: #6f42c1; color: white; }")
        else:  # vila
            card.setStyleSheet("QGroupBox { border: 1px solid #fd7e14; border-radius: 5px; margin-top: 1.5em; font-weight: bold; } "
                              "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; "
                              "padding: 5px 15px; background-color: #fd7e14; color: white; }")
        
        layout = QVBoxLayout(card)
        
        # Endereço
        endereco_label = QLabel(f"<b>Endereço:</b> {imovel.rua_nome}, {imovel.numero}")
        layout.addWidget(endereco_label)
        
        # Tipo
        tipo_label = QLabel(f"<b>Tipo:</b> {imovel.tipo.capitalize()}")
        layout.addWidget(tipo_label)
        
        # Total de unidades
        unidades_label = QLabel(f"<b>Total de Unidades:</b> {imovel.total_unidades or 'Não informado'}")
        layout.addWidget(unidades_label)
        
        # Portaria
        portaria = imovel.tipo_portaria.replace('-', ' ').capitalize() if imovel.tipo_portaria else "Não informado"
        portaria_label = QLabel(f"<b>Portaria:</b> {portaria}")
        layout.addWidget(portaria_label)
        
        # Acesso
        acesso = imovel.tipo_acesso.capitalize() if imovel.tipo_acesso else "Não informado"
        acesso_label = QLabel(f"<b>Acesso:</b> {acesso}")
        layout.addWidget(acesso_label)
        
        # Observações
        if imovel.observacoes:
            obs_label = QLabel(f"<b>Observações:</b> {imovel.observacoes}")
            obs_label.setWordWrap(True)
            layout.addWidget(obs_label)
        
        # Verificar se tem designação ativa
        designacao = DesignacaoPredioVila.get_by_imovel(self.db_manager, imovel.id)
        if designacao:
            designacao_label = QLabel(f"<b>Designado para:</b> {designacao.responsavel}")
            designacao_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            layout.addWidget(designacao_label)
        
        # Botão para detalhes
        btn_detalhes = QPushButton("Ver Detalhes")
        btn_detalhes.setStyleSheet("background-color: #007bff; color: white;")
        btn_detalhes.clicked.connect(lambda: self.ver_detalhes(imovel))
        layout.addWidget(btn_detalhes)
        
        return card
    
    def ver_detalhes(self, imovel):
        """Exibe a tela de detalhes do prédio/vila"""
        self.current_imovel = imovel
        
        # Criar diálogo para detalhes
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalhes do {imovel.tipo.capitalize()}")
        dialog.resize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Cabeçalho com nome e endereço
        header_label = QLabel(f"<h2>{imovel.nome or f'Nº {imovel.numero}'}</h2>")
        header_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(header_label)
        
        endereco_label = QLabel(f"{imovel.rua_nome}, {imovel.numero} - {imovel.territorio_nome}")
        layout.addWidget(endereco_label)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Dados básicos em grid
        info_grid = QGridLayout()
        
        info_grid.addWidget(QLabel("<b>Tipo:</b>"), 0, 0)
        info_grid.addWidget(QLabel(imovel.tipo.capitalize()), 0, 1)
        
        info_grid.addWidget(QLabel("<b>Total de Unidades:</b>"), 0, 2)
        info_grid.addWidget(QLabel(str(imovel.total_unidades or "Não informado")), 0, 3)
        
        portaria = imovel.tipo_portaria.replace('-', ' ').capitalize() if imovel.tipo_portaria else "Não informado"
        info_grid.addWidget(QLabel("<b>Portaria:</b>"), 1, 0)
        info_grid.addWidget(QLabel(portaria), 1, 1)
        
        acesso = imovel.tipo_acesso.capitalize() if imovel.tipo_acesso else "Não informado"
        info_grid.addWidget(QLabel("<b>Acesso:</b>"), 1, 2)
        info_grid.addWidget(QLabel(acesso), 1, 3)
        
        layout.addLayout(info_grid)
        
        # Abas para unidades, histórico e designação
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Tab de unidades
        unidades_tab = QWidget()
        unidades_layout = QVBoxLayout(unidades_tab)
        
        label_busca = QLabel("Buscar Unidade:")
        unidades_layout.addWidget(label_busca)
        
        busca_input = QLineEdit()
        busca_input.setPlaceholderText("Digite o número...")
        unidades_layout.addWidget(busca_input)
        
        # Grid de unidades
        unidades_grid = QGridLayout()
        unidades_layout.addLayout(unidades_grid)
        
        # Carregar unidades
        unidades = imovel.get_unidades(self.db_manager)
        self.mostrar_unidades(unidades, unidades_grid)
        
        # Conectar busca
        busca_input.textChanged.connect(lambda text: self.filtrar_unidades(text, unidades, unidades_grid))
        
        tabs.addTab(unidades_tab, "Unidades")
        
        # Tab de histórico
        historico_tab = QWidget()
        historico_layout = QVBoxLayout(historico_tab)
        
        # Botão para adicionar registro
        btn_add_registro = QPushButton("Adicionar Registro")
        btn_add_registro.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_add_registro.clicked.connect(lambda: self.adicionar_registro(imovel))
        historico_layout.addWidget(btn_add_registro)
        
        # Lista de registros
        registros_list = QListWidget()
        historico_layout.addWidget(registros_list)
        
        # Carregar histórico
        historico = imovel.get_historico(self.db_manager)
        for registro in historico:
            data_formatada = QDate.fromString(registro['data'], "yyyy-MM-dd").toString("dd/MM/yyyy")
            item = QListWidgetItem(f"{data_formatada}: {registro['descricao']}")
            registros_list.addItem(item)
        
        tabs.addTab(historico_tab, "Histórico")
        
        # Tab de designação
        designacao_tab = QWidget()
        designacao_layout = QVBoxLayout(designacao_tab)
        
        # Verificar se já tem designação
        designacao = DesignacaoPredioVila.get_by_imovel(self.db_manager, imovel.id)
        
        if designacao:
            # Exibir detalhes da designação
            info_group = QGroupBox("Informações da Designação")
            info_layout = QFormLayout(info_group)
            
            info_layout.addRow("Responsável:", QLabel(designacao.responsavel))
            info_layout.addRow("Saída de Campo:", QLabel(designacao.saida_campo_nome))
            
            data_des = QDate.fromString(designacao.data_designacao, "yyyy-MM-dd").toString("dd/MM/yyyy")
            info_layout.addRow("Data de Designação:", QLabel(data_des))
            
            if designacao.data_devolucao:
                data_dev = QDate.fromString(designacao.data_devolucao, "yyyy-MM-dd").toString("dd/MM/yyyy")
                info_layout.addRow("Data de Devolução:", QLabel(data_dev))
            else:
                info_layout.addRow("Data de Devolução:", QLabel("Não definida"))
            
            info_layout.addRow("Status:", QLabel(designacao.status.capitalize()))
            
            designacao_layout.addWidget(info_group)
            
            # Botões para gerenciar designação
            btn_layout = QHBoxLayout()
            
            btn_editar = QPushButton("Editar Designação")
            btn_editar.clicked.connect(lambda: self.editar_designacao(designacao, dialog))
            btn_layout.addWidget(btn_editar)
            
            if designacao.status == "ativo":
                btn_concluir = QPushButton("Concluir Designação")
                btn_concluir.setStyleSheet("background-color: #2196F3; color: white;")
                btn_concluir.clicked.connect(lambda: self.concluir_designacao(designacao, dialog))
                btn_layout.addWidget(btn_concluir)
            
            btn_excluir = QPushButton("Excluir Designação")
            btn_excluir.setStyleSheet("background-color: #f44336; color: white;")
            btn_excluir.clicked.connect(lambda: self.excluir_designacao(designacao, dialog))
            btn_layout.addWidget(btn_excluir)
            
            designacao_layout.addLayout(btn_layout)
        else:
            # Exibir mensagem e opção para designar
            msg_label = QLabel("Este prédio/vila ainda não foi designado.")
            designacao_layout.addWidget(msg_label)
            
            btn_designar = QPushButton("Designar Prédio/Vila")
            btn_designar.setStyleSheet("background-color: #4CAF50; color: white;")
            btn_designar.clicked.connect(lambda: self.designar_predio_vila(imovel, dialog))
            designacao_layout.addWidget(btn_designar)
        
        tabs.addTab(designacao_tab, "Designação")
        
        # Botão para fechar
        btn_fechar = QPushButton("Fechar")
        layout.addWidget(btn_fechar)
        btn_fechar.clicked.connect(dialog.accept)
        
        dialog.exec()
    
    def mostrar_unidades(self, unidades, grid_layout):
        """Mostra as unidades do prédio/vila em um grid"""
        # Limpar grid existente
        while grid_layout.count():
            item = grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not unidades:
            grid_layout.addWidget(QLabel("Nenhuma unidade cadastrada."), 0, 0)
            return
        
        # Configurar o grid
        max_columns = 6
        row, col = 0, 0
        
        for unidade in unidades:
            btn = QPushButton(unidade['numero'])
            btn.setMinimumSize(80, 40)
            
            # Verificar se tem atendimento
            cursor = self.db_manager.execute(
                "SELECT * FROM atendimentos WHERE unidade_id = ? ORDER BY data DESC LIMIT 1",
                (unidade['id'],)
            )
            
            atendido = False
            if cursor:
                atendimento = cursor.fetchone()
                if atendimento:
                    atendido = True
                    # Adicionar tooltip com data do atendimento
                    data_formatada = QDate.fromString(atendimento['data'],
                                               "yyyy-MM-dd").toString("dd/MM/yyyy")
                    btn.setToolTip(f"Atendido em: {data_formatada}")
                    
                    # Mudar cor de fundo para indicar que foi atendido
                    btn.setStyleSheet("background-color: #d4edda; color: #155724;")
            
            # ID da unidade como dado para quando o botão for clicado
            btn.setProperty("unidade_id", unidade['id'])
            btn.clicked.connect(lambda checked, u=unidade: self.registrar_atendimento_unidade(u))
            
            grid_layout.addWidget(btn, row, col)
            
            # Avançar para a próxima coluna ou linha
            col += 1
            if col >= max_columns:
                col = 0
                row += 1
    
    def filtrar_unidades(self, texto, unidades, grid_layout):
        """Filtra as unidades pelo texto de busca"""
        if not texto:
            self.mostrar_unidades(unidades, grid_layout)
            return
        
        unidades_filtradas = [u for u in unidades if texto.lower() in u['numero'].lower()]
        self.mostrar_unidades(unidades_filtradas, grid_layout)
    
    def registrar_atendimento_unidade(self, unidade):
        """Registra um atendimento para uma unidade específica"""
        # Verificar se já existe um atendimento para esta unidade
        cursor = self.db_manager.execute(
            "SELECT * FROM atendimentos WHERE unidade_id = ? ORDER BY data DESC LIMIT 1",
            (unidade['id'],)
        )
        
        atendimento_existente = None
        if cursor:
            atendimento_existente = cursor.fetchone()
        
        # Criar diálogo para registrar atendimento
        dialog = QDialog(self)
        dialog.setWindowTitle("Atendimento da Unidade")
        dialog.resize(400, 300)
        
        layout = QFormLayout(dialog)
        
        # Informações da unidade
        info_label = QLabel(f"{unidade['numero']} - {self.current_imovel.nome or 'Nº ' + self.current_imovel.numero}")
        layout.addRow("Unidade:", info_label)
        
        # Data do atendimento
        data_edit = QDateEdit(QDate.currentDate())
        data_edit.setCalendarPopup(True)
        data_edit.setDisplayFormat("dd/MM/yyyy")
        layout.addRow("Data do Atendimento:", data_edit)
        
        # Resultado do atendimento
        resultado_select = QComboBox()
        resultado_select.addItems([
            "Positivo", 
            "Ocupante Ausente", 
            "Recusou Atendimento", 
            "Apenas Visitado"
        ])
        layout.addRow("Resultado:", resultado_select)
        
        # Observações
        obs_edit = QTextEdit()
        obs_edit.setPlaceholderText("Observações sobre o atendimento...")
        layout.addRow("Observações:", obs_edit)
        
        # Preencher com dados existentes, se houver
        if atendimento_existente:
            data_edit.setDate(QDate.fromString(atendimento_existente['data'], "yyyy-MM-dd"))
            if atendimento_existente['resultado']:
                index = resultado_select.findText(atendimento_existente['resultado'].replace('-', ' ').title())
                if index >= 0:
                    resultado_select.setCurrentIndex(index)
            if atendimento_existente['observacoes']:
                obs_edit.setText(atendimento_existente['observacoes'])
        
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
            resultado = resultado_select.currentText().lower().replace(' ', '-')
            observacoes = obs_edit.toPlainText().strip() or None
            
            if atendimento_existente:
                # Atualizar atendimento existente
                cursor = self.db_manager.execute(
                    "UPDATE atendimentos SET data = ?, resultado = ?, observacoes = ? WHERE id = ?",
                    (data, resultado, observacoes, atendimento_existente['id'])
                )
            else:
                # Criar novo atendimento
                cursor = self.db_manager.execute(
                    "INSERT INTO atendimentos (imovel_id, unidade_id, data, resultado, observacoes) VALUES (?, ?, ?, ?, ?)",
                    (self.current_imovel.id, unidade['id'], data, resultado, observacoes)
                )
            
            if cursor:
                self.db_manager.commit()
                QMessageBox.information(self, "Sucesso", "Atendimento registrado com sucesso.")
                
                # Se ainda estamos vendo os detalhes do mesmo prédio/vila, recarregar
                dialog = self.sender().parent()
                if dialog:
                    dialog.accept()
                    self.ver_detalhes(self.current_imovel)
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível registrar o atendimento.")
        
        elif result == 2 and atendimento_existente:  # Remover atendimento
            cursor = self.db_manager.execute(
                "DELETE FROM atendimentos WHERE id = ?",
                (atendimento_existente['id'],)
            )
            
            if cursor:
                self.db_manager.commit()
                QMessageBox.information(self, "Sucesso", "Atendimento removido com sucesso.")
                
                # Se ainda estamos vendo os detalhes do mesmo prédio/vila, recarregar
                dialog = self.sender().parent()
                if dialog:
                    dialog.accept()
                    self.ver_detalhes(self.current_imovel)
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível remover o atendimento.")
    
    def adicionar_registro(self, imovel):
        """Adiciona um registro ao histórico do prédio/vila"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Adicionar Registro ao Histórico")
        dialog.resize(400, 250)
        
        layout = QFormLayout(dialog)
        
        # Data do registro
        data_edit = QDateEdit(QDate.currentDate())
        data_edit.setCalendarPopup(True)
        data_edit.setDisplayFormat("dd/MM/yyyy")
        layout.addRow("Data:", data_edit)
        
        # Descrição
        descricao_edit = QTextEdit()
        descricao_edit.setPlaceholderText("Descreva o que foi feito ou observado...")
        layout.addRow("Descrição:", descricao_edit)
        
        # Botões
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = QPushButton("Salvar Registro")
        save_button.setStyleSheet("background-color: #4CAF50; color: white;")
        save_button.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        
        layout.addRow("", buttons_layout)
        
        if dialog.exec():
            data = data_edit.date().toString("yyyy-MM-dd")
            descricao = descricao_edit.toPlainText().strip()
            
            if not descricao:
                QMessageBox.warning(self, "Atenção", "A descrição do registro é obrigatória.")
                return
            
            if imovel.adicionar_historico(self.db_manager, data, descricao):
                QMessageBox.information(self, "Sucesso", "Registro adicionado com sucesso.")
                
                # Se ainda estamos vendo os detalhes do mesmo prédio/vila, recarregar
                self.ver_detalhes(imovel)
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível adicionar o registro ao histórico.")
    
    def designar_predio_vila(self, imovel, parent_dialog=None):
        """Designa um prédio ou vila"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Designar Prédio/Vila")
        dialog.resize(400, 300)
        
        layout = QFormLayout(dialog)
        
        # Saída de campo
        saida_select = QComboBox()
        cursor = self.db_manager.execute("SELECT id, nome FROM saidas_campo ORDER BY data DESC")
        if cursor:
            for row in cursor.fetchall():
                saida_select.addItem(row['nome'], row['id'])
        layout.addRow("Saída de Campo:", saida_select)
        
        # Responsável
        responsavel_input = QLineEdit()
        layout.addRow("Responsável:", responsavel_input)
        
        # Data de designação
        data_des_edit = QDateEdit(QDate.currentDate())
        data_des_edit.setCalendarPopup(True)
        data_des_edit.setDisplayFormat("dd/MM/yyyy")
        layout.addRow("Data de Designação:", data_des_edit)
        
        # Data de devolução
        data_dev_edit = QDateEdit(QDate.currentDate().addDays(15))
        data_dev_edit.setCalendarPopup(True)
        data_dev_edit.setDisplayFormat("dd/MM/yyyy")
        layout.addRow("Data de Devolução:", data_dev_edit)
        
        # Botões
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = QPushButton("Designar")
        save_button.setStyleSheet("background-color: #4CAF50; color: white;")
        save_button.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        
        layout.addRow("", buttons_layout)
        
        if dialog.exec():
            saida_campo_id = saida_select.currentData()
            responsavel = responsavel_input.text().strip()
            data_designacao = data_des_edit.date().toString("yyyy-MM-dd")
            data_devolucao = data_dev_edit.date().toString("yyyy-MM-dd")
            
            if not saida_campo_id:
                QMessageBox.warning(self, "Atenção", "Selecione uma saída de campo.")
                return
            
            if not responsavel:
                QMessageBox.warning(self, "Atenção", "Informe o responsável pela designação.")
                return
            
            # Criar a designação
            designacao = DesignacaoPredioVila(
                imovel_id=imovel.id,
                responsavel=responsavel,
                saida_campo_id=saida_campo_id,
                data_designacao=data_designacao,
                data_devolucao=data_devolucao,
                status="ativo"
            )
            
            if designacao.save(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Prédio/Vila designado com sucesso.")
                
                # Se há diálogo pai, fechá-lo para mostrar os detalhes atualizados
                if parent_dialog:
                    parent_dialog.accept()
                    self.ver_detalhes(imovel)
                else:
                    # Se não, apenas atualizar a lista
                    self.load_data()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível designar o prédio/vila.")
    
    def editar_designacao(self, designacao, parent_dialog=None):
        """Edita uma designação existente"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Designação")
        dialog.resize(400, 300)
        
        layout = QFormLayout(dialog)
        
        # Saída de campo
        saida_select = QComboBox()
        cursor = self.db_manager.execute("SELECT id, nome FROM saidas_campo ORDER BY data DESC")
        if cursor:
            for row in cursor.fetchall():
                saida_select.addItem(row['nome'], row['id'])
                if row['id'] == designacao.saida_campo_id:
                    saida_select.setCurrentText(row['nome'])
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
                
                # Se há diálogo pai, fechá-lo para mostrar os detalhes atualizados
                if parent_dialog:
                    parent_dialog.accept()
                    self.ver_detalhes(self.current_imovel)
                else:
                    # Se não, apenas atualizar a lista
                    self.load_data()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível atualizar a designação.")
    
    def concluir_designacao(self, designacao, parent_dialog=None):
        """Conclui uma designação existente"""
        reply = QMessageBox.question(
            self, "Confirmar Conclusão",
            f"Tem certeza que deseja concluir a designação deste {designacao.imovel_tipo}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if designacao.concluir(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Designação concluída com sucesso.")
                
                # Se há diálogo pai, fechá-lo para mostrar os detalhes atualizados
                if parent_dialog:
                    parent_dialog.accept()
                    self.ver_detalhes(self.current_imovel)
                else:
                    # Se não, apenas atualizar a lista
                    self.load_data()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível concluir a designação.")
    
    def excluir_designacao(self, designacao, parent_dialog=None):
        """Exclui uma designação existente"""
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a designação deste {designacao.imovel_tipo}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if designacao.delete(self.db_manager):
                QMessageBox.information(self, "Sucesso", "Designação excluída com sucesso.")
                
                # Se há diálogo pai, fechá-lo para mostrar os detalhes atualizados
                if parent_dialog:
                    parent_dialog.accept()
                    self.ver_detalhes(self.current_imovel)
                else:
                    # Se não, apenas atualizar a lista
                    self.load_data()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível excluir a designação.")
    
    @Slot()
    def cadastrar_predio_vila(self):
        """Cadastra um novo prédio ou vila"""
        # Validar os campos obrigatórios
        territorio_id = self.territorio_select.currentData()
        rua_id = self.rua_select.currentData()
        numero = self.numero_input.text().strip()
        tipo = self.tipo_select.currentText().lower()
        nome = self.nome_input.text().strip() or None
        unidades_text = self.unidades_input.text().strip()
        portaria = self.portaria_select.currentText().lower().replace(' ', '-')
        acesso = self.acesso_select.currentText().split(' ')[0].lower()
        observacoes = self.observacoes_input.toPlainText().strip() or None
        
        # Validações
        if not territorio_id:
            QMessageBox.warning(self, "Atenção", "Selecione um território.")
            return
        
        if not rua_id:
            QMessageBox.warning(self, "Atenção", "Selecione uma rua.")
            return
        
        if not numero:
            QMessageBox.warning(self, "Atenção", "Informe o número do imóvel.")
            return
        
        if not unidades_text or not unidades_text.isdigit():
            QMessageBox.warning(self, "Atenção", "O total de unidades deve ser um número válido.")
            return
        
        total_unidades = int(unidades_text)
        
        # Criar o imóvel
        imovel = Imovel(
            rua_id=rua_id,
            numero=numero,
            tipo=tipo,
            nome=nome,
            total_unidades=total_unidades,
            tipo_portaria=portaria,
            tipo_acesso=acesso,
            observacoes=observacoes
        )
        
        if imovel.save(self.db_manager):
            QMessageBox.information(self, "Sucesso", f"{tipo.capitalize()} cadastrado com sucesso.")
            # Limpar o formulário
            self.territorio_select.setCurrentIndex(0)
            self.rua_select.clear()
            self.rua_select.setEnabled(False)
            self.numero_input.clear()
            self.tipo_select.setCurrentIndex(0)
            self.nome_input.clear()
            self.unidades_input.clear()
            self.portaria_select.setCurrentIndex(0)
            self.acesso_select.setCurrentIndex(0)
            self.observacoes_input.clear()
            
            # Atualizar a lista
            self.load_data()
        else:
            QMessageBox.critical(self, "Erro", f"Não foi possível cadastrar o {tipo}.")
    
    @Slot()
    def on_filtro_changed(self):
        """Atualiza a lista quando os filtros são alterados"""
        self.filtro_predios = self.cb_predios.isChecked()
        self.filtro_vilas = self.cb_vilas.isChecked()
        self.filtro_concluidos = self.cb_concluidos.isChecked()
        self.filtro_designados = self.cb_designados.isChecked()
        
        self.load_data()
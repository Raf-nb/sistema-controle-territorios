# Sistema de Controle de Territórios

Este é um aplicativo desktop desenvolvido em Python com PySide6 e SQLite, projetado para o gerenciamento e controle de territórios.

## Instalação e Configuração

### Requisitos

- Python 3.8 ou superior
- PySide6 6.4.0 ou superior

### Passos para Instalação

1. Clone ou baixe este repositório para seu computador
2. Crie um ambiente virtual (recomendado):
   ```
   python -m venv venv
   ```
3. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instale os requisitos:
   ```
   pip install -r requirements.txt
   ```
5. Execute a aplicação:
   ```
   python main.py
   ```

## Recursos do Sistema

O sistema possui os seguintes recursos principais:

### 1. Dashboard

- Visão geral de estatísticas
- Contagens de territórios, imóveis atendidos e designações ativas
- Visualização rápida do território designado para hoje
- Lista de próximas designações e saídas de campo

### 2. Cadastro de Territórios

- Adicionar, editar e excluir territórios
- Gerenciar ruas em cada território
- Cadastrar imóveis por tipo (residencial, comercial, prédio ou vila)

### 3. Saídas de Campo

- Programar saídas de campo com data, dia da semana e horário
- Registrar um dirigente responsável pela saída

### 4. Designação de Territórios

- Designar territórios para saídas de campo específicas
- Designar prédios/vilas individualmente
- Definir datas de designação e devolução
- Gerenciar status das designações (ativas, concluídas)

### 5. Controle de Atendimentos

- Registrar e acompanhar atendimentos em imóveis residenciais e comerciais
- Visualizar progresso de atendimentos por território
- Filtrar visualizações por tipo de imóvel

### 6. Prédios e Vilas

- Cadastro especializado para prédios e vilas
- Gestão de unidades individuais (apartamentos/casas)
- Histórico de trabalho
- Designações específicas

## Como Usar

### Fluxo de Trabalho Básico

1. **Cadastre os territórios e suas ruas**
   - Acesse a tela "Cadastro de Territórios"
   - Adicione territórios e suas respectivas ruas
   - Cadastre imóveis em cada rua

2. **Configure saídas de campo**
   - Acesse a tela "Saídas de Campo"
   - Crie diferentes saídas de campo com horários e dias específicos

3. **Faça designações**
   - Acesse a tela "Designação"
   - Designe territórios para saídas de campo
   - Para prédios e vilas, use a aba específica para designação individual

4. **Registre atendimentos**
   - Utilize as telas "Controle de Atendimentos" ou "Prédios e Vilas"
   - Registre os atendimentos realizados em cada imóvel ou unidade

5. **Acompanhe o progresso**
   - Utilize o Dashboard para acompanhar estatísticas
   - Verifique o progresso dos atendimentos e as próximas designações

## Solução de Problemas

### Banco de Dados

O sistema utiliza um arquivo SQLite (`territorios.db`) para armazenar todos os dados. Se encontrar problemas de corrupção do banco de dados, você pode:

1. Fazer backup de seus dados (exportar, se possível)
2. Excluir o arquivo de banco de dados
3. Reiniciar a aplicação para criar um novo banco vazio

## Suporte e Manutenção

Este sistema foi desenvolvido para uso local e não requer conexão com a internet. Para manutenção:

- Faça backups periódicos do arquivo `territorios.db`
- Atualize o Python e as dependências conforme necessário

---

## Estrutura do Projeto

```
sistema_territorios/
├── database/               # Módulos para gerenciamento do banco de dados
│   ├── __init__.py
│   ├── db_manager.py       # Gerenciador de conexão com o banco
│   └── schema.sql          # Esquema SQL para criação das tabelas
├── views/                  # Interfaces gráficas
│   ├── __init__.py
│   ├── main_window.py      # Janela principal
│   ├── dashboard.py        # Tela inicial com estatísticas
│   ├── territorios.py      # Cadastro de territórios
│   ├── saidas_campo.py     # Gerenciamento de saídas de campo
│   ├── designacoes.py      # Designação de territórios
│   ├── view_territorios.py # Controle de atendimentos
│   └── predios_vilas.py    # Gerenciamento de prédios e vilas
├── models/                 # Modelos de dados
│   ├── __init__.py
│   ├── territorio.py       # Modelo de território
│   ├── imovel.py           # Modelo de imóvel
│   ├── saida_campo.py      # Modelo de saída de campo
│   ├── designacao.py       # Modelo de designação
│   └── atendimento.py      # Modelo de atendimento
├── main.py                 # Ponto de entrada do aplicativo
└── requirements.txt        # Dependências do projeto
```
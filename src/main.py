import sys
from pathlib import Path
import logging
import json
from dotenv import load_dotenv

# Adicione o diretório raiz do projeto ao PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

import uvicorn
from src.interfaces.web_interface import app
from src.utils.database import engine, Base

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_necessary_directories():
    directories = [
        root_dir / "src" / "data",
        root_dir / "static",
        root_dir / "logs"
    ]
    for directory in directories:
        directory.mkdir(exist_ok=True)
        logging.info(f"Ensured directory exists: {directory}")

def initialize_database():
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created")

def load_initial_data():
    checklist_path = root_dir / "src" / "data" / "checklist.json"
    if not checklist_path.exists():
        initial_checklist = {
            "Fase 1: Iniciação e Planejamento": {
                "Status": "Não Iniciado",
                "Tarefas": [
                    "Definir escopo detalhado do projeto",
                    "Criar cronograma preliminar",
                    "Identificar recursos necessários",
                    "Realizar análise de riscos inicial"
                ]
            },
            "Fase 2: Análise de Requisitos": {
                "Status": "Não Iniciado",
                "Tarefas": [
                "Coletar requisitos detalhados",
                "Realizar entrevistas com stakeholders",
                "Criar documentação de requisitos",
                "Validar requisitos com o cliente"
                ]
            },
            "Fase 3: Design e Arquitetura": {
                "Status": "Não Iniciado",
                "Tarefas": [
                "Desenvolver arquitetura do sistema",
                "Criar design de interface do usuário",
                "Definir estrutura de dados",
                "Realizar revisões de design"
                ]
            },
            "Fase 4: Desenvolvimento": {
                "Status": "Não Iniciado",
                "Tarefas": [
                "Configurar ambiente de desenvolvimento",
                "Implementar funcionalidades core",
                "Desenvolver interface do usuário",
                "Realizar testes unitários"
                ]
            },
            "Fase 5: Testes e Garantia de Qualidade": {
                "Status": "Não Iniciado",
                "Tarefas": [
                "Executar testes de integração",
                "Realizar testes de usabilidade",
                "Conduzir testes de segurança",
                "Resolver bugs e problemas identificados"
                ]
            },
            "Fase 6: Implantação": {
                "Status": "Não Iniciado",
                "Tarefas": [
                "Preparar ambiente de produção",
                "Realizar migração de dados (se aplicável)",
                "Executar implantação",
                "Conduzir testes pós-implantação"
                ]
            },
            "Fase 7: Pós-Lançamento e Manutenção": {
                "Status": "Não Iniciado",
                "Tarefas": [
                "Monitorar desempenho do sistema",
                "Coletar feedback dos usuários",
                "Implementar atualizações e melhorias",
                "Fornecer suporte contínuo"
                ]
            }
            }
            # ... (adicione outras fases conforme necessário)

        with open(checklist_path, 'w') as f:
            json.dump(initial_checklist, f, indent=2)
        logging.info("Initial checklist.json created")

if __name__ == "__main__":
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Lógica adicional de inicialização
    setup_logging()
    create_necessary_directories()
    initialize_database()
    load_initial_data()
    
    logging.info("Starting the server...")
    uvicorn.run("src.interfaces.web_interface:app", host="0.0.0.0", port=8000, reload=True)
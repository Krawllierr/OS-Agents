import json
from src.utils.database import get_db, DBProject

class AgentManager:
    def __init__(self):
        self.current_phase = 1
        self.agents = []

    def process_project(self, project_id):
        # Ler projeto.json
        with open('src/data/projeto.json', 'r') as f:
            projeto = json.load(f)

        # Preencher checklist.json
        self.fill_checklist(projeto)

        # Iniciar Fase 1
        self.start_phase(1)

    def fill_checklist(self, projeto):
        # Ler o arquivo checklist.json existente
        with open('src/data/checklist.json', 'r') as f:
            checklist = json.load(f)

        # Atualizar o checklist com informações do projeto
        checklist["Fase 1: Iniciação e Planejamento"]["Tarefas"].extend([
            f"Revisar escopo do projeto: {projeto['escopo_do_projeto']}",
            f"Analisar riscos potenciais: {projeto['riscos_potenciais']}",
            f"Definir cronograma baseado no prazo estimado de {projeto['prazo_estimado']}"
        ])

        # Salvar o checklist atualizado
        with open('src/data/checklist.json', 'w') as f:
            json.dump(checklist, f, indent=2)

    def start_phase(self, phase):
        print(f"Iniciando Fase {phase}")
        self.generate_agents()
        self.work_on_phase(phase)

    def generate_agents(self):
        self.agents = ["Agente Planejador", "Agente Analista de Riscos", "Agente de Cronograma"]
        print(f"Agentes gerados para a fase atual: {self.agents}")

    def work_on_phase(self, phase):
        print(f"Agentes trabalhando na Fase {phase}")
        # Simular trabalho dos agentes
        with open('src/data/checklist.json', 'r') as f:
            checklist = json.load(f)
        
        fase_atual = f"Fase {phase}: " + list(checklist.keys())[phase-1].split(": ")[1]
        tarefas = checklist[fase_atual]["Tarefas"]
        
        for tarefa in tarefas:
            print(f"Executando tarefa: {tarefa}")
            # Aqui você implementaria a lógica real de execução das tarefas
        
        checklist[fase_atual]["Status"] = "Concluído"
        
        with open('src/data/checklist.json', 'w') as f:
            json.dump(checklist, f, indent=2)

    def process_feedback(self, project_id, feedback):
        print(f"Processando feedback para o projeto {project_id}: {feedback}")
        # Aqui você implementaria a lógica de processamento do feedback
        
        self.current_phase += 1
        self.start_phase(self.current_phase)
        
        return self.current_phase

# Adicione outros métodos conforme necessário
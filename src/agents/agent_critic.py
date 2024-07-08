from src.agents.agent_base import AgentBase
from src.utils.ai_integration import get_ai_response

class AgentCritic(AgentBase):
    def __init__(self):
        super().__init__("Critic")

    def process(self, solution):
        # Analyze the proposed solution
        analysis = self.analyze_solution(solution)
        feedback = self.generate_feedback(analysis)
        return feedback

    def analyze_solution(self, solution):
        prompt = f"Analyze this solution critically: {solution}"
        analysis = get_ai_response(prompt)
        return analysis

    def generate_feedback(self, analysis):
        prompt = f"Based on this analysis, provide constructive feedback: {analysis}"
        feedback = get_ai_response(prompt)
        return feedback
from src.agents.agent_base import AgentBase
from src.utils.ai_integration import get_ai_response

class AgentResearcher(AgentBase):
    def __init__(self):
        super().__init__("Researcher")

    def process(self, query):
        research_results = self.conduct_research(query)
        summary = self.summarize_findings(research_results)
        return summary

    def conduct_research(self, query):
        prompt = f"Conduct a comprehensive research on: {query}"
        research_results = get_ai_response(prompt)
        return research_results

    def summarize_findings(self, research_results):
        prompt = f"Summarize these research findings concisely: {research_results}"
        summary = get_ai_response(prompt)
        return summary
import os
import sys
from pathlib import Path
from .urls import path
from .views import SimpleAgent
from .views import AgentGpt
from .views import AgentGem
from .agent import SimpleAgent
from .smartagent.smart_agent import SmartAgent
from .agents.agent_gpt import AgentGpt
from .agents.agent_cla import AgentCla
from .agents.agent_gem import AgentGem
from .agents.teacher_agent import TeacherAgent
from .agents.self_improve import SelfImproveLoop
from .agents.integrator_agent import IntegratorAgent
from .agents.tool_manager_agent import ToolManagerAgent
from .agents.director_agent import DirectorAgent
from .agents.composer_agent import ComposerAgent
from .agents.insider_agent import InsiderAgent
from .agents.marketer_agent import MarketerAgent
from .agents.investor_agent import InvestorAgent
from .agents.freelancer_agent import FreelancerAgent
from .agents.journalist_agent import JournalistAgent

sys.path.append('.')

agents = {
    "simple_agent": SimpleAgent(os.getenv('KIETEST'), 'https://api.kie.ai', 'gpt-6-astra'),
    "health_agent": AgentGpt(os.getenv('KIETEST')),
    "main_advisor": AgentGem(os.getenv('KIETEST')),
    "teacher": TeacherAgent(os.getenv('KIETEST')),
    "technician": ToolManagerAgent(os.getenv('KIETEST')),
    "integrator": IntegratorAgent(os.getenv('KIETEST')),
    "director": DirectorAgent(os.getenv('KIETEST')),
    "composer": ComposerAgent(os.getenv('KIETEST')),
    "insider": InsiderAgent(os.getenv('KIETEST')),
    "marketer": MarketerAgent(os.getenv('KIETEST')),
    "investor": InvestorAgent(os.getenv('KIETEST')),
    "freelancer": FreelancerAgent(os.getenv('KIETEST')),
    "journalist": JournalistAgent(os.getenv('KIETEST')),
    "smart_agent": SmartAgent(os.getenv('KIETEST'), 'https://api.kie.ai', 'grok-4-6'),
    "legal_agent": AgentCla(os.getenv('KIETEST'))
}

for name, agent in agents.items():
    print(f"\n🩺 [{name.upper()}] Self-Assess:")
    print(agent.self_assess())
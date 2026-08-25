import os, sys
from .views import SimpleAgent
from .views import AgentGpt
from .views import AgentGem

sys.path.append('.')

agents = {
    "simple_agent": SimpleAgent(os.getenv('KIETEST'), 'https://api.kie.ai', 'gpt-5-6-sol'),
    "health_agent": AgentGpt(os.getenv('KIETEST')),
    "main_advisor": AgentGem(os.getenv('KIETEST'))
}

for name, agent in agents.items():
    print(f"\n🩺 [{name.upper()}] Self-Assess:")
    print(agent.self_assess())
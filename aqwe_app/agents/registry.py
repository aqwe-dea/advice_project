import os
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence

AGENT_FACTORIES: Dict[str, Callable[[str], Any]] = {
    "main_advisor": lambda key: AgentGem(key),
    "teacher": lambda key: TeacherAgent(key),
    "technician": lambda key: ToolManagerAgent(key),
    "integrator": lambda key: IntegratorAgent(key),
    "director": lambda key: DirectorAgent(key),
    "composer": lambda key: ComposerAgent(key),
    "insider": lambda key: InsiderAgent(key),
    "marketer": lambda key: MarketerAgent(key),
    "freelancer": lambda key: FreelancerAgent(key),
    "journalist": lambda key: JournalistAgent(key),
    "simple_agent": lambda key: SimpleAgent(key),
    "smart_agent": lambda key: SmartAgent(key),
    "health_agent": lambda key: AgentGpt(key),
    "legal_agent": lambda key: AgentCla(key),
    # ... остальные
}

def get_all_agents(api_key: str) -> Dict[str, Any]:
    """Единая точка регистрации всех 14 агентов"""
    agents = {}
    for name, factory in AGENT_FACTORIES.items():
        try:
            agents[name] = factory(api_key)
        except Exception as e:
            logger.warning(f"Не удалось инициализировать агента {name}: {e}")
    return agents
    #return {name: factory(api_key) for name, factory in AGENT_FACTORIES.items()}
    #return {
    #    "main_advisor": AgentGem(api_key),
    #    "teacher": TeacherAgent(api_key),
    #    "technician": ToolManagerAgent(api_key),
    #    "integrator": IntegratorAgent(api_key),
    #    "director": DirectorAgent(api_key),
    #    "composer": ComposerAgent(api_key),
    #    "insider": InsiderAgent(api_key),
    #    "marketer": MarketerAgent(api_key),
    #    "investor": InvestorAgent(api_key),
    #    "freelancer": FreelancerAgent(api_key),
    #    "journalist": JournalistAgent(api_key),
    #    "simple_agent": SimpleAgent(api_key),
    #    "smart_agent": SmartAgent(api_key),
    #    "health_agent": AgentGpt(api_key),
    #    "legal_agent": AgentCla(api_key)
    #}

def get_agent(name: str, api_key: str) -> Optional[Any]:
    factory = AGENT_FACTORIES.get(name)
    if factory:
        try:
            return factory(api_key)
        except Exception as e:
            logger.error(f"Ошибка создания агента {name}: {e}")
    return None
import os
import logging
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from ..agent import SimpleAgent
from ..smartagent.smart_agent import SmartAgent
from .agent_gpt import AgentGpt
from .agent_cla import AgentCla
from .agent_gem import AgentGem
from .teacher_agent import TeacherAgent
from .integrator_agent import IntegratorAgent
from .tool_manager_agent import ToolManagerAgent
from .director_agent import DirectorAgent
from .composer_agent import ComposerAgent
from .insider_agent import InsiderAgent
from .marketer_agent import MarketerAgent
from .investor_agent import InvestorAgent
from .freelancer_agent import FreelancerAgent
from .journalist_agent import JournalistAgent
from .content_maker_agent import ContentMakerAgent
from .auditor_checker_agent import AuditorCheckerAgent
from .partner_representative_agent import PartnerRepresentativeAgent
from .lead_manager_agent import LeadManagerAgent
from .manager_briefcase_assets_agent import ManagerBriefcaseAssetsAgent
from .seller_dealer_agent import SellerDealerAgent
from .author_agent import AuthorAgent

logger = logging.getLogger(__name__)

AGENT_REGISTRY = {
    "Content-Maker": {
        "name": "Content-Maker",
        "role": "Элитный цифровой художник и маркетолог",
        "description": "Создает высококачественный визуальный контент (SVG, HTML, инфографика, 3D-спецификации). Владеет методами: _vector_maket, _vector_collage, _image_into_3d, _made_sketch, _one_business_page, generate_image_pipeline, edit_image_pipeline.",
        "status": "active"
    },
    "Author": {
        "name": "Author",
        "role": "Создатель и упаковщик авторского контента",
        "description": "Пишет книги, курсы, сценарии и упаковывает их для монетизации на платформах Sponsr/Gumroad. Превращает идеи в цифровые активы с высокой маржой.",
        "status": "active"
    },
    "Auditor-Checker": {
        "name": "Auditor-Checker",
        "role": "Эксперт по аудиту и безопасности",
        "description": "Проводит глубокий анализ кода, текстов и бизнес-профилей. Находит риски, уязвимости и точки роста. Владеет методами: _check_code, _check_document, _check_text.",
        "status": "active"
    },
    "Leadership-Gem": {
        "name": "Leadership-Gem",
        "role": "Руководство Старшая Гемини",
        "description": "Возможности: личное общение, дизайнер, нутрициолог, бухгалтер, художник.",
        "status": "active"
    },
    "Administration-Cla": {
        "name": "Administration-Cla",
        "role": "Администрация Главный Клод",
        "description": "Возможности: деловое общение, изучение, оркестрация, стратегия, художество.",
        "status": "active"
    },
    "Management-Gpt": {
        "name": "Management-Gpt",
        "role": "Управление Основной ДжиПиТи",
        "description": "Возможности: корпоративное общение, исследование, планирование, улучшение, рисование",
        "status": "active"
    },
    "Smart-Kimi": {
        "name": "Smart-Kimi",
        "role": "Интеллигенция Умная Кими",
        "description": "Возможности: интеллектуальное общение, цели, задачи, решения, проверка.",
        "status": "active"
    },
    "Simple-Gpt": {
        "name": "Simple-Gpt",
        "role": "Естественность Простой ДжиПиТи",
        "description": "Возможности: естественное общение, инструктаж, документалистика, диагностика.",
        "status": "active"
    },
    "Partner-Representative": {
        "name": "Partner-Representative",
        "role": "Партнер Представитель",
        "description": "Возможности: пишет экспертные, глубокие, полезные статьи.",
        "status": "active"
    },
    "Lead-Manager": {
        "name": "Lead-Manager",
        "role": "Управляющий Заявками",
        "description": "Возможности: квалифицирует заявки, анализирует описание потенциального клиента.",
        "status": "active"
    },
    "Manager-Briefcase-Assets": {
        "name": "Manager-Briefcase-Assets",
        "role": "Портфельный Управляющий",
        "description": "Возможности: анализирует портфель активов, выявляет риски и предлагает ребалансировку.",
        "status": "active"
    },
    "Seller-Dealer": {
        "name": "Seller-Dealer",
        "role": "Продавец Дилер",
        "description": "Возможности: создает продающие презентации товаров или услуг.",
        "status": "active"
    },
    "Teacher": {
        "name": "Teacher",
        "role": "Учительница",
        "description": "Возможности: отвечает на вопросы, выдаёт справочные материалы, адаптирует сложность.",
        "status": "active"
    },
    "Technician-Tool": {
        "name": "Technician-Tool",
        "role": "Техник Специалист по инструментам",
        "description": "Возможности: управляет реестром инструментов, динамически вызывает функции.",
        "status": "active"
    },
    "Integrator": {
        "name": "Integrator",
        "role": "Интегратор программист",
        "description": "Возможности: генерирует код обёрток для API, сервисов, вебхуков.",
        "status": "active"
    },
    "Director": {
        "name": "Director",
        "role": "Режиссер",
        "description": "Возможности: создаёт сценарии, концепции видео, тренд-анализ, и видеоролики.",
        "status": "active"
    },
    "Composer": {
        "name": "Composer",
        "role": "Композитор",
        "description": "Возможности: генерирует музыкальные концепции, и создает музыку.",
        "status": "active"
    },
    "Insider": {
        "name": "Insider",
        "role": "Инсайдер",
        "description": "Возможности: агрегация открытых данных, OSINT, структурирование информации, и поиск.",
        "status": "active"
    },
    "Marketer": {
        "name": "Marketer",
        "role": "Маркетолог",
        "description": "Возможности: написание постов, авто-постинг, A/B тесты, аналитика вовлечения.",
        "status": "active"
    },
    "Freelancer": {
        "name": "Freelancer",
        "role": "Фрилансер",
        "description": "Возможности: аудит портфолио и профиля, поиск заказов, авто-отклики, управление задачами.",
        "status": "active"
    },
    "Journalist": {
        "name": "Journalist",
        "role": "Журналист",
        "description": "Возможности: публицистика, журналистика, работа с новостями и событиями.",
        "status": "active"
    },
    "Investor": {
        "name": "Investor",
        "role": "Инвестор",
        "description": "Возможности: скоринг активов, анализ рисков, рекомендации.",
        "status": "active"
    },
    # ... добавь сюда агентов по аналогии ...
}

AGENT_FACTORIES: Dict[str, Callable[[str], Any]] = {
    "Leadership-Gem": lambda key: AgentGem(key),
    "Teacher": lambda key: TeacherAgent(key),
    "Technician-Tool": lambda key: ToolManagerAgent(key),
    "Integrator": lambda key: IntegratorAgent(key),
    "Director": lambda key: DirectorAgent(key),
    "Composer": lambda key: ComposerAgent(key),
    "Insider": lambda key: InsiderAgent(key),
    "Marketer": lambda key: MarketerAgent(key),
    "Freelancer": lambda key: FreelancerAgent(key),
    "Journalist": lambda key: JournalistAgent(key),
    "Simple-Gpt": lambda key: SimpleAgent(key, base_url='https://api.kie.ai', model='gpt-6-1-sol'),
    "Smart-Kimi": lambda key: SmartAgent(key, base_url='https://api.kie.ai', model='kimi-k3'),
    "Management-Gpt": lambda key: AgentGpt(key),
    "Administration-Cla": lambda key: AgentCla(key),
    "Content-Maker": lambda key: ContentMakerAgent(key),
    "Auditor-Checker": lambda key: AuditorCheckerAgent(key),
    "Partner-Representative": lambda key: PartnerRepresentativeAgent(key),
    "Lead-Manager": lambda key: LeadManagerAgent(key),
    "Manager-Briefcase-Assets": lambda key: ManagerBriefcaseAssetsAgent(key),
    "Seller-Dealer": lambda key: SellerDealerAgent(key),
    "Author": lambda key: AuthorAgent(key),
    "Investor": lambda key: InvestorAgent(key)
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

def get_description_agent(agent_name: str) -> str:
    """Возвращает подробное описание возможностей агента из реестра."""
    agent = AGENT_REGISTRY.get(agent_name)
    if agent:
        return f"Агент: {agent['name']}. Роль: {agent['role']}. Возможности: {agent['description']}"
    return f"Агент '{agent_name}' не найден в реестре или описание отсутствует."    
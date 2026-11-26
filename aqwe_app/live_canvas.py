import os
import subprocess
import json
import logging
import uuid
from pathlib import Path
from datetime import datetime
from uuid import UUID
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from abc import ABC, abstractmethod
from .generators.base import BaseGenerator
from .generators.image_generator import ImageGenerator
from .generators.code_generator import CodeGenerator
from .generators.video_generator import VideoGenerator
from .generators.voice_generator import VoiceGenerator
from .generators.liveimage_generator import LiveimageGenerator
from .generators.character_generator import CharacterGenerator
from .generators.instrumental_generator import InstrumentalGenerator
from .generators.image_edit import ImageEdit
from .generators.flux_gen import FluxGen
from .generators.minimax_gen import MinimaxGen
from .generators.wan_gen import WanGen
from .generators.vidu_gen import ViduGen
from .generators.seedance_gen import SeedanceGen
from .generators.geminitts_gen import GeminittsGen
from .generators.omnihuman_gen import OmnihumanGen
from .generators.volcengine_gen import VolcengineGen

logger = logging.getLogger(__name__)

class LiveMultimodalWorkspace:
    """Единое пространство для совместного творчества"""
    
    #def __init__(self, session_id: str):
    #    self.session_id = session_id
    #    self.artifacts = {}  # {artifact_id: {"type": "image|text|diagram", "content": ..., "metadata": ...}}
    def __init__(self, session_id: str, api_key: str, base_url: str = "https://api.kie.ai"):
        self.session_id = session_id
        self.api_key = api_key      # <--- Сохраняем ключ для генераторов
        self.base_url = base_url    # <--- Сохраняем URL
        self.artifacts = {}
    def create_artifact(
        self, 
        artifact_type: str, 
        prompt: str,
        image_urls: list,
        video_urls: list,
        audio_urls: list, 
        file_urls: list,
        link_urls: list,
        input_urls: list,
        character_ids: list,
        text: str = "", 
        text2: str = "",
        scene: str = "",
        sample_context: str = "",
        image_url: str = "", 
        audio_url: str = "",
        first_frame_url: str = "",
        last_frame_url: str = "",
        elements_url: str = "",
        voices_url: str = "",
        generator: str = "ImageGenerator", 
        language: str = "python", 
        include_comments: bool = True
    ) -> Dict[str, Any]:
        """Создать артефакт через соответствующий генератор"""
        artifact_id = f"{artifact_type}_{uuid.uuid4().hex[:8]}"
        result = None # Инициализируем переменную, чтобы избежать ошибок

        try:
            if generator == "ImageGenerator":
                gen = ImageGenerator(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt)
                result = res_dict.get('image_url') or res_dict
            elif generator == "InstrumentalGenerator":
                gen = InstrumentalGenerator(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt)
                result = res_dict.get('instrumental_url') or res_dict
            elif generator == "VideoGenerator":
                gen = VideoGenerator(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt, image_urls=image_urls, video_urls=video_urls, elements_url=elements_url, voices_url=voices_url)
                result = res_dict.get('video_url') or res_dict
            elif generator == "CodeGenerator":
                gen = CodeGenerator(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt, language=language, include_comments=include_comments)
                result = res_dict.get('code') or res_dict
            elif generator == "VoiceGenerator":
                gen = VoiceGenerator(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(text=text, scene=scene, sample_context=sample_context)
                result = res_dict.get('audio_url') or res_dict
            elif generator == "LiveimageGenerator":
                gen = LiveimageGenerator(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt, image_urls=image_urls, first_frame_url=first_frame_url, last_frame_url=last_frame_url, video_list=video_urls, character_ids=character_ids)
                result = res_dict.get('liveimage_url') or res_dict
            elif generator == "CharacterGenerator":
                gen = CharacterGenerator(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt, image_url=image_url, audio_url=audio_url)
                result = res_dict.get('character_url') or res_dict
            elif generator == "ImageEdit":
                gen = ImageEdit(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt, input_urls=input_urls)
                result = res_dict.get('edit_url') or res_dict
            elif generator == "FluxGen":
                gen = FluxGen(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt)
                result = res_dict.get('flux_url') or res_dict
            elif generator == "MinimaxGen":
                gen = MinimaxGen(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt, image_urls=image_urls)
                result = res_dict.get('minimax_url') or res_dict
            elif generator == "WanGen":
                gen = WanGen(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt, first_frame_url=first_frame_url, last_frame_url=last_frame_url, reference_image_urls=image_urls, reference_link_urls=link_urls, reference_audio_urls=audio_urls, reference_video_urls=video_urls, reference_file_urls=file_urls)
                result = res_dict.get('wan_url') or res_dict
            elif generator == "ViduGen":
                gen = ViduGen(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt, reference_image_urls=image_urls, reference_audio_urls=audio_urls)
                result = res_dict.get('vidu_url') or res_dict
            elif generator == "SeedanceGen":
                gen = SeedanceGen(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt, reference_image_urls=image_urls, reference_video_urls=video_urls, reference_audio_urls=audio_urls)
                result = res_dict.get('seedance_url') or res_dict
            elif generator == "GeminittsGen":
                gen = GeminittsGen(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(text1=text, text2=text2)
                result = res_dict.get('geminitts_url') or res_dict
            elif generator == "OmnihumanGen":
                gen = OmnihumanGen(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(prompt=prompt, audio_url=audio_url, image_urls=image_urls)
                result = res_dict.get('omnihuman_url') or res_dict
            elif generator == "VolcengineGen":
                gen = VolcengineGen(api_key=self.api_key, base_url=self.base_url)
                res_dict = gen.generate(video_url=video_url, audio_url=audio_url)
                result = res_dict.get('volcengine_url') or res_dict
            # ... (добавь остальные по аналогии) ...
            else:
                result = f"Генератор {generator} временно недоступен или не указан."

            # Сохраняем в холст ТОЛЬКО если есть результат
            if result:
                self.artifacts[artifact_id] = {
                    "type": artifact_type,
                    "content": result,
                    "created_at": datetime.utcnow().isoformat(),
                    "prompt": prompt
                }

            return {
                "artifact_id": artifact_id, 
                "status": "created" if result else "failed", 
                "result": result
            }
        except Exception as e:
            logger.error(f"Ошибка создания артефакта: {e}")
            return {"artifact_id": artifact_id, "status": "error", "error": str(e)}

    def edit_artifact(self, artifact_id: str, instruction: str) -> str:
        """Редактировать существующий артефакт"""
        if artifact_id not in self.artifacts:
            return json.dumps({"error": "Артефакт не найден"}, ensure_ascii=False)
        
        artifact = self.artifacts[artifact_id]
        # Здесь можно подключить LLM для рефакторинга контента 
        updated_content = refine_content(artifact["content"], instruction)
        artifact["content"] = updated_content
        artifact["edited_at"] = datetime.utcnow().isoformat()
        
        return json.dumps({"artifact_id": artifact_id, "status": "updated"}, ensure_ascii=False)
    
    def render_canvas(self) -> str:
        """Вернуть текущее состояние холста для отображения"""
        return json.dumps({
            "session_id": self.session_id,
            "artifacts": list(self.artifacts.values()),
            "timestamp": datetime.utcnow().isoformat()
        }, ensure_ascii=False)
import os
import subprocess
import json
import logging
import uuid
from pathlib import Path
from datetime import datetime
from uuid import UUID
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from .generators.image_generator import ImageGenerator
from .generators.code_generator import CodeGenerator
from .generators.video_generator import VideoGenerator
from .generators.voice_generator import VoiceGenerator
from .generators.liveimage_generator import LiveimageGenerator
from .generators.character_generator import CharacterGenerator
from .generators.instrumental_generator import InstrumentalGenerator
from .generators.image_edit import ImageEdit

logger = logging.getLogger(__name__)

class LiveMultimodalWorkspace:
    """Единое пространство для совместного творчества"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.artifacts = {}  # {artifact_id: {"type": "image|text|diagram", "content": ..., "metadata": ...}}
    
    def create_artifact(
        self, 
        artifact_type: str, 
        prompt: str, 
        text: str = "", 
        image_url: str = "", 
        audio_url: str = "", 
        input_urls: str = "", 
        generator: str = "ImageGenerator", 
        language: str = "python", 
        include_comments: bool = True
    ) -> Dict[str, Any]:
        """Создать артефакт через соответствующий генератор"""
        artifact_id = f"{artifact_type}_{uuid.uuid4().hex[:8]}"
        result = None # Инициализируем переменную, чтобы избежать ошибок

        try:
            if generator == "ImageGenerator":
                # Предполагаем, что у генератора есть метод generate, возвращающий dict
                res_dict = ImageGenerator.generate(prompt=prompt) 
                result = res_dict.get('image_url') or res_dict
            elif generator == "InstrumentalGenerator":
                res_dict = InstrumentalGenerator.generate(prompt=prompt)
                result = res_dict.get('instrumental_url')
            elif generator == "VideoGenerator":
                res_dict = VideoGenerator.generate(prompt=prompt)
                result = res_dict.get('video_url')
            elif generator == "CodeGenerator":
                res_dict = CodeGenerator.generate(prompt=prompt, language=language, include_comments=include_comments)
                result = res_dict.get('code')
            elif generator == "VoiceGenerator":
                res_dict = VoiceGenerator.generate(text=text)
                result = res_dict.get('audio_url')
            elif generator == "LiveimageGenerator":
                res_dict = LiveimageGenerator.generate(prompt=prompt, image_url=image_url)
                result = res_dict.get('liveimage_url')
            elif generator == "CharacterGenerator":
                res_dict = CharacterGenerator.generate(prompt=prompt, image_url=image_url, audio_url=audio_url)
                result = res_dict.get('character_url')
            elif generator == "ImageEdit":
                res_dict = ImageEdit.generate(prompt=prompt, input_urls=input_urls)
                result = res_dict.get('edit_url')
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

    #def create_artifact(
    #    self,
    #    artifact_type: str,
    #    prompt: str,
    #    text: str,
    #    image_url: str,
    #    audio_url: str,
    #    input_urls: str,
    #    generator: str,
    #    language: str = "python",
    #    include_comments: bool = True
    #) -> Dict[str, Any]:
    #    """Создать артефакт через соответствующий генератор"""
    #    artifact_id = f"{artifact_type}_{uuid.uuid4().hex[:8]}"

    #    if generator == "ImageGenerator":
    #        result = ImageGenerator.generate(self, prompt)  # твой существующий генератор
    #        return result
        #if generator == "ImageGenerator":
        #    result = ImageGenerator.generate(self, prompt=prompt)  # твой существующий генератор
            #result = image.get('image_url')
        #    return result
    #    if generator == "InstrumentalGenerator":
    #        instrumental = InstrumentalGenerator.generate(self, prompt)
    #        result = instrumental.get('instrumental_url')
    #    if generator == "VideoGenerator":
    #        video = VideoGenerator.generate(self, prompt)
    #        result = video.get('video_url')
    #    if generator == "CodeGenerator":
    #        code = CodeGenerator.generate(self, prompt, language, include_comments)
    #        result = code.get('code')
    #    if generator == "VoiceGenerator":
    #        audio = VoiceGenerator.generate(self, text)
    #        result = audio.get('audio_url')
    #    if generator == "LiveimageGenerator":
    #        liveimage = LiveimageGenerator.generate(self, prompt, image_url)
    #        result = liveimage.get('liveimage_url')
    #    if generator == "CharacterGenerator":
    #        character = CharacterGenerator.generate(self, prompt, image_url, audio_url)
    #        result = character.get('character_url')
    #    if generator == "ImageEdit":
    #        edit = ImageEdit.generate(self, prompt, input_urls)
    #        result = edit.get('edit_url')
        #elif generator == "text_generator":
        #    result = generate_text(prompt)
        
    #    self.artifacts[artifact_id] = {
    #        "type": artifact_type,
    #        "content": result,
    #        "created_at": datetime.utcnow().isoformat(),
    #        "prompt": prompt
    #    }

    #    return json.dumps({
    #        "artifact_id": artifact_id, 
    #        "status": "created", 
    #        "result": result
    #    }, ensure_ascii=False)
    
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
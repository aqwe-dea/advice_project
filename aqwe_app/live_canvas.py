import os
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence

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
        generator: str, 
        language: str, 
        include_comments: str,
        text: str,
        image_url: str,
        audio_url: str,
        input_urls: str
    ) -> str:

        """Создать артефакт через соответствующий генератор"""
        if generator == "ImageGenerator":
            result = generate(prompt)  # твой существующий генератор
        elif generator == "InstrumentalGenerator":
            result = generate(prompt)
        elif generator == "VideoGenerator":
            result = generate(prompt)
        elif generator == "CodeGenerator":
            result = generate(prompt, language, include_comments)
        elif generator == "VoiceGenerator":
            result = generate(text)
        elif generator == "LiveimageGenerator":
            result = generate(prompt, image_url)
        elif generator == "CharacterGenerator":
            result = generate(prompt, image_url, audio_url)
        elif generator == "ImageEdit":
            result = generate(prompt, input_urls)
        #elif generator == "text_generator":
        #    result = generate_text(prompt)
        
        artifact_id = f"{artifact_type}_{uuid.uuid4().hex[:8]}"
        self.artifacts[artifact_id] = {
            "type": artifact_type,
            "content": result,
            "created_at": datetime.utcnow().isoformat(),
            "prompt": prompt
        }
        return json.dumps({"artifact_id": artifact_id, "status": "created"}, ensure_ascii=False)
    
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
import os
import json
import requests
from typing import List, Optional, Dict
from bs4 import BeautifulSoup

def _hyperbrowse(self, url: str, query: str = None) -> str:
    """Инструмент: посещение веб-страницы и извлечение контента."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
            
        soup = BeautifulSoup(response.text, 'html.parser')
            
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
            
        if query:
            lines = text.split('\n')
            relevant = [line for line in lines if query.lower() in line.lower()]
            text = '\n'.join(relevant[:10])  
        
        return f"[Hyperbrowse] {url}:\n{text[:1000]}..."  
    except Exception as e:
        return f"[Hyperbrowse Error] {str(e)}"
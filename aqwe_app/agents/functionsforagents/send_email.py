import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, IO, TYPE_CHECKING, Any, Type, Tuple, Union, Mapping, TypeVar, Callable, Iterator, Optional, Sequence
from uuid import UUID
from pathlib import Path
from abc import abstractmethod

def send_email(to: str, subject: str, body: str) -> str:
    """Отправляет email через SMTP. Требует env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS. function for send email"""
    try:
        host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        port = int(os.getenv("SMTP_PORT", "587"))
        user = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PASS")
        
        if not all([user, password]):
            return json.dumps({"error": "Не настроены SMTP_USER и SMTP_PASS"}, ensure_ascii=False)
            
        msg = MIMEMultipart()
        msg["From"] = user
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
            
        return json.dumps({"status": "success", "to": to, "subject": subject}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Ошибка отправки email: {str(e)}"}, ensure_ascii=False)
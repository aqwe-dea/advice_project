import requests 
import time 
from datetime import datetime, timezone 

def check_network_connection( url="https://www.google.com", timeout=5 ):
    """ 
        Проверка доступности интернет-соединения. 
        Делает GET-запрос и возвращает состояние сети. 
    """ 
    result = { 
        "connected": False, 
        "url": url, 
        "status_code": None, 
        "response_time_ms": None, 
        "checked_at": datetime.now(timezone.utc).isoformat(), 
        "error": None 
    } 
    
    try: 
        start = time.time() 
        response = requests.get( 
            url, 
            timeout=timeout 
        ) 
        end = time.time() 
        result["response_time_ms"] = round( (end - start) * 1000, 2 ) 
        result["status_code"] = response.status_code 
        if response.status_code < 500: 
            result["connected"] = True 
    except requests.exceptions.Timeout: 
        result["error"] = "Connection timeout" 
    except requests.exceptions.ConnectionError: 
        result["error"] = "No internet connection" 
    except requests.exceptions.RequestException as e: 
        result["error"] = str(e) 
    return result
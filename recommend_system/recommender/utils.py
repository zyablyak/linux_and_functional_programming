import json
import csv
from datetime import datetime
from functools import wraps
import time
import os

def timer(func):
    """Декоратор для измерения времени выполнения"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} выполнена за {end-start:.4f} секунд")
        return result
    return wrapper


def save_recommendations(recommendations, filepath):
    """Сохранение рекомендаций в файл"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Начинаем сохранение {len(recommendations)} книг в {filepath}")

    clean_recommendations = []
    for book in recommendations:
        clean_book = {
            'title': book.get('title', ''),
            'author': book.get('author', ''),
            'genre': book.get('genre', ''),
            'year': book.get('year', ''),
            'score': book.get('score', 0),
            'description': book.get('description', '')[:200],
            'saved_at': timestamp
        }
        clean_recommendations.append(clean_book)
    
    data_to_save = {
        'timestamp': timestamp,
        'total_selected': len(clean_recommendations),
        'reading_list': clean_recommendations
    }

    try:
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Создана директория: {directory}")
    except Exception as e:
        print(f"Ошибка при создании директории: {e}")
        raise
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        print(f"✅ Успешно сохранено {len(clean_recommendations)} книг в {filepath}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении в {filepath}: {e}")
        raise


def load_recommendations(filepath):
    """Загрузка сохраненных рекомендаций"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def chunked(iterable, size):
    """Разбиение итератора на чанки фиксированного размера"""
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]
import json
import re
from functools import lru_cache

def validate_book_data(book):
    """Валидация данных книги"""
    required_fields = ['title', 'author', 'genre']
    return all(book.get(field) for field in required_fields)


def text_to_lemmas(text):
    """Обработка текста"""
    if not text:
        return []
    words = re.findall(r'\w+', text.lower())
    return words


def load_books(file_path: str):
    """Загрузка данных о книгах с обработкой ошибок"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            books = json.load(f)

        valid_books = []
        for book in books:
            if validate_book_data(book):
                description = book.get('description', '')
                book['description_lemmas'] = text_to_lemmas(description)
                valid_books.append(book)
            else:
                print(f"Пропущена книга с неполными данными: {book.get('title', 'Unknown')}")
        
        print(f"Загружено {len(valid_books)} валидных книг")
        return valid_books
        
    except FileNotFoundError:
        print(f"Файл {file_path} не найден")
        return []
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
        return []
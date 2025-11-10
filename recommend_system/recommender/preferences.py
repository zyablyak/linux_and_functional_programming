import re
from functools import reduce
from operator import or_

try:
    from pymorphy3 import MorphAnalyzer
    morph = MorphAnalyzer()
    PYMOEPHY_AVAILABLE = True
    print("pymorphy3 успешно загружен")
except ImportError:
    morph = None
    PYMOEPHY_AVAILABLE = False
    print("Предупреждение: pymorphy3 не установлен, используется упрощенная обработка текста")

def normalize_text(text):
    """Нормализация текста для сравнения с обработкой pymorphy3 если доступен"""
    if not text:
        return ''
    
    if PYMOEPHY_AVAILABLE:
        try:
            words = re.findall(r'\w+', text.lower())
            normalized_words = []
            for word in words:
                parsed = morph.parse(word)[0]
                normalized_words.append(parsed.normal_form)
            return ' '.join(normalized_words)
        except Exception as e:
            print(f"Ошибка при нормализации текста: {e}")
            return ' '.join(re.findall(r'\w+', text.lower()))
    else:
        return ' '.join(re.findall(r'\w+', text.lower()))


def validate_user_input(genres, authors, keywords):
    """Валидация пользовательского ввода"""
    errors = []
    if not genres and not authors and not keywords:
        errors.append("Заполните хотя бы одно поле: выберите жанры, авторов или введите ключевые слова")
        
    if len(keywords) > 10:
        errors.append("Слишком много ключевых слов (максимум 10)")

    short_keywords = [kw for kw in keywords if len(kw) < 2]
    if short_keywords:
        errors.append(f"Слишком короткие ключевые слова: {', '.join(short_keywords)} (минимум 2 символа)")
    
    return errors


def process_preferences(genres, authors, keywords_text):
    """Обработка пользовательских предпочтений"""
    genres_set = {g.strip() for g in genres if g.strip()}
    authors_set = {a.strip() for a in authors if a.strip()}

    keywords_clean = []
    if keywords_text:
        keywords_split = re.split(r'[,;]\s*|\s+', keywords_text)
        keywords_clean = [normalize_text(k.strip()) for k in keywords_split if k.strip()]
    
    return {
        "genres": genres_set,
        "authors": authors_set,
        "keywords": keywords_clean
    }
from functools import partial
from operator import itemgetter

def compute_match_score(book, preferences):
    """Вычисление рейтинга соответствия"""
    score = 0

    if book.get('genre') in preferences['genres']:
        score += 3

    if book.get('author') in preferences['authors']:
        score += 3

    description_lemmas = set(book.get('description_lemmas', []))
    keyword_matches = sum(1 for kw in preferences['keywords'] if kw in description_lemmas)
    score += min(keyword_matches * 2, 6)
    
    return score


def filter_books(books, min_year=None, genres=None, authors=None):
    """Функциональная фильтрация книг"""
    filters = []
    
    if min_year is not None:
        filters.append(lambda book: book.get('year', 0) >= min_year)
    
    if genres:
        filters.append(lambda book: book.get('genre') in genres)
    
    if authors:
        filters.append(lambda book: book.get('author') in authors)

    def apply_filters(book):
        return all(f(book) for f in filters)
    
    return filter(apply_filters, books)


def sort_books(books, key='score', reverse=True):
    """Сортировка книг по различным критериям"""
    sort_keys = {
        'score': lambda x: x.get('score', 0),
        'title': lambda x: x.get('title', '').lower(),
        'year': lambda x: x.get('year', 0),
        'author': lambda x: x.get('author', '').lower()
    }
    
    key_func = sort_keys.get(key, sort_keys['score'])
    return sorted(books, key=key_func, reverse=reverse)


def recommend_books(books, preferences, min_year=None, sort_by='score'):
    """Основная функция рекомендаций с интеллектуальной фильтрацией"""
    scored_books = []
    strict_genre = preferences.get('strict_genre', False)
    
    filter_by_authors = bool(preferences['authors'])
    
    for book in books:
        if min_year is not None and book.get('year', 0) < min_year:
            continue

        if filter_by_authors and book.get('author') not in preferences['authors']:
            continue

        if strict_genre and preferences['genres']:
            if book.get('genre') not in preferences['genres']:
                continue
                
        score = compute_match_score(book, preferences)

        if not strict_genre or (strict_genre and score > 0):
            scored_books.append({**book, 'score': score})

    if sort_by == 'score':
        return sorted(scored_books, key=lambda x: x['score'], reverse=True)
    elif sort_by == 'title':
        return sorted(scored_books, key=lambda x: x.get('title', '').lower())
    elif sort_by == 'title_asc':
        return sorted(scored_books, key=lambda x: x.get('title', '').lower(), reverse=True)
    elif sort_by == 'year':
        return sorted(scored_books, key=lambda x: x.get('year', 0), reverse=True)
    elif sort_by == 'year_asc':
        return sorted(scored_books, key=lambda x: x.get('year', 0))
    elif sort_by == 'author':
        return sorted(scored_books, key=lambda x: x.get('author', '').lower())
    else:
        return sorted(scored_books, key=lambda x: x['score'], reverse=True)
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
import json
import sys
from functools import wraps

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from recommender.data_loader import load_books
from recommender.preferences import process_preferences, validate_user_input, normalize_text
from recommender.recommendations import recommend_books
from recommender.utils import save_recommendations


app = Flask(__name__)
app.secret_key = 'book_recommendation_system_secret_key_2024'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'books.json')

try:
    books = load_books(DATA_PATH)
    print(f"Загружено {len(books)} книг")
except Exception as e:
    print(f"Ошибка загрузки данных: {e}")
    books = []

genres_all = sorted({book.get('genre', '') for book in books if book.get('genre')})
authors_all = sorted({book.get('author', '') for book in books if book.get('author')})
years = [book.get('year') for book in books if book.get('year') is not None]
min_year_global = min(years) if years else 1900
max_year_global = max(years) if years else 2023


def handle_errors(f):
    """Декоратор для обработки ошибок в маршрутах Flask"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return f"Ошибка: {str(e)}", 500
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
@handle_errors
def index():
    """Главная страница с формой выбора предпочтений"""
    if request.method == 'POST':
        genres = request.form.getlist('genres')
        authors = request.form.getlist('authors')
        keywords_text = request.form.get('keywords', '')
        min_year = request.form.get('min_year', '').strip()
        sort_by = request.form.get('sort_by', 'score')
        strict_genre = request.form.get('strict_genre') == 'true'
        
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]

        validation_errors = validate_user_input(genres, authors, keywords)
        if validation_errors:
            return render_template(
                'index.html',
                genres_all=genres_all,
                authors_all=authors_all,
                min_year=min_year_global,
                max_year=max_year_global,
                total_books=len(books),
                errors=validation_errors
            )

        preferences = process_preferences(genres, authors, keywords_text)
        preferences['strict_genre'] = strict_genre
 
        min_year_filter = int(min_year) if min_year and min_year.isdigit() else None

        recommended = recommend_books(books, preferences, min_year_filter, sort_by)

        session['last_recommendations'] = recommended
        session['sort_by'] = sort_by
        session['strict_genre'] = strict_genre
        session.modified = True
        
        print(f"Сохранено в сессию: {len(recommended)} книг")
        
        return render_template('results.html', 
                             books=recommended, 
                             preferences=preferences,
                             total_books=len(books),
                             sort_by=sort_by,
                             strict_genre=strict_genre)

    return render_template(
        'index.html',
        genres_all=genres_all,
        authors_all=authors_all,
        min_year=min_year_global,
        max_year=max_year_global,
        total_books=len(books)
    )


@app.route('/save', methods=['POST'])
@handle_errors
def save():
    """Сохраняет выбранные книги в список для чтения"""
    selected_indices = request.form.getlist('selected_books')
    
    print(f"Получены индексы: {selected_indices}")
    
    if not selected_indices:
        return "Не выбрано ни одной книги для сохранения", 400

    selected_books = []
    for idx in selected_indices:
        try:
            book_index = int(idx)
            book_data_json = request.form.get(f'book_data_{book_index}', '')
            if book_data_json:
                book_data = json.loads(book_data_json)
                selected_books.append(book_data)
                print(f"Добавлена книга: {book_data['title']}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Ошибка при обработке книги {idx}: {e}")
            continue
    
    if not selected_books:
        return "Не удалось найти выбранные книги", 400

    save_path = os.path.join(BASE_DIR, 'data', "recommendations.json")
    print(f"Сохраняем {len(selected_books)} выбранных книг в: {save_path}")
    
    try:
        save_recommendations(selected_books, save_path)
        return redirect(url_for('save_success', count=len(selected_books)))
    except Exception as e:
        return f"Ошибка сохранения: {str(e)}", 500


@app.route('/save_success')
@handle_errors
def save_success():
    """Страница успешного сохранения"""
    count = request.args.get('count', 0)
    return render_template('save_success.html', count=count)


@app.route('/reading_list')
@handle_errors
def reading_list():
    """Просмотр сохраненного списка для чтения"""
    save_path = os.path.join(BASE_DIR, 'data', "recommendations.json")
    
    try:
        with open(save_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        saved_books = saved_data.get('reading_list', [])
        saved_count = saved_data.get('total_selected', 0)
        saved_time = saved_data.get('timestamp', 'Неизвестно')
    except (FileNotFoundError, json.JSONDecodeError):
        saved_books = []
        saved_count = 0
        saved_time = 'Нет сохраненных данных'
    
    return render_template('reading_list.html', 
                         books=saved_books, 
                         count=saved_count,
                         saved_time=saved_time)


@app.route('/stats')
@handle_errors
def stats():
    """Статистика по библиотеке"""
    stats_data = {
        'total_books': len(books),
        'genres_count': len(genres_all),
        'authors_count': len(authors_all),
        'year_range': f"{min_year_global}-{max_year_global}",
        'popular_genres': sorted(genres_all, key=lambda g: sum(1 for b in books if b.get('genre') == g), reverse=True)[:5]
    }
    return render_template('stats.html', stats=stats_data)


if __name__ == '__main__':
    data_dir = os.path.join(BASE_DIR, 'data')
    os.makedirs(data_dir, exist_ok=True)
    print(f"Директория данных: {data_dir}")

    recommendations_path = os.path.join(data_dir, "recommendations.json")
    if not os.path.exists(recommendations_path):
        print("Файл recommendations.json будет создан при первом сохранении")
    
    app.run(debug=True, host='0.0.0.0', port=5050)
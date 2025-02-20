import requests
import collections
import datetime
import re
from bs4 import BeautifulSoup
from collections import Counter
import pytest

class Movies:
    """Информация о фильме содержится в файле `movies.csv`. Каждая строка этого файла после строки заголовка представляет один фильм и имеет следующий формат:
    movieId, title, genres
    Названия фильмов вводятся вручную или импортируются с <https://www.themoviedb.org/> и включают год выпуска в скобках. В этих названиях могут быть ошибки и несоответствия.
    Жанры представляют собой список, разделенный вертикальной чертой, и выбираются из следующих:

    * Боевик
    * Приключения
    * Анимация
    * Детский
    * Комедия
    * Криминал
    * Документальный
    * Драма
    * Фэнтези
    * Фильм-нуар
    * Ужасы
    * Мюзикл
    * Мистика
    * Романтика
    * Фантастика
    * Триллер
    * Война
    * Вестерн
    * (жанры не указаны)"""

    def __init__(self, path_to_the_file):
        """Constructor. Gets the filepath to the movies.csv-method"""
        self.filepath = path_to_the_file
        self.movies = self.get_first_1000_values()

    def dist_by_release(self):
        """
        The method returns a dict or an OrderedDict where the keys are years and the values are counts. 
        You need to extract years from the titles. Sort it by counts descendingly.
        """
        movies = self.movies
        year_counts = {}

        for movie in movies:
            title = movie["title"]
            match = re.search(r'\((\d{4})\)', title)
            if match:
                year = int(match.group(1))
                if year in year_counts:
                    year_counts[year] += 1
                else:
                    year_counts[year] = 1
        release_years = collections.OrderedDict(sorted(year_counts.items(), key=lambda x: x[1], reverse=True))
        return release_years
    
    def dist_by_genres(self):
        """
        The method returns a dict where the keys are genres and the values are counts.
     Sort it by counts descendingly.
        """
        movies = self.movies
        genres = {}

        for movie in movies:
            genres_list = movie["genres"].split("|")
            for genre in genres_list:
                if genre in genres:
                    genres[genre] += 1
                else:
                    genres[genre] = 1
        
        new_genres = dict(sorted(genres.items(), key=lambda item: item[1], reverse=True))
        genres = new_genres

        return genres
    
    def most_genres(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and 
        the values are the number of genres of the movie. Sort it by numbers descendingly.
        """
        movies_list = self.movies
        movies = {}

        number_of_times = 0
        for movie in movies_list:
            movies[movie["title"]] = len(movie["genres"].split("|"))
            number_of_times += 1
            if number_of_times >= n: break

        new_movies = dict(sorted(movies.items(), key=lambda item: item[1], reverse=True))
        movies = new_movies

        return movies

    def most_genres_by_years(self):
        """
        The method returns a dict with the most popular genres in different years, where the keys
        are years and the values are the genres of the movie. Sort it by years ascendingly.
        """
        movies_list = self.movies
        years_list = []

        for movie in movies_list:
            title = movie["title"]
            match = re.search(r'\((\d{4})\)', title)
            year = int(match.group(1))
            years_list.append(year)
            movie.update({"year": year})
        
        years_list = set(years_list)

        most_genres = {}

        for year in years_list:
            years_genres = {}
            for movie in movies_list:
                if movie["year"] == year:
                    genres_list = movie["genres"].split("|")
                    for genre in genres_list:
                        if genre in years_genres:
                            years_genres[genre] += 1
                        else:
                            years_genres.update({genre: 1})
            new_years_genres = dict(sorted(years_genres.items(), key=lambda item: item[1], reverse=True))
            most_genres.update({year: list(new_years_genres)[0]})

        return most_genres

    def get_first_1000_values(self):
        """Принимает указатель на экземпляр класса.
        Возвращает список из 1000 словарей с полями:
        movieId
        titles
        genres
        """
        filepath = self.filepath
        movies = []

        if self.is_movies_structure(): 
            with open(filepath, "r", encoding="utf-8") as file:
                next(file)
                for line in file:
                    meta = line.strip().split(",")
                    title, genres = self.parse_movie_string(line)
                    movie = {
                        "movieId": int(meta[0]),
                        "title": title,
                        "genres": genres
                    }
                    movies.append(movie)
                    if len(movies) >= 1000: break

        return movies
    
    def parse_movie_string(self, movie_string):
        """Принимает строку из файла movies
        и парсит ее, в зависимости от того, начинается
        ли она с кавычек или нет
        (это влияет на наличие запятой внутри названия)
        """
        comma_index = movie_string.find(',')
        if comma_index != -1:
            movie_string = movie_string[comma_index + 1:].strip()
        if movie_string[0] != '"':
            title = movie_string.split(',')[0]
            genres = movie_string.split(',')[1]
        else:
            last_quote_index = movie_string[1:].find('"')
            title = movie_string[:last_quote_index + 2].strip()
            genres = movie_string[last_quote_index + 3:].strip()

        return title, genres
    
    def is_movies_structure(self):
        status = 1
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                header_line = next(file).strip().split(',')
                if header_line[0] != "movieId" or header_line[1] != "title" or header_line[2] != "genres":
                    status = 0
                    raise Exception("Неверная структура файла")
        except Exception as e:
            print(f"Ошибка в чтении файла: {e}")
        return status

class Ratings:
    """Все рейтинги содержатся в файле `ratings.csv`. Каждая строка этого файла после строки заголовка
    представляет одну оценку одного фильма одним пользователем и имеет следующий формат:

    userId,movieId,rating,timestamp

    Строки в этом файле упорядочены сначала по userId, затем, внутри пользователя, по movieId.
    Рейтинги выставляются по 5-звездочной шкале с шагом в ползвезды (0,5 звезды - 5,0 звезды).
    Временные метки представляют секунды с полуночи по всемирному координированному времени (UTC) 1 января 1970 года."""
    def __init__(self, path_to_the_file):
        """Конструктор. Принимает путь к файлу ratings.csv
        Определяет местоположение movies.csv, предполагая, что они в одной директории
        Хранит 1000 строк фильмов и 1000 строк рейтинга в self.movies и self.ratings"""
        self.filepath = path_to_the_file
        self.movies_filepath = self.find_movies_filepath(self.filepath)

        self.outer_movies = Movies(self.movies_filepath)
        self.movies = self.outer_movies.get_first_1000_values()

        self.inner_movies = self.Movies(self)
        self.ratings = self.get_first_1000_values()
    
    def find_movies_filepath(self, filepath):
        """Принимает путь к файлу ratings.csv
        Возвращает путь к файлу movies.csv"""
        filename_index = filepath.find("ratings.csv")
        directory = filepath[:filename_index]
        movies_filepath = directory+"movies.csv"
        return movies_filepath
    
    def get_first_1000_values(self):
        """Принимает указатель на экземпляр класса.
        Возвращает список из 1000 рейтингов
        """
        filepath = self.filepath
        ratings = []
        
        if self.is_ratings_structure():
            with open(filepath, "r", encoding="utf-8") as file:
                next(file)
                for line in file:
                    meta = line.strip().split(",")
                    rating = {
                        "userId": int(meta[0]),
                        "movieId": int(meta[1]),
                        "rating": float(meta[2]),
                        "timestamp": int(meta[3]),
                    }
                    ratings.append(rating)
                    if len(ratings) >= 1000: break

        return ratings
    
    def is_ratings_structure(self):
        status = 1
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                header_line = next(file).strip().split(',')
                if header_line[0] != "userId" or header_line[1] != "movieId" or header_line[2] != "rating" or header_line[3] != "timestamp":
                    status = 1
                    raise Exception("Неверная структура файла")
        except Exception as e:
            print(f"Ошибка в чтении файла: {e}")
        return status

    class Movies:
        """Вложенный класс внутри Ratings.
        Неудачный нэйминг, может быть путаница из-за того,
        что на верхнем уровне есть класс с таким же именем"""
        def __init__(self, parent):
            """Конструктор
            Принимает ссылку на экземпляр класса,
            а также ссылку на экземпляр родительского класса parent"""
            self.parent = parent

        def dist_by_year(self):
            """
            The method returns a dict where the keys are years and the values are counts. 
            Sort it by years ascendingly. You need to extract years from timestamps.
            """
            years = {}
            ratings = self.parent.ratings
            for rating in ratings:
                year = (datetime.datetime.fromtimestamp(rating["timestamp"])).year
                if year in years:
                    years[year] += 1
                else:
                    years[year] = 1
            
            new_years = dict(sorted(years.items(), key=lambda item: item[0]))
            years = new_years
            
            return years

        def dist_by_rating(self):
            """
            The method returns a dict where the keys are ratings and the values are counts.
         Sort it by ratings ascendingly.
            """
            ratings_distribution = {}
            ratings = self.parent.ratings
            for rating in ratings:
                score = rating["rating"]
                if score in ratings_distribution:
                    ratings_distribution[score] += 1
                else:
                    ratings_distribution[score] = 1
            
            scores = dict(sorted(ratings_distribution.items(), key=lambda item: item[0]))
            ratings_distribution = scores

            return ratings_distribution
        
        def top_by_num_of_ratings(self, n):
            """
            The method returns top-n movies by the number of ratings. 
            It is a dict where the keys are movie titles and the values are numbers.
     Sort it by numbers descendingly.
            """
            top_movies = {}
            movies_with_counts = {}
            movies = self.parent.movies
            ratings = self.parent.ratings
            
            for movie in movies:
                ratings_count = 0
                for rating in ratings:
                    if movie["movieId"] == rating["movieId"]:
                        ratings_count += 1
                movies_with_counts.update({movie["title"]: ratings_count})

            scores = dict(sorted(movies_with_counts.items(), key=lambda item: item[1], reverse=True))

            times = 0
            for title, count in scores.items():
                top_movies.update({title: count})
                times += 1
                if times >= n: break

            return top_movies
        
        def top_by_ratings(self, n, metric="average"):
            """
            The method returns top-n movies by the average or median of the ratings.
            It is a dict where the keys are movie titles and the values are metric values.
            Sort it by metric descendingly.
            The values should be rounded to 2 decimals.
            """
            top_movies = {}
            rated_movies = {}
            movies = self.parent.movies
            ratings = self.parent.ratings

            for movie in movies:
                ratings_list = []
                for rating in ratings:
                    if rating["movieId"] == movie["movieId"]:
                        ratings_list.append(rating["rating"])
                if len(ratings_list) > 0: rated_movies[movie["title"]] = ratings_list

            new_movies = self.calc_rating(rated_movies, metric)
            sorted_movies = dict(sorted(new_movies.items(), key=lambda item: item[1], reverse=True))
            
            times = 0
            for movie in sorted_movies.items():
                top_movies[movie[0]] = movie[1]
                times += 1
                if times >= n: break

            return top_movies

        def top_controversial(self, n):
            """
            The method returns top-n movies by the variance of the ratings.
            It is a dict where the keys are movie titles and the values are the variances.
          Sort it by variance descendingly.
            The values should be rounded to 2 decimals.
            """
            top_movies = {}
            rated_movies = {}
            movies = self.parent.movies
            ratings = self.parent.ratings

            for movie in movies:
                ratings_list = []
                for rating in ratings:
                    if rating["movieId"] == movie["movieId"]:
                        ratings_list.append(rating["rating"])
                if len(ratings_list) > 0: rated_movies[movie["title"]] = ratings_list

            new_movies = self.calc_rating_variance(rated_movies)
            sorted_movies = dict(sorted(new_movies.items(), key=lambda item: item[1], reverse=True))
            
            times = 0
            for movie in sorted_movies.items():
                top_movies[movie[0]] = movie[1]
                times += 1
                if times >= n: break

            return top_movies
            
        def calc_rating(self, movies, metric):
            """Определяет, как посчитать рейтинг: по средне-арифметическому или по медиане.
            Принимает словарь movies и тип расчета среднего в переменной metric: либо average, либо mean.
            В зависимости от типа расчета среднего вызывает ту или иную функцию расчета.
            Получает обновленный словарь после расчета среднего и возвращает его на уровень выше"""
            if metric == "average":
                result = self.calc_avg_rating(movies)
            elif metric == "mean":
                result = self.calc_mean_rating(movies)
            else:
                raise Exception("Your should send parameter metric with the 'average' or 'mean' value")
            
            return result
        
        def calc_avg_rating(self, movies):
            """Принимает словарь movies: ключи - названия фильмов, значения - список оценок.
            Рассчитывает средне-арифметическое рейтингов из списка и возвращает обновленный словарь"""
            top_movies = {}
            for title, ratings in movies.items():
                ratings_count = len(ratings)
                ratings_sum = sum(ratings)
                ratings_avg = round(ratings_sum / ratings_count, 2)
                top_movies[title] = ratings_avg
            
            return top_movies
        
        def calc_mean_rating(self, movies):
            """Принимает словарь movies: ключи - названия фильмов, значения - список оценок.
            Рассчитывает медианное значение рейтингов из списка и возвращает обновленный словарь"""
            top_movies = {}
            for title, ratings in movies.items():
                ratings_count = len(ratings)
                sorted_ratings = sorted(ratings)

                if ratings_count % 2 == 0:
                    mid_index1 = ratings_count // 2 - 1
                    mid_index2 = ratings_count // 2
                    ratings_mean = (sorted_ratings[mid_index1] + sorted_ratings[mid_index2]) / 2
                else:
                    mid_index = ratings_count // 2
                    ratings_mean = sorted_ratings[mid_index]

                top_movies[title] = round(ratings_mean, 2) 

            return top_movies
        
        def calc_rating_variance(self, movies):
            """Принимает словарь movies: ключи - названия фильмов, значения - список оценок.
            Рассчитывает дисперсию и возвращает обновленный словарь, в значениях - дисперсия"""
            top_movies = {}
            avg_rating = self.calc_avg_rating(movies)
            variance = 0

            for title, ratings in movies.items():
                ratings_count = len(ratings)
                variance = 0
                variance_sum = 0
                for rating in ratings:
                    variance_sum += (rating - avg_rating[title]) * (rating - avg_rating[title])
                if ratings_count > 1:
                    variance = variance_sum / (ratings_count - 1)
                    top_movies[title] = round(variance, 2)
                else:
                    top_movies[title] = 0.00

            return top_movies
        
    class Users(Movies):
        """
        In this class, three methods should work. 
        The 1st returns the distribution of users by the number of ratings made by them.
        The 2nd returns the distribution of users by average or median ratings made by them.
        The 3rd returns top-n users with the biggest variance of their ratings.
     Inherit from the class Movies. Several methods are similar to the methods from it.
        """
        def __init__(self, parent):
            """Конструктор, принимающий ссылку на родительский класс Ratings."""
            super().__init__(parent)
        
        def dist_users_by_num_of_ratings(self):
            """returns the distribution of users by the number of ratings made by them.
            Хоть в задании и не указано, отсортировал от большего к меньшему"""
            users = {}
            ratings = self.parent.ratings

            for rating in ratings:
                userId = rating["userId"]
                if userId in users:
                    users[userId] += 1
                else:
                    users[userId] = 1
            
            sorted_users = dict(sorted(users.items(), key=lambda item: item[1], reverse=True))
            users = sorted_users

            return users
        
        def dist_users_by_rating(self, metric="average"):
            """returns the distribution of users by average or median ratings made by them.
            Хоть в задании напрямую и не указано, отсортировал от большего к меньшему по рейтингу"""
            users = {}
            users_ids = []
            ratings = self.parent.ratings

            for rating in ratings:
                if rating["userId"] not in users_ids: users_ids.append(rating["userId"])

            for user_id in users_ids:
                ratings_list = []
                for rating in ratings:
                    if rating["userId"] == user_id: ratings_list.append(rating["rating"])
                users.update({user_id: ratings_list})

            average_ratings = self.calc_rating(users, metric)
            sorted_users = dict(sorted(average_ratings.items(), key=lambda item: item[1], reverse=True))

            return sorted_users

        def top_controversial_users(self, n):
            """returns top-n users with the biggest variance of their ratings."""
            top_users = {}
            users = {}
            users_ids = []
            ratings = self.parent.ratings

            for rating in ratings:
                if rating["userId"] not in users_ids: users_ids.append(rating["userId"])

            for user_id in users_ids:
                ratings_list = []
                for rating in ratings:
                    if rating["userId"] == user_id: ratings_list.append(rating["rating"])
                users.update({user_id: ratings_list})

            controversial_users = self.calc_rating_variance(users)
            sorted_users = dict(sorted(controversial_users.items(), key=lambda item: item[1], reverse=True))

            times = 0
            for user in sorted_users.items():
                top_users[user[0]] = user[1]
                times += 1
                if times >= n: break
            
            return top_users

class Tags:
    """Все теги содержатся в файле `tags.csv`. Каждая строка этого файла после строки заголовка
    представляет одну оценку, примененную к одному фильму одним пользователем, и имеет следующий формат:

    userId,movieId,tag,timestamp
    
    Строки в этом файле упорядочены сначала по userId, затем, внутри пользователя, по movieId.
    Теги — это метаданные о фильмах, создаваемые пользователями. Каждый тег обычно представляет собой одно слово или короткую фразу.
    Значение, ценность и цель конкретного тега определяются каждым пользователем.
    Временные метки представляют собой секунды с полуночи по всемирному координированному времени (UTC) 1 января 1970 года."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.tags = self.read_file(self.file_path)
    
    def read_file(self, path_to_file):
        tag_list = []
        if self.is_tags_structure(path_to_file):
            with open(path_to_file, 'r') as file:
                lines = file.readlines()[1:1001]
                tag_list = [line.split(',')[2].strip() for line in lines]
        return tag_list
    
    def is_tags_structure(self, path_to_file):
        status = 1
        try:
            with open(path_to_file, 'r', encoding='utf-8') as file:
                header_line = next(file).strip().split(',')
                if header_line[0] != "userId" or header_line[1] != "movieId" or header_line[2] != "tag" or header_line[3] != "timestamp":
                    status = 0
                    raise Exception("Неверная структура файла")
        except Exception as e:
            print(f"Ошибка в чтении файла: {e}")
        return status

    def most_words(self, n):
        unique_tags = list(set(self.tags))
        word_counts = [(tag, len(tag.split())) for tag in unique_tags]
        sorted_tags = sorted(word_counts, key=lambda x: x[1], reverse=True)
        big_tags = {tag: count for tag, count in sorted_tags[:n]}
        return big_tags

    def longest(self, n):
        unique_tags = list(set(self.tags)) 
        big_tags = sorted(unique_tags, key=lambda x: len(x), reverse=True)
        return big_tags[:n]

    def most_words_and_longest(self, n):
        most_words_set = set(self.most_words(n).keys())
        longest_set = set(self.longest(n))
        big_tags = list(most_words_set & longest_set)
        return big_tags
        
    def most_popular(self, n):
        tag_counts = Counter(self.tags)
        sorted_tags = list(sorted(tag_counts.items(), key=lambda item: item[1], reverse=True))
        popular_tags = dict(sorted_tags[:n])
        return popular_tags
        
    def tags_with(self, word):
        filtered_tags = [tag for tag in self.tags if word.lower() in tag.lower()]
        unique_tags = set(filtered_tags)
        tags_with_word = sorted(unique_tags)
        return tags_with_word

class Links:
    """Идентификаторы, которые можно использовать для ссылки на другие источники данных о фильмах, содержатся в файле `links.csv`.
    Каждая строка этого файла после строки заголовка представляет один фильм и имеет следующий формат:

    movieId,imdbId,tmdbId
    movieId — это идентификатор фильмов, используемый <https://movielens.org>. Например, фильм «История игрушек» имеет ссылку <https://movielens.org/movies/1>.
    imdbId — это идентификатор фильмов, используемых <http://www.imdb.com>. Например, фильм «История игрушек» имеет ссылку <http://www.imdb.com/title/tt0114709/>.
    tmdbId — это идентификатор фильмов, используемых <https://www.themoviedb.org>. Например, фильм «История игрушек» имеет ссылку <https://www.themoviedb.org/movie/862>.
    Использование перечисленных выше ресурсов регулируется условиями каждого поставщика."""
    def __init__(self, path_to_the_file):
        self.filepath = path_to_the_file
        self.movie_list = self.read_file(self.filepath)
        self.imdb = self.get_imdb()
    
    def get_imdb(self):
        movie_list = self.movie_list
        sorted_movie_list = sorted(movie_list, key=lambda x: int(x[1]), reverse=True)
        imdb_list = [self.parse_imdb(movie) for movie in sorted_movie_list]
        imdb_info = [x for x in imdb_list if x is not None]
        return imdb_info
    
    def top_directors(self, n):
        director_count = Counter(movie[2] for movie in self.imdb)
        sorted_directors = sorted(director_count.items(), key=lambda item: item[1], reverse=True)
        directors = dict(sorted_directors[:n])
        return directors
    
    def most_expensive(self, n):
        budget_data = [(movie[1], movie[3]) for movie in self.imdb]
        sorted_movies = sorted(budget_data, key=lambda item: item[1], reverse=True)
        budgets = dict(sorted_movies[:n])
        return budgets
    
    def most_profitable(self, n):
        profit_data = [(movie[1], movie[4] - movie[3]) for movie in self.imdb]
        sorted_movies = sorted(profit_data, key=lambda item: item[1], reverse=True)
        profits = dict(sorted_movies[:n])
        return profits
    
    def longest(self, n):
        runtime_data = [(movie[1], movie[5]) for movie in self.imdb]
        sorted_movies = sorted(runtime_data, key=lambda item: item[1], reverse=True)
        runtimes = dict(sorted_movies[:n])
        return runtimes
    
    def top_cost_per_minute(self, n):
        cost_data = [(movie[1], round(movie[3] / movie[5], 2)) for movie in self.imdb]
        sorted_movies = sorted(cost_data, key=lambda item: item[1], reverse=True)
        costs = dict(sorted_movies[:n])
        return costs
    
    def parse_imdb(self, movie):
        try:
            id = movie[1]
            url = f"https://www.imdb.com/title/tt{id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            page = requests.get(url, headers=headers)
            if page.status_code != 200:
                raise Exception(page.status_code)
                # return None
        except Exception as e:
            print(f"Ошибка imdb: {e}")

        soup = BeautifulSoup(page.text, "html.parser")
        director = self._get_field(soup, "Director")
        budget = self._get_field(soup, "Budget")
        runtime = self._get_field(soup, "Runtime")
        title = self._get_field(soup, "Title")
        if len(budget) == 8:
            movie_data = [
                id,
                title,
                director,
                self.parse_budget(budget[2]),
                self.parse_budget(budget[6]),
                runtime
            ]
        else:
            return None
        return movie_data
    
    def read_file(self, path_to_the_file):
        movie_list = []
        if self.is_links_structure(path_to_the_file):
            with open(path_to_the_file, 'r') as file:
                lines = file.readlines()[1:3]
                movie_list = [line.split(',') for line in lines]
            return movie_list
    
    def is_links_structure(self, path_to_file):
        status = 1
        try:
            with open(path_to_file, 'r', encoding='utf-8') as file:
                header_line = next(file).strip().split(',')
                if header_line[0] != "movieId" or header_line[1] != "imdbId" or header_line[2] != "tmdbId":
                    status = 0
                    raise Exception("Неверная структура файла")
        except Exception as e:
            print(f"Ошибка в чтении файла: {e}")
        return status
        
    @staticmethod
    def parse_budget(budget_str):
        try:
            return int(budget_str.replace('$', '').replace('£', '').replace('€', '').replace(',', '').split()[0])
        except (ValueError, IndexError):
            return 0

    @staticmethod
    def _get_field(soup, field_name): 
        def get_duration(html):
            match = re.search(r'(\d+)h?\s*(\d+)?m?', html)
            if match:
                hours = int(match.group(1)) if match.group(1) else 0
                minutes = int(match.group(2)) if match.group(2) else 0
                total_minutes = hours * 60 + minutes
                return total_minutes
            else:
                return 0

        field_name = field_name.lower()
        field_value = "N/A"

        if field_name == "director":
            director_tag = soup.find("span", class_="ipc-metadata-list-item__label ipc-metadata-list-item__label--btn", string="Director")
            if director_tag:
                director = director_tag.find_parent("li").find("a")
                field_value = director.text.strip() if director else "N/A"
               
        if field_name == "runtime":
            runtime_tag = soup.find("li", class_="ipc-inline-list__item", string=lambda text: text and ("h" in text or "m" in text))
            if runtime_tag:
                field_value = get_duration(str(runtime_tag))
            else:
                field_value = 0

        if field_name == "budget":
            budget_tags = soup.find_all('span', class_='ipc-metadata-list-item__list-content-item')
            if budget_tags:
                field_value = [span.get_text(strip=True) for span in budget_tags]

        if field_name == "title":
            title_tag = soup.find('div', class_='sc-ec65ba05-1 fUCCIx')
            if title_tag:
                field_value = title_tag.text.split(':')[1].strip()
        
        return field_value

class Tests:
    """Тесты обязательно должны проверять:
    1. Методы возвращают корректные типы данных
    2. Списки элементов содержат корректные типы данных
    3. Возвращаемые данные отсортированы корректно
    Нужно запускать тесты перед переходом к следующему этапу задания"""

################ FOR LINKS AND TAGS ################

    @pytest.fixture
    def links_obj(self):
        links_test_data = Links('./ml_latest_small/links.csv')
        return links_test_data

    @pytest.fixture
    def tags_obj(self):
        tags_test_data = Tags('./ml_latest_small/tags.csv')
        return tags_test_data

################ MOVIES() ################

    def test_movies_dist_by_release_data_type(self):
        """Проверяет тип выходных данных"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.dist_by_release()
        assert type(result) == collections.OrderedDict

    def test_movies_dist_by_release_list_element_type(self):
        """Проверяет тип данных внутри упорядоченного словаря"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.dist_by_release()
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        assert type(first_key) == int
        assert type(first_value) == int

    def test_movies_dist_by_release_sort(self):
        """Проверяет корректность сортировки внутри упорядоченного списка"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.dist_by_release()
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        second_key = list(result.keys())[1]
        second_value = result[second_key]
        third_key = list(result.keys())[2]
        third_value = result[third_key]
        assert first_value >= second_value
        assert second_value >= third_value

    def test_movies_dist_by_genres_data_type(self):
        """Проверяет тип выходных данных"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.dist_by_genres()
        assert type(result) == dict

    def test_movies_dist_by_genres_list_element_type(self):
        """Проверяет тип данных внутри словаря"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.dist_by_genres()
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        assert type(first_key) == str
        assert type(first_value) == int

    def test_movies_dist_by_genres_sort(self):
        """Проверяет корректность сортировки внутри упорядоченного списка"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.dist_by_genres()
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        second_key = list(result.keys())[1]
        second_value = result[second_key]
        third_key = list(result.keys())[2]
        third_value = result[third_key]
        assert first_value >= second_value
        assert second_value >= third_value

    def test_movies_most_genres_data_type(self):
        """Проверяет тип выходных данных"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.most_genres(10)
        assert type(result) == dict

    def test_movies_most_genres_list_element_type(self):
        """Проверяет тип данных внутри словаря"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.most_genres(10)
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        assert type(first_key) == str
        assert type(first_value) == int

    def test_movies_most_genres_sort(self):
        """Проверяет корректность сортировки внутри упорядоченного списка"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.most_genres(10)
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        second_key = list(result.keys())[1]
        second_value = result[second_key]
        third_key = list(result.keys())[2]
        third_value = result[third_key]
        assert first_value >= second_value
        assert second_value >= third_value

    def test_movies_most_genres_length(self):
        """Проверяет длину полученного словаря"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.most_genres(10)
        assert len(result) == 10

    def test_movies_most_genres_by_years(self):
        """Проверяет тип выходных данных"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.most_genres_by_years()
        assert type(result) == dict

    def test_movies_most_genres_by_years_list_element_type(self):
        """Проверяет тип данных внутри словаря"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.most_genres_by_years()
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        assert type(first_key) == int
        assert type(first_value) == str

    def test_movies_most_genres_by_years_sort(self):
        """Проверяет корректность сортировки внутри упорядоченного списка"""
        movies = Movies("./ml_latest_small/movies.csv")
        result = movies.most_genres_by_years()
        first_key = list(result.keys())[0]
        second_key = list(result.keys())[1]
        third_key = list(result.keys())[2]
        assert first_key <= second_key
        assert second_key <= third_key

################ RATINGS() ################

    def test_ratings_dist_by_year_data_type(self):
        """Проверяет тип выходных данных"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.dist_by_year()
        assert type(result) == dict

    def test_ratings_dist_by_year_list_element_type(self):
        """Проверяет тип данных внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.dist_by_year()
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        assert type(first_key) == int
        assert type(first_value) == int

    def test_ratings_dist_by_year_sort(self):
        """Проверяет корректность сортировки внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.dist_by_year()
        first_key = list(result.keys())[0]
        second_key = list(result.keys())[1]
        third_key = list(result.keys())[2]
        assert first_key <= second_key
        assert second_key <= third_key

    def test_ratings_dist_by_rating_data_type(self):
        """Проверяет тип выходных данных"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.dist_by_rating()
        assert type(result) == dict

    def test_ratings_dist_by_rating_list_element_type(self):
        """Проверяет тип данных внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.dist_by_rating()
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        assert type(first_key) == float
        assert type(first_value) == int

    def test_ratings_dist_by_rating_sort(self):
        """Проверяет корректность сортировки внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.dist_by_rating()
        first_key = list(result.keys())[0]
        second_key = list(result.keys())[1]
        third_key = list(result.keys())[2]
        assert first_key <= second_key
        assert second_key <= third_key

    def test_ratings_top_by_num_of_ratings_data_type(self):
        """Проверяет тип выходных данных"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_by_num_of_ratings(10)
        assert type(result) == dict

    def test_ratings_top_by_num_of_ratings_list_element_type(self):
        """Проверяет тип данных внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_by_num_of_ratings(10)
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        assert type(first_key) == str
        assert type(first_value) == int

    def test_ratings_top_by_num_of_ratings_sort(self):
        """Проверяет корректность сортировки внутри словаря"""
        n = 10
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_by_num_of_ratings(n)
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        second_key = list(result.keys())[1]
        second_value = result[second_key]
        last_key = list(result.keys())[n - 1]
        last_value = result[last_key]
        assert first_value >= second_value
        assert second_value >= last_value

    def test_ratings_top_by_num_of_ratings_length(self):
        """Проверяет длину полученного словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_by_num_of_ratings(10)
        assert len(result) == 10

    def test_ratings_top_by_ratings_data_type(self):
        """Проверяет тип выходных данных"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_by_ratings(100)
        assert type(result) == dict

    def test_ratings_top_by_ratings_list_element_type(self):
        """Проверяет тип данных внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_by_ratings(100)
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        assert type(first_key) == str
        assert type(first_value) == float

    def test_ratings_top_by_ratings_sort(self):
        """Проверяет корректность сортировки внутри словаря"""
        n = 100
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_by_ratings(n)
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        mid_key = list(result.keys())[int(n / 2)]
        mid_value = result[mid_key]
        last_key = list(result.keys())[n - 1]
        last_value = result[last_key]
        assert first_value >= mid_value
        assert mid_value >= last_value

    def test_ratings_top_by_ratings_length(self):
        """Проверяет длину полученного словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_by_ratings(100)
        assert len(result) == 100

    def test_ratings_top_by_ratings_value_avg(self):
        """Проверяет среднее значение"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_by_ratings(100)
        assert result["Beauty and the Beast (1991)"] == 4.12

    def test_ratings_top_by_ratings_value_mean(self):
        """Проверяет медиану"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_by_ratings(100, "mean")
        assert result["Beauty and the Beast (1991)"] == 4.25

    def test_ratings_top_controversial_data_type(self):
        """Проверяет тип выходных данных"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_controversial(100)
        assert type(result) == dict

    def test_ratings_top_controversial_list_element_type(self):
        """Проверяет тип данных внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_controversial(100)
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        assert type(first_key) == str
        assert type(first_value) == float

    def test_ratings_top_controversial_sort(self):
        """Проверяет корректность сортировки внутри словаря"""
        n = 100
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_controversial(n)
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        mid_key = list(result.keys())[int(n / 2)]
        mid_value = result[mid_key]
        last_key = list(result.keys())[n - 1]
        last_value = result[last_key]
        assert first_value >= mid_value
        assert mid_value >= last_value

    def test_ratings_top_controversial_length(self):
        """Проверяет длину полученного словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_controversial(100)
        assert len(result) == 100

    def test_ratings_top_controversial_value_variance(self):
        """Проверяет длину полученного словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        result = ratings.inner_movies.top_controversial(100)
        assert result["Independence Day (a.k.a. ID4) (1996)"] == 1.08

    def test_dist_users_by_num_of_ratings_data_type(self):
        """Проверяет тип выходных данных"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.dist_users_by_num_of_ratings()
        assert type(result) == dict

    def test_dist_users_by_num_of_ratings_list_element_type(self):
        """Проверяет тип данных внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.dist_users_by_num_of_ratings()
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        assert type(first_key) == int
        assert type(first_value) == int

    def test_dist_users_by_num_of_ratings_sort(self):
        """Проверяет корректность сортировки внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.dist_users_by_num_of_ratings()
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        mid_key = list(result.keys())[1]
        mid_value = result[mid_key]
        last_key = list(result.keys())[2]
        last_value = result[last_key]
        assert first_value >= mid_value
        assert mid_value >= last_value
        
    def test_dist_users_by_rating_data_type(self):
        """Проверяет тип выходных данных"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.dist_users_by_rating()
        assert type(result) == dict

    def test_dist_users_by_rating_list_element_type(self):
        """Проверяет тип данных внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.dist_users_by_rating()
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        assert type(first_key) == int
        assert type(first_value) == float

    def test_dist_users_by_rating_sort(self):
        """Проверяет корректность сортировки внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.dist_users_by_rating()
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        mid_key = list(result.keys())[int(1)]
        mid_value = result[mid_key]
        last_key = list(result.keys())[2]
        last_value = result[last_key]
        assert first_value >= mid_value
        assert mid_value >= last_value

    def test_dist_users_by_rating_value_avg(self):
        """Проверяет среднее значение"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.dist_users_by_rating()
        assert result[2] == 3.95

    def test_dist_users_by_rating_value_mean(self):
        """Проверяет медиану"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.dist_users_by_rating(metric="mean")
        assert result[3] == 0.5

    def test_top_controversial_users_data_type(self):
        """Проверяет тип выходных данных"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.top_controversial_users(5)
        assert type(result) == dict

    def test_top_controversial_users_list_element_type(self):
        """Проверяет тип данных внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.top_controversial_users(5)
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        assert type(first_key) == int
        assert type(first_value) == float

    def test_top_controversial_users_sort(self):
        """Проверяет корректность сортировки внутри словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.top_controversial_users(5)
        first_key = list(result.keys())[0]
        first_value = result[first_key]
        mid_key = list(result.keys())[int(1)]
        mid_value = result[mid_key]
        last_key = list(result.keys())[2]
        last_value = result[last_key]
        assert first_value >= mid_value
        assert mid_value >= last_value

    def test_top_controversial_users_length(self):
        """Проверяет длину полученного словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.top_controversial_users(5)
        assert len(result) == 5

    def test_top_controversial_users_variance(self):
        """Проверяет длину полученного словаря"""
        ratings = Ratings("./ml_latest_small/ratings.csv")
        users = ratings.Users(ratings)
        result = users.top_controversial_users(5)
        assert result[3] == 4.37

################ TAGS() ################

    def test_most_words_return_type(self, tags_obj):
        result = tags_obj.most_words(5)
        assert isinstance(result, dict), "Returned value is not a dictionary"

    def test_most_words_dict_element_type(self, tags_obj):
        result = tags_obj.most_words(5)
        for tag, count in result.items():
            assert isinstance(tag, str), f"Tag {tag} is not a string"
            assert isinstance(count, int), f"Value {count} is not an integer"
        
    def test_most_words_sort(self, tags_obj):
        result = tags_obj.most_words(5)
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True), "The data is not sorted correctly"

    def test_longest_return_type(self, tags_obj):
        result = tags_obj.longest(5)
        assert isinstance(result, list), "Returned value is not a list"

    def test_longest_list_element_type(self, tags_obj):
        result = tags_obj.longest(5)
        for tag in result:
            assert isinstance(tag, str), f"Tag {tag} is not a string"

    def test_longest_sort(self, tags_obj):
        result = tags_obj.longest(5)
        counts = [len(tag) for tag in result]
        assert counts == sorted(counts, reverse=True), "The data is not sorted correctly"

    def test_most_words_and_longest_return_type(self, tags_obj):
        result = tags_obj.most_words_and_longest(5)
        assert isinstance(result, list), "Returned value is not a list"

    def test_most_words_and_longest_list_element_type(self, tags_obj):
        result = tags_obj.most_words_and_longest(5)
        for tag in result:
            assert isinstance(tag, str), f"Tag {tag} is not a string"

    def test_most_popular_return_type(self, tags_obj):
        result = tags_obj.most_popular(5)
        assert isinstance(result, dict), "Returned value is not a dictionary"

    def test_most_popular_dict_element_type(self, tags_obj):
        result = tags_obj.most_popular(5)
        for tag, count in result.items():
            assert isinstance(tag, str), f"Tag {tag} is not a string"
            assert isinstance(count, int), f"Value {count} is not an integer"

    def test_most_popular_sort(self, tags_obj):
        result = tags_obj.most_popular(5)
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True), "The data is not sorted correctly"

    def test_tags_with_return_type(self, tags_obj):
        result = tags_obj.tags_with('comedy')
        assert isinstance(result, list), "Returned value is not a list"

    def test_tags_with_list_element_type(self, tags_obj):
        result = tags_obj.tags_with('comedy')
        for tag in result:
            assert isinstance(tag, str), f"Tag {tag} is not a string"

    def test_tags_with_sort(self, tags_obj):
        result = tags_obj.tags_with('comedy')
        assert result == sorted(result), "The data is not sorted correctly"

################ LINKS() ################

    def test_get_imdb_return_type(self, links_obj):
        result = links_obj.get_imdb()
        assert isinstance(result, list), "Returned value is not a list"

    def test_get_imdb_list_elements_type(self, links_obj):
        result = links_obj.get_imdb()
        for movie in result:
            assert isinstance(movie, list), f"Value {movie} is not a list"
            assert isinstance(movie[0], str), f"movieId {movie[0]} is not a string"
            assert isinstance(movie[1], str), f"Title {movie[1]} is not a string"
            assert isinstance(movie[2], str), f"Director {movie[2]} is not a string"
            assert isinstance(movie[3], int), f"Budget {movie[3]} is not an integer"
            assert isinstance(movie[4], int), f"CWG {movie[4]} is not an integer"
            assert isinstance(movie[5], int), f"Minutes {movie[5]} is not an integer"

    def test_get_imdb_sort(self, links_obj):
        result = links_obj.get_imdb()
        counts = [movie[0] for movie in result]
        assert counts == sorted(counts, reverse=True), "The data is not sorted correctly"

    def test_top_directors_return_type(self, links_obj):
        result = links_obj.top_directors(5)
        assert isinstance(result, dict), "Returned value is not a dictionary"

    def test_top_directors_dict_elements_type(self, links_obj):
        result = links_obj.top_directors(5)
        for director, count in result.items():
            assert isinstance(director, str), f"Director {director} is not a string"
            assert isinstance(count, int), f"value {count} is not an integer"

    def test_top_directors_sort(self, links_obj):
        result = links_obj.top_directors(5)
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True), "The data is not sorted correctly"

    def test_most_expensive_return_type(self, links_obj):
        result = links_obj.most_expensive(5)
        assert isinstance(result, dict), "Returned value is not a dictionary"

    def test_most_expensive_dict_element_type(self, links_obj):
        result = links_obj.most_expensive(5)
        for movie, budget in result.items():
            assert isinstance(movie, str), f"Title {movie} is not a string"
            assert isinstance(budget, int), f"Value {budget} is not an integer"

    def test_most_expensive_sort(self, links_obj):
        result = links_obj.most_expensive(5)
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True), "The data is not sorted correctly"

    def test_most_profitable_return_type(self, links_obj):
        result = links_obj.most_profitable(5)
        assert isinstance(result, dict), "Returned value is not a dictionary"

    def test_most_profitable_dict_element_type(self, links_obj):
        result = links_obj.most_profitable(5)
        for movie, profit in result.items():
            assert isinstance(movie, str), f"Title {movie} is not a string"
            assert isinstance(profit, int), f"Value {profit} is not an integer"

    def test_most_profitable_sort(self, links_obj):
        result = links_obj.most_profitable(5)
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True), "The data is not sorted correctly"

    def test_longest_return_type(self, links_obj):
        result = links_obj.longest(5)
        assert isinstance(result, dict), "Returned value is not a dictionary"

    def test_longest_dict_element_type(self, links_obj):
        result = links_obj.longest(5)
        for movie, minutes in result.items():
            assert isinstance(movie, str), f"Title {movie} is not a string"
            assert isinstance(minutes, int), f"Value {minutes} is not an integer"

    def test_longest_sort(self, links_obj):
        result = links_obj.longest(5)
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True), "The data is not sorted correctly"

    def test_top_cost_per_minute_return_type(self, links_obj):
        result = links_obj.top_cost_per_minute(5)
        assert isinstance(result, dict), "Returned value is not a dictionary"

    def test_top_cost_per_minute_dict_element_type(self, links_obj):
        result = links_obj.top_cost_per_minute(5)
        for movie, cost in result.items():
            assert isinstance(movie, str), f"Title {movie} is not a string"
            assert isinstance(cost, float), f"Value {cost} is not a float"

    def test_top_cost_per_minute_sort(self, links_obj):
        result = links_obj.top_cost_per_minute(5)
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True), "The data is not sorted correctly"

from flask import Flask, Response, request
from flask_cors import CORS
from datetime import datetime
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/')
def homepage():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")
    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>

    <img src="http://loremflickr.com/600/400">
    """.format(time=the_time)

@app.route('/test')
def test():
    return 'Hello'

@app.route('/most_popular')
def most_popular_movie():
    movies = pd.read_csv('./tmdb_5000_movies.csv', low_memory=False)
    C = movies['vote_average'].mean()
    m = movies['vote_count'].quantile(0.50)
    q_movies = movies.copy().loc[movies['vote_count'] >= m]
    def weighted_rating(x, m=m, C=C):
        v = x['vote_count']
        R = x['vote_average']
        # Calculation based on the IMDB formula
        return (v/(v+m) * R) + (m/(v+m) * C)
    q_movies['score'] = q_movies.apply(weighted_rating, axis=1)
    q_movies = q_movies.sort_values('score', ascending=False)
    return(Response(q_movies[['title', 'vote_count', 'vote_average', 'score']].head(10).to_json(orient='records'), mimetype='application/json'))

@app.route('/search')
def search():
    searchword = request.args.get('key', '')
    movies = pd.read_csv('./tmdb_5000_movies.csv', low_memory=False)
    titles = movies[movies['title'].str.contains(searchword, case=False)]['title'].head(10)
    return(Response(titles.to_json(orient='records'), mimetype='application/json'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
from flask import Flask, Response, request
from flask_cors import CORS
from datetime import datetime
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

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

@app.route('/recommend')
def recommend():
    title = request.args.get('title', '')
    tfidf = TfidfVectorizer(stop_words='english')
    movies = pd.read_csv('./tmdb_5000_movies.csv', low_memory=False)
    movies['overview'] = movies['overview'].fillna('')
    tfidf_matrix = tfidf.fit_transform(movies['overview'])
    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    #Construct a reverse map of indices and movie titles
    indices = pd.Series(movies.index, index=movies['title'].str.lower()).drop_duplicates()
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return(Response(movies['title'].iloc[movie_indices].to_json(orient='records'), mimetype='application.json'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
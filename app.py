from flask import Flask
from flask_cors import CORS
from datetime import datetime
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

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
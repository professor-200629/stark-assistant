# STARK Main Application

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to the STARK application!'

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, session, redirect, render_template,jsonify

app = Flask(__name__, static_url_path='')
app.config['DEBUG'] = True
app.secret_key = 'tiptone'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800

@app.route('/')
def index():
    # 
    return "hello"


if __name__ == "__main__":
    app.run(debug = True)

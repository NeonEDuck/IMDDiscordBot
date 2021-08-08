from flask import Flask

app = Flask(__name__)

@app.route('/')
def main():
    return 'Bot is alive!'

def run(host='0.0.0.0', port=8080):
	app.run(host=host, port=port)
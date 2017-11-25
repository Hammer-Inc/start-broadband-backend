from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return 'success', 200


@app.route('/address/search', methods=['POST'])
def search():
    return 'success', 200


if __name__ == '__main__':
    app.run()

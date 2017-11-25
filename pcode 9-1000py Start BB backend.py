from flask import Flask

app = Flask(__name__)


@app.route('/address/search')
def search():
    return 'success', 200

if __name__ == '__main__':
    app.run()

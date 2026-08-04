from flask import Flask

app = Flask(__name__)

@app.route('/api/test', methods=['GET'])
def test():
    return {'message': 'Backend is running!'}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
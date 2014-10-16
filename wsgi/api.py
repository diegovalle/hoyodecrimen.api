from flask import Flask
 
app = Flask(__name__)
 
@app.route('/')
@app.route('/hello')
def index():
    return "Hello from OpenShift"
 
if __name__ == '__main__':
    app.run()
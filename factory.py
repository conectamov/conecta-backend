from flask import Flask

def create_app():
    app = Flask(__name__)
    #app.config.from_object(Config)

    @app.get("/")
    def hello_world():
        return "Hello World!"


    return app

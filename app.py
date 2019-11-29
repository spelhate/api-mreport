from flask import Flask, jsonify
from flask_restplus import Api, Resource, fields
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
import json


class CherrokeeFix(object):

    def __init__(self, app, script_name, scheme):
        self.app = app
        self.script_name = script_name
        self.scheme = scheme

    def __call__(self, environ, start_response):
        path = environ.get('SCRIPT_NAME', '') + environ.get('PATH_INFO', '')
        environ['wsgi.url_scheme'] = self.scheme
        environ['SCRIPT_NAME'] = self.script_name
        environ['PATH_INFO'] = path[len(self.script_name):]
        return self.app(environ, start_response)



app = Flask(__name__)
app.config.from_object('config')
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)
app.wsgi_app = CherrokeeFix(app.wsgi_app, app.config['APP_PREFIX'], app.config['APP_SCHEME'])
api = Api(app=app, version='0.1', title='MReport Api', description='Test API', validate=True)

ns = api.namespace('store', description='Store de dataviz')

@ns.route('/items')
class GetItems(Resource):
    def get(self):
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()
        result = connection.execute("select * from data.dataviz")
        return jsonify({'catalog': json.loads(json.dumps([dict(r) for r in result]))})
        connection.close()



if __name__ == "__main__":
    app.run(host='127.0.0.1')

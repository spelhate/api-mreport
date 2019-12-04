# -*- coding: cp1252 -*-
from flask import Flask, jsonify
from flask_restplus import Api, Resource, fields
from sqlalchemy import create_engine, bindparam, Integer, String
from sqlalchemy.sql import text
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

class Dataviz(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    titre = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(120), index=True, unique=True)
    source = db.Column(db.String(128))
    raws = db.relationship('Data', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<Dataviz {}>'.format(self.id)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataid = db.Column(db.String(140))
    label = db.Column(db.String(140))
    data = db.Column(db.String(140))
    dataviz_id = db.Column(db.String(200), db.ForeignKey('dataviz.id'))

    def __repr__(self):
        return '<Data {}>'.format(self.id)


app.wsgi_app = CherrokeeFix(app.wsgi_app, app.config['APP_PREFIX'], app.config['APP_SCHEME'])
api = Api(app=app, version='0.1', title='MReport Api', description='Test API', validate=True)

ns = api.namespace('store', description='Store de dataviz')

@ns.route('/catalog')
class GetCatalog(Resource):
    def get(self):
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()
        result = connection.execute("select * from data.dataviz")
        data = {'catalog': json.loads(json.dumps([dict(r) for r in result]))}
        return jsonify(**data)
        connection.close()

@ns.route('/reports')
class GetReports(Resource):
    def get(self):
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()
        sql = text("""
            select data.reports_lst.title,
                data.reports.id,
                count(datavizid) as nb
            from data.reports_lst, data.reports
            where data.reports_lst.reportid = data.reports.id
            group by 1,2;
            """)
        result = connection.execute(sql)
        return jsonify({'reports': json.loads(json.dumps([dict(r) for r in result]))})
        connection.close()

@ns.route('/report/<id>', doc={'description': 'Récupération d\'un rapport ex: test'})
@ns.doc(params={'id': 'identifiant du rapport'})
class GetReport(Resource):
    def get(self,id):
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()
        sql = text("""
            select
                distinct data.rawdata.dataid as dataid,
                data.levels.label as label
        from data.rawdata, data.reports, data.levels
        where
            data.rawdata.dataviz = data.reports.datavizid and
            data.rawdata.dataid = data.levels.dataid and
            data.reports.id = :id order by label asc;
        """)
        sql.bindparams(bindparam("id", type_=String))
        result = connection.execute(sql, {"id": id})
        data = []
        return jsonify({'items': json.loads(json.dumps([dict(r) for r in result]))})
        connection.close()

@ns.route('/report/<id>/<idgeo>', doc={'description': 'Récupération des données pour rapport ex: test & 200039022'})
@ns.doc(params={'id': 'identifiant du rapport', 'idgeo': 'id géographique'})
class GetReport(Resource):
    def get(self, id, idgeo):
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()
        sql = text("""
            select
                data.rawdata.dataviz as dataviz,
                data.rawdata.dataid as dataid,
                data.rawdata.dataset as dataset,
                data.rawdata.order as "order",
                data.rawdata.label as label,
                data.rawdata.data as data
        from data.rawdata, data.reports
        where
            data.rawdata.dataviz = data.reports.datavizid and
            data.reports.id = :id and data.rawdata.dataid = :idgeo;
        """)
        sql.bindparams(bindparam("id", type_=String), bindparam("idgeo", type_=String))
        result = connection.execute(sql, {"id": id, "idgeo": idgeo})
        return jsonify(json.loads(json.dumps([dict(r) for r in result])))
        connection.close()





if __name__ == "__main__":
    app.run(host='127.0.0.1')

# -*- coding: cp1252 -*-
from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields
from sqlalchemy import create_engine, bindparam, Integer, String, event, func
#from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.sql import text
from flask_sqlalchemy import SQLAlchemy
import json
from sqlalchemy.schema import CreateSchema, DropSchema

def row2dict(row):
    d = {}
    if(row.__table__.columns):
        for column in row.__table__.columns:
            d[column.name] = str(getattr(row, column.name))
    else:
        print("NB")
    return d
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
schema = app.config['SCHEMA']+"."
db = SQLAlchemy(app)
event.listen(db.metadata, 'before_create', CreateSchema(app.config['SCHEMA']))
event.listen(db.metadata, 'after_drop', DropSchema(app.config['SCHEMA']))
from models import *


app.wsgi_app = CherrokeeFix(app.wsgi_app, app.config['APP_PREFIX'], app.config['APP_SCHEME'])
api = Api(app=app, version='0.1', title='MReport Api', description='Test API', validate=True)

store = api.namespace('store', description='Store de dataviz')
report = api.namespace('report', description='Reports')

@store.route('/')
class GetCatalog(Resource):
    def get(self):
        result = db.session.query(Dataviz)
        data = {'reports': json.loads(json.dumps([row2dict(r) for r in result]))}
        return jsonify(**data)


@store.route('/<string:id>')
class DatavizManagement(Resource):
    def put(self, id):
        data = request.get_json()
        if not data:
            data = {"response": "ERROR"}
            return data, 404
        else:
            if Dataviz.query.get(id):
                return {"response": "dataviz already exists."}, 403
            else:
                dvz = Dataviz(**data)
                #**data will unpack the dict object, so if have data = {'dataviz': 'test', 'name': 'Awesome'}, Dataviz(**data) will do like Dataviz(dataviz='test', name='Awesome')
                db.session.add(dvz)
                db.session.commit()
                return {"response": "success" , "data": data}

    def post(self, id):
        data = request.get_json()
        if not data:
            data = {"response": "ERROR"}
            return data, 404
        else:
            if Dataviz.query.get(id):
                dvz = Dataviz.query.get(id)
                for fld in ["title", "description", "source", "year", "type", "level", "unit", "job"]:
                    value = data.get(fld)
                    if value:
                        setattr(dvz, fld, value)

                db.session.commit()
                return {"response": "success" , "data": data}
            else:
                return {"response": "dataviz doesn't exists."}, 403

    def delete(self, id):
        dvz = Dataviz.query.get(id)
        if dvz:
            db.session.delete(dvz)
            db.session.commit()
            return {"response": "success"}
        else:
            return {"response": "dataviz does not exists."}, 403


@report.route('/')
class GetReports(Resource):
    def get(self):
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()
        result1 = db.session.query(Report,func.count()).join(Report_composition,Report.report == Report_composition.report).group_by(Report.report).all()
        print({'reports': json.loads(json.dumps([row2dict(r) for r in result1]))})
        sql = text("""
            select """+schema+"""report.title,
                """+schema+"""report.report,
                count(dataviz) as nb
            from """+schema+"""report, """+schema+"""report_composition
            where """+schema+"""report.report = """+schema+"""report_composition.report
            group by """+schema+"""report.report;
            """)
        result = connection.execute(sql)
        return jsonify({'reports': json.loads(json.dumps([dict(r) for r in result]))})
        connection.close()

@report.route('/<id>', doc={'description': 'R�cup�ration d\'un rapport ex: test'})
@report.doc(params={'id': 'identifiant du rapport'})
class GetReport(Resource):
    def get(self,id):
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()
        sql = text("""
            select
                distinct """+schema+"""rawdata.dataid as dataid,
                """+schema+"""dataid.label as label
        from """+schema+"""rawdata, """+schema+"""report_composition, """+schema+"""dataid
        where
            """+schema+"""rawdata.dataviz = """+schema+"""report_composition.dataviz and
            """+schema+"""rawdata.dataid = """+schema+"""dataid.dataid and
            """+schema+"""report_composition.report = :id order by label asc;
        """)
        sql.bindparams(bindparam("id", type_=String))
        result = connection.execute(sql, {"id": id})
        data = []
        return jsonify({'items': json.loads(json.dumps([dict(r) for r in result]))})
        connection.close()

@report.route('/<id>/<idgeo>', doc={'description': 'R�cup�ration des donn�es pour rapport ex: test & 200039022'})
@report.doc(params={'id': 'identifiant du rapport', 'idgeo': 'id g�ographique'})
class GetReport(Resource):
    def get(self, id, idgeo):
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()
        sql = text("""
            select
                """+schema+"""rawdata.dataviz as dataviz,
                """+schema+"""rawdata.dataid as dataid,
                """+schema+"""rawdata.dataset as dataset,
                """+schema+"""rawdata.order as "order",
                """+schema+"""rawdata.label as label,
                """+schema+"""rawdata.data as data
        from """+schema+"""rawdata, """+schema+"""report
        where
            """+schema+"""rawdata.dataviz = """+schema+"""report_composition.dataviz and
            """+schema+"""report.report = :id and """+schema+"""rawdata.dataid = :idgeo;
        """)
        sql.bindparams(bindparam("id", type_=String), bindparam("idgeo", type_=String))
        result = connection.execute(sql, {"id": id, "idgeo": idgeo})
        return jsonify(json.loads(json.dumps([dict(r) for r in result])))
        connection.close()





if __name__ == "__main__":
    app.run(host='127.0.0.1')

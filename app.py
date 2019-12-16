# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields
from sqlalchemy import create_engine, bindparam, Integer, String, event, func, inspect, desc
#from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.sql import text
from flask_sqlalchemy import SQLAlchemy
import json
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy.exc import NoInspectionAvailable

## Use for (select *) from a single table ex : {'datavizs': json.loads(json.dumps([row2dict(r) for r in result]))}
def row2dict(row,label="null"):
    d = {}
    try:
        inspect(row)
        if(row.__table__.columns):
            for column in row.__table__.columns:
                d[column.name] = str(getattr(row, column.name))
    except NoInspectionAvailable:
        d[label]=row
    return d
## Use for (select atr1,atr2 ...) ex : {'reports': json.loads(json.dumps(dict_builder(result)))}.
def dict_builder(result):
    dlist = []
    for r in result:
        d={}
        res = r._asdict()
        for key in res:
            d.update(row2dict(res[key],key))
        dlist.append(d)
    return dlist
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
try :
    schema = app.config['SCHEMA']
    event.listen(db.metadata, 'before_create', CreateSchema(schema))
    event.listen(db.metadata, 'after_drop', DropSchema(schema))
except KeyError :
    print("If you want to add a schema edit config.py with SCHEMA variable")
from models import *


app.wsgi_app = CherrokeeFix(app.wsgi_app, app.config['APP_PREFIX'], app.config['APP_SCHEME'])
api = Api(app=app, version='0.1', title='MReport Api', description='Test API', validate=True)

store = api.namespace('store', description='Store de dataviz')
report = api.namespace('report', description='Reports')

@store.route('/')
class GetCatalog(Resource):
    def get(self):
        result = db.session.query(Dataviz).all()
        data = {'datavizs': json.loads(json.dumps([row2dict(r) for r in result]))}
        return jsonify(**data)


@store.route('/<string:id>')
class DatavizManagement(Resource):
    def put(self, id):
        data = request.get_json()
        if not data:
            data = {"response": "ERROR no data supplied"}
            return data, 405
        else:
            if Dataviz.query.get(id):
                return {"response": "dataviz already exists."}, 403
            else:
                dvz = Dataviz(**data)
                #**data will unpack the dict object, so if have data = {'dataviz': 'test', 'name': 'Awesome'}, Dataviz(**data) will do like Dataviz(dataviz='test', name='Awesome')
                db.session.add(dvz)
                db.session.commit()
                return {"response": "success" , "data": data, "dataviz":id}

    def post(self, id):
        data = request.get_json()
        if not data:
            data = {"response": "ERROR no data supplied"}
            return data, 405
        else:
            if Dataviz.query.get(id):
                dvz = Dataviz.query.get(id)
                for fld in ["title", "description", "source", "year", "type", "level", "unit", "job"]:
                    value = data.get(fld)
                    if value:
                        setattr(dvz, fld, value)

                db.session.commit()
                return {"response": "success" , "data": data, "dataviz":id}
            else:
                return {"response": "dataviz doesn't exists."}, 404


    def delete(self, id):
        dvz = Dataviz.query.get(id)
        if dvz:
            db.session.delete(dvz)
            db.session.commit()
            return {"response": "success", "dataviz":id}
        else:
            return {"response": "dataviz does not exists."}, 404


@report.route('/')
class GetReports(Resource):
    def get(self):
        result = db.session.query(Report,func.count().label('nb')).join(Report_composition,Report.report == Report_composition.report).group_by(Report.report).all()
        '''
                db.session.query(Report,func.count().label('nb'))
                .join(Report_composition,Report.report == Report_composition.report)
                .group_by(Report.report)
                .all()
        '''
        data = {'reports': json.loads(json.dumps(dict_builder(result)))}
        return jsonify(**data)

@report.route('/<id>', doc={'description': 'Récupération d\'un rapport ex: test'})
@report.doc(params={'id': 'identifiant du rapport'})
class GetReport(Resource):
    def get(self,id):
        result = db.session.query(Rawdata.dataid.label("dataid"),Dataid.label.label("label")).distinct().join(Report_composition,Rawdata.dataviz == Report_composition.dataviz).join(Dataid,Dataid.dataid == Rawdata.dataid).filter(Report_composition.report == id).order_by(desc(Dataid.label)).all()
        '''
                db.session.query(Rawdata.dataid.label("dataid"),Dataid.label.label("label"))
                .distinct()
                .join(Report_composition,Rawdata.dataviz == Report_composition.dataviz)
                .join(Dataid,Dataid.dataid == Rawdata.dataid)
                .filter(Report_composition.report == id)
                .order_by(desc(Dataid.label))
                .all()
        '''
        data = {'items': json.loads(json.dumps(dict_builder(result)))}
        return jsonify(**data)

@report.route('/<id>/<idgeo>', doc={'description': 'Récupération des données pour rapport ex: test & 200039022'})
@report.doc(params={'id': 'identifiant du rapport', 'idgeo': 'id géographique'})
class GetReport(Resource):
    def get(self, id, idgeo):
        result = db.session.query(Rawdata).join(Report_composition,Rawdata.dataviz == Report_composition.dataviz).filter(Report_composition.report == id).filter(Rawdata.dataid == idgeo).all()
        '''
                db.session.query(Rawdata)
                .join(Report_composition,Rawdata.dataviz == Report_composition.dataviz)
                .filter(Report_composition.report == id)
                .filter(Rawdata.dataid == idgeo)
                .all()
        '''
        data = {'geo': json.loads(json.dumps([row2dict(r) for r in result]))}
        return jsonify(**data)
if __name__ == "__main__":
    app.run(host='127.0.0.1')

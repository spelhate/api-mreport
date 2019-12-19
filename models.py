from app import db, app
tableschema = {}
schema = ""
try :
    schema = app.config['SCHEMA']
    tableschema={'schema': schema}
    schema = schema+'.'
except KeyError :
    pass
    
    
class Dataviz(db.Model):
    dataviz = db.Column(db.String(50),primary_key=True)
    title = db.Column(db.String(200),nullable=False)
    description = db.Column(db.String(250))
    source = db.Column(db.String(200),nullable=False)
    year = db.Column(db.String(4))
    unit = db.Column(db.String(50))
    type = db.Column(db.String(200),nullable=False)
    level = db.Column(db.String(50),nullable=False)
    job = db.Column(db.String(50))
    report_composition_dvz = db.relationship('Report_composition', backref="report1", cascade="all, delete-orphan" , lazy='dynamic')
    rawdata_dvz = db.relationship('Rawdata', backref="rawdata1", cascade="all, delete-orphan", lazy='dynamic')

    __table_args__ = (tableschema)
    def __repr__(self):
        return '<Dataviz {}>'.format(self.dataviz)

class Dataid(db.Model):
    dataid = db.Column(db.String(50),primary_key=True,index=True)
    label = db.Column(db.String(250),nullable=False)
    rawdata_dataid = db.relationship('Rawdata', backref="rawdata2", cascade="all, delete-orphan", lazy='dynamic')
    __table_args__ = (
        tableschema
    )
    def __repr__(self):
        return '<Dataid {}>'.format(self.dataid)

class Rawdata(db.Model):
    dataviz = db.Column(db.String(50),db.ForeignKey(schema+'dataviz.dataviz'),index=True,nullable=False)
    dataid = db.Column(db.String(50),db.ForeignKey(schema+'dataid.dataid'),index=True,nullable=False)
    dataset = db.Column(db.String(50),nullable=False)
    order = db.Column(db.Integer,nullable=False)
    label = db.Column(db.String(250))
    data = db.Column(db.String(250))
    __table_args__ = (
        db.PrimaryKeyConstraint('dataviz', 'dataid', 'dataset', 'order'),
        tableschema
    )
    def __repr__(self):
        return '<Rawdata {}>'.format(self.dataviz)

class Report(db.Model):
    report = db.Column(db.String(50),primary_key=True)
    title = db.Column(db.String(250),nullable=False)
    report_composition_rep = db.relationship('Report_composition', backref="report2", cascade="all, delete-orphan" , lazy='dynamic')
    __table_args__ = (tableschema)
    def __repr__(self):
        return '<Report {}>'.format(self.report)

class Report_composition(db.Model):
    report = db.Column(db.String(50),db.ForeignKey(schema+'report.report'),nullable=False)
    dataviz = db.Column(db.String(50),db.ForeignKey(schema+'dataviz.dataviz'),nullable=False)
    __table_args__ = (
        db.PrimaryKeyConstraint('report', 'dataviz'),
        tableschema
    )
    def __repr__(self):
        return '<Report_composition {}>'.format(self.report)


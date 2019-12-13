from app import db, app
schema = app.config['SCHEMA']+'.'
class Dataviz(db.Model):
    dataviz = db.Column(db.String(50),primary_key=True)
    title = db.Column(db.String(200),nullable=False)
    description = db.Column(db.String(250),nullable=False)
    source = db.Column(db.String(200),nullable=False)
    year = db.Column(db.String(4))
    unit = db.Column(db.String(50))
    type = db.Column(db.String(200),nullable=False)
    level = db.Column(db.String(50),nullable=False)
    job = db.Column(db.String(50))


    __table_args__ = ({'schema': app.config['SCHEMA']})
    def __repr__(self):
        return '<Dataviz {}>'.format(self.dataviz)
    def to_json(self):
        return dict(dataviz=self.dataviz,
                    title=self.title,
                    description=self.description,
                    source=self.source,
                    year=self.year,
                    unit=self.unit,
                    type=self.type,
                    level=self.level,
                    job=self.job)

class Dataid(db.Model):
    dataid = db.Column(db.String(50),primary_key=True,index=True)
    label = db.Column(db.String(250),nullable=False)
    __table_args__ = (
        {'schema': app.config['SCHEMA']}
    )
    def __repr__(self):
        return '<Dataid {}>'.format(self.dataid)
    def to_json(self):
        return dict(dataid=self.dataid,
                    label=self.label)
class Rawdata(db.Model):
    dataviz = db.Column(db.String(50),db.ForeignKey(schema+'dataviz.dataviz'),index=True,nullable=False)
    dataid = db.Column(db.String(50),db.ForeignKey(schema+'dataid.dataid'),index=True,nullable=False)
    dataset = db.Column(db.String(50),nullable=False)
    order = db.Column(db.Integer,nullable=False)
    label = db.Column(db.String(250))
    data = db.Column(db.String(250))
    __table_args__ = (
        db.PrimaryKeyConstraint('dataviz', 'dataid', 'dataset', 'order'),
        {'schema': app.config['SCHEMA']}
    )
    def __repr__(self):
        return '<Rawdata {}>'.format(self.dataviz)
    def to_json(self):
        return dict(dataviz=self.dataviz,
                    dataid=self.dataid,
                    dataset=self.dataset,
                    order=self.order,
                    label=self.label,
                    data=self.data)

class Report(db.Model):
    report = db.Column(db.String(50),primary_key=True)
    title = db.Column(db.String(250),nullable=False)
    __table_args__ = ({'schema': app.config['SCHEMA']})
    def __repr__(self):
        return '<Report {}>'.format(self.report)
    def to_json(self):
        return dict(report=self.report,
                    title=self.title)

class Report_composition(db.Model):
    report = db.Column(db.String(50),db.ForeignKey(schema+'report.report'),nullable=False)
    dataviz = db.Column(db.String(50),db.ForeignKey(schema+'dataviz.dataviz'),nullable=False)
    __table_args__ = (
        db.PrimaryKeyConstraint('report', 'dataviz'),
        {'schema': app.config['SCHEMA']}
    )
    def __repr__(self):
        return '<Report_composition {}>'.format(self.report)
    def to_json(self):
        return dict(report=self.report,
                    dataviz=self.dataviz)


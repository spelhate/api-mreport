from app import db

class Dataviz(db.Model):
    dataviz = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(200),nullable=False)
    description = db.Column(db.String(250),nullable=False)
    source = db.Column(db.String(200),nullable=False)
    year = db.Column(db.String(4))
    unit = db.Column(db.String(50))
    type = db.Column(db.String(200),nullable=False)
    level = db.Column(db.String(50),nullable=False)
    job = db.Column(db.String(50))
    
    __table_args__ = {'schema': 'data'}
    
    def __repr__(self):
        return '<Dataviz {}>'.format(self.dataviz)
class Rawdata(db.Model):
    dataviz = db.Column(db.String(50),db.ForeignKey('dataviz.dataviz'),index=True,nullable=False)
    dataid = db.Column(db.String(50),nullable=False)
    dataset = db.Column(db.String(50),nullable=False)
    order = db.Column(db.Integer,nullable=False)
    label = db.Column(db.String(250))
    data = db.Column(db.String(250))
    __table_args__ = (
        PrimaryKeyConstraint('dataviz', 'dataid', 'dataset', 'order'),
        {},
    )
    def __repr__(self):
        return '<Rawdata {}>'.format(self.dataviz)


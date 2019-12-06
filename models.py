from app import db

class Dataviz(db.Model):
    dataviz = db.Column(db.String(50), primary_key=True)
    titre = db.Column(db.String(200))
    description = db.Column(db.String(250))
    source = db.Column(db.String(200))
    millesime = db.Column(db.String(4))
    type = db.Column(db.String(200))
    niveau = db.Column(db.String(50))
    job = db.Column(db.String(50))
    
    __table_args__ = {'schema': 'data'}
    

    def __repr__(self):
        return '<Dataviz {}>'.format(self.dataviz)


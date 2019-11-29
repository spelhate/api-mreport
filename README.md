# api-mreport
flask api for mreport

Install
---------
::
    # clone the repository
    $ git clone https://github.com/spelhate/api-mreport.git
    $ cd api-mreport


Create a virtualenv and activate it

::

    $ python3 -m venv venv
    $ . venv/bin/activate


Install Flask and dependencies

::

    $ pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt



Configure
---------

::

Edit config.py and set SQLALCHEMY_DATABASE_URI



Run
---

::

    $ export FLASK_APP=app
    $ flask run


Deploy with apache and gunicorn
--------------------------------

In apache conf

::

<Location "/api">
	 Header set Access-Control-Allow-Origin "*"
  	 Header set Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization"
     ProxyPass "http://127.0.0.1:5000/api/"
  	 ProxyPassReverse "http://127.0.0.1:5000/api/"
</Location>

logs

::

mkdir /var/log/api-mreport

set write rights to the api user

Test gunicorn

::

gunicorn -c gunicorn.conf -b 0.0.0.0:5000 app:app

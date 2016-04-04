**Note: This README is out of date. TODO.**

server: the DB + "manager"
==========================

centralized "manager" of the rest of the system: DB; API endpoint for
controllers and the outside world

Setup
-----

**Required Python version: 3.4**

1. Create virtualenv if necessary: `pyvenv ./venv` (or `pyvenv-3.4 ./venv`)
2. Activate virtualenv:
   - bash, zsh: `source venv/bin/activate`
   - fish: `. venv/bin/activate.fish`
   - csh, tcsh: `source venv/bin/activate.csh`
3. Install dependencies if necessary: `pip install -r requirements.txt`
4. configure: `cp config.py{.example,}; $EDITOR config.py`
5. create DB tables: `psql -U <dbuser> <dbname> -f dbinit.sql`
6. run with `./runserver.py`;  
   run the HTTP API server with `./runhttp.py`

Running tests
-------------

1. Edit configuration: `cp tests/config.py{.example,}; $EDITOR tests/config.py`  
   A real Postgres DB is used, you need to specify the connection string.
2. create DB tables: `psql -U <testdbuser> <testdbname> -f dbinit.sql`
3. run with `py.test tests/`  
   or `py.test --cov gateserver/ --cov-report term-missing tests/` for coverage report

Next to do:
-----------

- split DB table to controller and door
- on request arrival check if client IP matches the one in DB for this ID
- HTTP: rewrite to use Werkzeug instead of CherryPy
- fix DB singleton (who wants a singleton?!)
- CI

Style Guide & such
------------------

[PEP-8](https://www.python.org/dev/peps/pep-0008/), `import this`. Also: code and design reviews.

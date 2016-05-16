server: the DB + "manager"
==========================

centralized "manager" of the rest of the system: DB; API endpoint for
controllers and the outside world

Deployment TL;DR
----------------

1. virtualenv with Python 3.4 or 3.5
2. `pip install -r requirements.txt`
3. `cp config/local.py{.example,}; $EDITOR config/local.py`
4. `./deadcli newdb --yes`
5. run what you want with `./run*.py` or `make runall` or your favorite Procfile thing

Development Quick-Start
-----------------------

**Required Python version: 3.4 or 3.5**

1. Create virtualenv if necessary: `pyvenv ./venv` (or `pyvenv-3.4 ./venv`)
2. Activate virtualenv:
   - bash, zsh: `source venv/bin/activate`
   - fish: `. venv/bin/activate.fish`
   - csh, tcsh: `source venv/bin/activate.csh`
3. Install dependencies if necessary: `pip install -r requirements.txt`
   (or use `requirements-fresh.txt` for up-to-date instead of frozen dependencies)
4. configure: `cp config/local.py{.example,}; $EDITOR config/local.py`
5. create DB tables: `./deadcli newdb --yes`
   optionally add `--extra sql/99-testdata.sql` or whatever you like
6. run components with `./run*.py` or your favorite Procfile thing

Next to do:
-----------

- fix DB: use psycopg directly, maybe with a simple named args wrapper if it can be made simple
  + then commit explicitly (on cursor.close / contextmanager)
- HTTP API
- CI
- rename "accesspoint" to "poa" everywhere :D

Style Guide & such
------------------

- [PEP-8](https://www.python.org/dev/peps/pep-0008/)
  - linting with `pep8 --ignore=E221,E241,E302,E701 --max-line-length=100`
- `import this`
- design and code reviews

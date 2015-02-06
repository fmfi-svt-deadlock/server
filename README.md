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
5. bootstrap (create DB tables and such): `./bootstrap.py`
6. run with `./run.py` (or `while true; do sleep 0.1; ./run.py; done`, as the
   server will stop when the code changes => auto-restart on save ^_^)

The rest doesn't exist yet.

Next to do:
-----------

- listen on UDP socket
- wrap/unwrap NaCl
- fix DB singleton (who wants a singleton?!) -- inversion of control
- CI

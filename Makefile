DB_URL = $(shell python -c 'import config; print(config.db_url)')

runall:
	python runsrv.py --log=DEBUG > deadsrv.log &
	python runapi.py --log=DEBUG > deadapi.log &
	python runaux.py --log=DEBUG > deadaux.log &

watch:
	echo Not implemented yet

clean:
	find . -name *.pyc -exec rm {} \;
	find . -depth -name __pycache__ -exec rm -r {} \;
	rm -rf .cache
	rm -f *.log

newdb_really_destroy_everything:
	psql ${DB_URL} -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
	for f in sql/*.sql ; do psql ${DB_URL} -f $$f ; done

psql:
	psql ${DB_URL}

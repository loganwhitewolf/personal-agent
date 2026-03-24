run:
	cd agent && op run --env-file ../.env.template -- python main.py

run-now:
	cd agent && op run --env-file ../.env.template -- env RUN_NOW=true python main.py

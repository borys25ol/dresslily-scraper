ve:
	test ! -d .ve && python3 -m venv .ve; \
	. .ve/bin/activate; \
	pip install -r requirements.txt; \

clean:
	test -d .ve && rm -rf .ve
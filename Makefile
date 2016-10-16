release:
	python setup.py sdist upload

build_docs:
	sphinx-build -b html docs/ docs/_build/

tests:
	py.test -sv aiolocust/test

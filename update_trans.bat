pybabel extract -F babel.cfg -k _l -o translations/_messages.pot .
pybabel update -i translations/_messages.pot -d translations
pybabel compile -d translations
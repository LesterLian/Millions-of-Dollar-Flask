pybabel extract -F babel.cfg -o translations/_messages.pot .
pybabel update -i translations/_messages.pot -d translations
pybabel compile -d translations
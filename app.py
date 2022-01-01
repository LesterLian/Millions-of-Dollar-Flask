from flask import Flask, abort, json, send_from_directory, redirect, url_for, render_template, make_response, request
from xml.etree.ElementTree import tostring, parse as parse_xml, Element, SubElement

from random import shuffle
from bisect import bisect_left

from flask.wrappers import Response


# 4, 5-6, 7
NUM_OF_CARDS = [
    # (3, ),
    (4, 3),
    (6, 4),
    (7, 5),
]

app = Flask(__name__, static_url_path='/public')
cards = []
shuffled = False
num = 4

# Serve files in public
@app.route('/<path:path>')
def send_file(path):
    if path in ['favicon.ico', 'rss.xsl'] or 'images/' in path:
        return send_from_directory('public', path)
    abort(404)

@app.route('/')
def index():
    return redirect('index')

@app.route('/index')
def get_index():
    global num

    if 'num' in request.args:
        num = int(request.args['num'])
    if num < 4:
        return abort(Response('Number of player must greater than 4'), 500)
    ind = bisect_left(NUM_OF_CARDS, (num,))
    return render_template('index.html', state='planning', num=NUM_OF_CARDS[ind][1])

@app.route('/sub')
def submit_card():
    cards.append(request.args['card'])
    
    return render_template('index.html', state='planning', num=0), {"Refresh": f"1; url=show"}

@app.route('/show')
def show_cards():
    global shuffled, num, old_cards

    if len(cards) < num:
        return 'Wait', {"Refresh": f"1; url=show"}
    if not shuffled:
        shuffle(cards)
        shuffled = True
        old_cards = cards.copy()
        
    
    return render_template('index.html', state='negotiation', cards=cards[1:])

@app.route('/all')
def show_all():
    global old_cards
    
    return render_template('index.html', state='loot', cards=old_cards)

@app.route('/reset')
def reset_game():
    global shuffled, cards, num

    cards.clear()
    shuffled = False
    
    return redirect(f'index?num={num}')

from flask import Flask, abort, json, send_from_directory, redirect, url_for, render_template, make_response, request
from flask.wrappers import Response
from flask_babel import Babel, _, lazy_gettext as _l

from random import shuffle
import secret, hashlib, hmac, threading, time, os


app = Flask(__name__, static_url_path='/public')
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'
babel = Babel(app)

ROLES = {
    'brute': _l('Brute'),
    'crook': _l('Crook'),
    'driver': _l('Driver'),
    'snitch': _l('Snitch'),
    'mastermind': _l('Mastermind'),
    'unknown': _l('Unknown')
}
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
        return abort(Response(_('Number of player must be greater than 4')), 500)
    elif num < 5:
        role_num = 3
    elif num < 7:
        role_num = 4
    elif num > 8:
        return abort(Response(_('Number of player must be lesser than 8')), 500)
    else:
        role_num = 5
    
    return render_template('index.html', state='planning', roles=list(ROLES.items())[:role_num])

@app.route('/sub')
def submit_card():

    if len(cards) < num:
        cards.append(request.args['card'])
        message = _('Success! You have submitted your role!')
    else:
        message = _('Error! Role number exceeded!')
    
    return render_template('index.html', state='submitted', message=message), {"Refresh": f"1; url=show"}

@app.route('/show')
def show_cards():
    global shuffled, num, old_cards

    if len(cards) < num:
        return _('Waiting others...'), {"Refresh": f"1; url=show"}
    if not shuffled:
        shuffle(cards)
        shuffled = True
        old_cards = cards.copy()
    tmp = [(role, ROLES[role]) for role in ['unknown'] + cards[1:]]
    print(tmp)
    
    return render_template('index.html', state='negotiation', cards=tmp)

@app.route('/all')
def show_all():
    global old_cards
    
    return render_template('index.html', state='loot', cards=[(role, ROLES[role]) for role in old_cards])

@app.route('/reset')
def reset_game():
    global shuffled, cards

    cards.clear()
    shuffled = False
    
    return redirect(f'index')

@app.route('/hook', methods=['POST'])
def webhook():
    # X-Hub-Signature-256: sha256=<hash>
    sig_header = 'X-Hub-Signature-256'
    if sig_header not in request.headers:
        return ''
    header_splitted = request.headers[sig_header].split("=")
    if len(header_splitted) != 2:
        return ''
    req_sign = header_splitted[1]
    computed_sign = hmac.new(secret.webhook, request.data, hashlib.sha256).hexdigest()
    # is the provided signature ok?
    if not hmac.compare_digest(req_sign, computed_sign):
        return ''
    # create a thread to return a response (so GitHub is happy) and start a 2s timer before exiting this app
    # this is supposed to be run by systemd unit which will restart it automatically
    # the [] syntax for lambda allows to have 2 statements
    threading.Thread(target=lambda: [print("Exit called", flush=True), time.sleep(2), os._exit(-1)]).start()
    return "ok"

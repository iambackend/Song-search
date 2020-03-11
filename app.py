from flask import Flask, render_template, request

import search_engine as se

app = Flask(__name__)

collection = None
index = None
soundex_index = None
permuterm = None
rebuild = None
lock = None
auxiliary_add, auxiliary_drop = None, None

def rebuild_indeces(from_disc=False):
    global collection, index, soundex_index, permuterm, rebuild, lock
    with lock:
        if from_disc:
            index = se.Index()
        else:
            index = se.Index(collection)
        soundex_index = se.form_soundex(index.keys())
        permuterm = se.do_permuterm(index.keys())
        rebuild = False


def get_aux(collection):
    index = se.Index(collection)
    soundex_index = se.form_soundex(index.keys())
    permuterm = se.do_permuterm(index.keys())
    return index, soundex_index, permuterm


@app.route('/', methods=['GET'])
def main_page():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get("query")
    print(len(auxiliary_add))
    if rebuild:
        rebuild_indeces()
        return "its working"
    with lock:
        relevant = se.fancy_search(collection, index, permuterm, soundex_index, query)
        aux_index, aux_soundex, aux_permuterm = get_aux(auxiliary_add)
        relevant.extend(se.fancy_search(auxiliary_add, aux_index, aux_soundex, aux_permuterm, query))
        relevant = [song for song in relevant if song not in auxiliary_drop]
    return render_template('results.html', query=query, songs=relevant, res_num=len(relevant))


def run_flask(*args):
    global collection, index, soundex_index, permuterm, rebuild, lock, auxiliary_add, auxiliary_drop
    collection, auxiliary_add, auxiliary_drop, lock, rebuild = args
    if rebuild:
        rebuild_indeces(from_disc=False)
    else:
        rebuild_indeces(from_disc=False)
    app.run()

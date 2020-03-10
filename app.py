from flask import Flask, render_template, request

import search_engine as se

app = Flask(__name__)

collection = None
index = None
soundex_index = None
permuterm = None


@app.route('/', methods=['GET'])
def main_page():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get("query")
    relevant = se.fancy_search(collection, index, permuterm, soundex_index, query)
    return render_template('results.html', query=query, songs=relevant)

def run_flask():
    global collection, index, soundex_index, permuterm
    collection = se.get_collection(100)
    try:
        index = se.Index()
    except:
        index = se.Index(collection)
    soundex_index = se.form_soundex(index.keys())
    permuterm = se.do_permuterm(index.keys())
    app.run()

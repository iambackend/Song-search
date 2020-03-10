import search_engine as se

collection = se.get_collection(100)
try:
    index = se.Index()
except:
    index = se.Index(collection)
soundex_index = se.form_soundex(index.keys())
permuterm = se.do_permuterm(index.keys())

def()
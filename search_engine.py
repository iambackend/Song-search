import json
import unicodedata

# normalize text
from string import ascii_lowercase


def normalize(text):
    # text = text.lower()
    # print(text)
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub('[,.\n]', ' ', text)
    return re.sub('[^a-zA-Z *|]', '', text).lower()


# tokenize text using nltk lib
import nltk

nltk.download('punkt')


def tokenize(text):
    return nltk.word_tokenize(text)


from nltk.stem import WordNetLemmatizer

nltk.download('wordnet')


def lemmatization(tokens):
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]


from nltk.corpus import stopwords

nltk.download('stopwords')


def remove_stop_word(tokens):
    stop_words = set(stopwords.words('english'))
    return [token for token in tokens if token not in stop_words]


def preprocess(text):
    return remove_stop_word(lemmatization(tokenize(normalize(text))))


import requests


class Document:

    def __init__(self, url):
        self.url = url
        self.content = None

    def get_file_name(self):
        return self.url.replace('/', '\\')

    def get(self):
        if not self.load():
            if self.download():
                self.persist()
            else:
                return False

    def download(self):
        r = requests.get(self.url)
        if r.status_code != 200:
            return False
        self.content = r.content
        return True

    def persist(self):
        with open("cache/" + self.get_file_name(), 'wb') as file:
            file.write(self.content)

    def load(self):
        try:
            file = open("cache/" + self.get_file_name(), 'rb')
            self.content = file.read()
            file.close()
        except:
            return False
        return True


from bs4 import BeautifulSoup as bs
from bs4.element import Comment


class Song(Document):

    # from stackoverflow
    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def text_from_html(self, body):
        soup = bs(body, 'html.parser')
        texts = soup.find(id="lyric-body-text").findAll(text=True)
        visible_texts = filter(self.tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)

    def parse(self):
        try:
            with open("cache/" + self.get_file_name() + "parsed", "r") as file:
                dict = json.load(file)
                self.artist = dict["artist"]
                self.title = dict["title"]
                self.text = dict["text"]
        except:
            self.get()
            soup = bs(self.content)
            self.artist = soup.find(class_="lyric-artist").get_text()[:-16]  # there is "Buy this song" in the end.
            self.title = soup.find(class_="lyric-title").get_text()
            self.text = self.text_from_html(self.content)
            _dict = self.__dict__
            del _dict['content']
            # del _dict['url']
            with open("cache/" + self.get_file_name() + "parsed", "w") as file:
                json.dump(_dict, file)

# I took this code from my room mate, cause it is the task from previous lab, and i did it, but my solution is too slow.
ORIGIN = 'https://www.lyrics.com/'


def getArtists(total=1000):
    for i in ascii_lowercase:
        res = requests.get(ORIGIN + 'artists/' + i + '/99999')
        if not res:
            print('GET failed with ' + res.status_code)
            continue
        page = bs(res.content, 'html.parser')
        rows = page.find(id='content-body').div.find(class_='tdata-ext').table.tbody
        artists = []
        pattern = re.compile('[0-9]+$')
        for row in rows.contents:
            link = row.contents[0].a or row.contents[0].strong.a
            artists.append((pattern.search(link['href']).group(0), link.contents[0]))
            if len(artists) > total:
                break
        return artists


def getSongsOf(artist, total=1000):
    name = artist[1].replace(' ', '-')
    res = requests.get(ORIGIN + 'artist.php?name=' + name + '&aid=' + artist[0] + '&o=1')
    if not res:
        print('GET failed with ' + res.status_code)
        return
    page = bs(res.content, 'html.parser')
    if page.find(id='content-body').find(class_='tdata-ext') is None:
        return None
    rows = page.find(id='content-body').find(class_='tdata-ext').table.tbody
    songs = []
    pattern = re.compile('[0-9]+')
    for row in rows.contents:
        # print(row)
        if row.contents[0].strong:
            link = row.contents[0].strong.a
        else:
            link = row.contents[0].a
        id_ = pattern.search(link['href']).group(0)
        song = Song('https://www.lyrics.com/lyric/' + id_)
        # song.get()
        try:
            song.parse()
            songs.append(song)
        except Exception as e:
            print(e)
        if len(songs) > total:
            break
    return songs


def get_collection(total=1000):
    artists = getArtists(total)
    songs = []
    for a in artists:
        print('artist ', a, len(songs))
        songs += getSongsOf(a, total - len(songs)) or []
        if len(songs) >= total:
            break
    return songs


class Index:

    def __init__(self, collection=None):
        if collection is None:
            with open("cache/index.json", "r") as file:
                self.inverted_index = json.load(file)
        else:
            self.make_index(collection)
            self.save_index()

    def make_index(self, collection):
        self.inverted_index = {}
        i = 0
        for song in collection:
            lemmas = []
            lemmas.extend(preprocess(song.artist))
            lemmas.extend(preprocess(song.title))
            lemmas.extend(preprocess(song.text))
            # print(lemmas)
            lemmas = set(lemmas)
            for lemma in lemmas:
                if lemma in self.inverted_index:
                    self.inverted_index[lemma].append(i)
                else:
                    self.inverted_index[lemma] = [i]
            i += 1

    def save_index(self):
        with open("cache/index.json", "w") as file:
            json.dump(self.inverted_index, file)

    def __getitem__(self, item):
        return self.inverted_index[item]

    def __iter__(self):
        for word in self.inverted_index:
            yield

    def __contains__(self, item):
        return item in self.inverted_index

    def keys(self):
        return self.inverted_index.keys()


# never used, lol
def search_and(collection, index, query):
    relevant_documents = range(len(collection))
    for lemma in query:
        relevant_documents = [i for i in index[lemma] if i in relevant_documents]
    return relevant_documents


def levenshtein(word1, word2):
    len1 = len(word1) + 1
    len2 = len(word2) + 1
    m = [[0 for i in range(len2)] for j in range(len1)]
    for i in range(len1):
        m[i][0] = i
    for i in range(len2):
        m[0][i] = i
    for i in range(1, len1):
        for j in range(1, len2):
            m[i][j] = min(m[i - 1][j - 1] + (0 if word1[i - 1] == word2[j - 1] else 1),
                          m[i - 1][j] + 1,
                          m[i][j - 1] + 1)
    return m[len1 - 1][len2 - 1]


import re


def soundex(word):
    word = word.upper()
    word = re.sub('[^A-Za-z]', '', word)
    first = word[0]
    word = word[1:]
    word = re.sub('[AEIOUHWY]', '0', word)
    word = re.sub('[BFPV]', '1', word)
    word = re.sub('[CGJKQSXZ]', '2', word)
    word = re.sub('[DT]', '3', word)
    word = re.sub('[L]', '4', word)
    word = re.sub('[MN]', '5', word)
    word = re.sub('[R]', '6', word)
    new_word = ""
    for i in range(len(word) - 1):
        if word[i] != word[i + 1]:
            new_word += word[i]
    word = new_word
    word = re.sub('0', '', word) + "000"
    return first + word[:3]


def form_soundex(vocabulary):
    soundex_index = {}
    for word in vocabulary:
        processed = soundex(word)
        if processed not in soundex_index:
            soundex_index[processed] = [word]
        else:
            soundex_index[processed].append(word)
    return soundex_index


def do_permuterm(vocabulary):
    permuterm = {}
    for term in vocabulary:
        termx = term + '$'
        for i in range(len(termx)):
            # print(termx, termx[-1], termx[:-1])
            permuterm[termx] = term
            termx = termx[-1] + termx[:-1]
    return permuterm


def matching_prefixes(term, permuterm):
    res = []
    for key in permuterm.keys():
        if key.startswith(term):
            res.append(permuterm[key])
    return res


def search_permuterm(term, permuterm):
    parts = term.split("*")
    if len(parts) == 1:
        if term + '$' not in permuterm:
            return []
        else:
            return permuterm[term + '$']
    elif len(parts) == 2:
        if parts[1] == "":
            search_term = "$" + parts[0]
            return matching_prefixes(search_term, permuterm)
        elif parts[0] == "":
            search_term = parts[1] + '$'
            return matching_prefixes(search_term, permuterm)
        else:
            search_term = parts[1] + '$' + parts[0]
            return matching_prefixes(search_term, permuterm)
    return parts


def search_or(collection, index, query):
    relevant_documents = [0] * len(collection)
    for lemma in query:
        for i in index[lemma]:
            relevant_documents[i] = 1
    res = []
    for i in range(len(collection)):
        if relevant_documents[i] == 1:
            res.append(i)
    return res


def merge_and(results):
    res = []
    for doc in results[0]:
        bit = True
        for result in results[1:]:
            if doc not in result:
                bit = False
                break
        if bit:
            res.append(doc)
    return res


def fancy_search(collection, index, permuterm, soundex_index, query):
    query = preprocess(query)
    res = range(len(collection))
    for word in query:
        if word in index:
            # print(word + " is regular")
            docs = index[word]
            res = [doc for doc in res if doc in docs]
        elif '*' in word:
            # print(word + " is wildcard")
            terms = search_permuterm(word, permuterm)
            # print(terms)
            if len(terms) == 0:
                return []
            docs = search_or(collection, index, terms)
            res = [doc for doc in res if doc in docs]
        else:
            # print(word + " is misspell")
            try:
                terms = soundex_index[soundex(word)]
            except KeyError:
                return []
            min_dis = 1000
            for term in terms:
                min_dis = min(levenshtein(term, word), min_dis)
            terms = [term for term in terms if levenshtein(term, word) == min_dis]
            # print(terms)
            docs = search_or(collection, index, terms)
            res = [doc for doc in res if doc in docs]
    return [collection[i] for i in res]

# permuterm = do_permuterm(index.keys())
# relevant = fancy_search(index, permuterm, soundex_index, "see is g*t lifee")
# print(len(relevant))
# print(relevant[0])
# print(relevant[0].artist)
# print(relevant[0].title)
# print(relevant[0].text)

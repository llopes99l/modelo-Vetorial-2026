import os
import sys
import math
import time
import re
import unicodedata
from flask import Flask, jsonify, request, render_template

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from processador import ProcessadorTexto
from indice import IndiceInvertido
from recuperador import RecuperadorVetorial
import indexador

app = Flask(__name__)

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, 'storage')
DEFAULT_DIR = os.path.join(BASE_DIR, 'data')

_cache: dict = {}


def _db_path(dir_col: str) -> str:
    nome = os.path.basename(os.path.normpath(dir_col))
    return os.path.join(STORAGE_DIR, f'indice_{nome}.json')


def _get_idx(dir_col: str) -> IndiceInvertido:
    path = _db_path(dir_col)
    if path not in _cache:
        if not os.path.exists(path):
            indexador.executar(dir_col, path)
        idx = IndiceInvertido()
        idx.carregar(path)
        _cache[path] = idx
    return _cache[path]


def _normalize(text: str) -> str:
    nfkd = unicodedata.normalize('NFD', text.lower())
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn')


def _get_snippet(dir_col: str, doc_name: str, query_terms: list, max_len: int = 220) -> str:
    path = os.path.join(dir_col, doc_name)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read().replace('\n', ' ').strip()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        best, best_score = None, 0
        for sentence in sentences:
            norm  = _normalize(sentence)
            score = sum(1 for t in query_terms if t in norm)
            if score > best_score:
                best_score, best = score, sentence.strip()
        if best:
            return (best[:max_len] + '…') if len(best) > max_len else best
        return (text[:max_len] + '…') if len(text) > max_len else text
    except Exception:
        return ''


def _listar_colecoes() -> list:
    result = []
    if os.path.isdir(DEFAULT_DIR):
        docs = [f for f in os.listdir(DEFAULT_DIR) if f.endswith('.txt')]
        if docs:
            result.append({'nome': 'data', 'path': DEFAULT_DIR, 'total': len(docs)})
    cols_dir = os.path.join(BASE_DIR, 'collections')
    if os.path.isdir(cols_dir):
        for item in sorted(os.listdir(cols_dir)):
            full = os.path.join(cols_dir, item)
            if os.path.isdir(full):
                docs = [f for f in os.listdir(full) if f.endswith('.txt')]
                if docs:
                    result.append({'nome': item, 'path': full, 'total': len(docs)})
    return result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/collections')
def get_collections():
    return jsonify(_listar_colecoes())


@app.route('/api/search', methods=['POST'])
def search():
    t0      = time.time()
    body    = request.json or {}
    query   = body.get('query', '').strip()
    dir_col = body.get('collection_path', DEFAULT_DIR)

    if not query:
        return jsonify({'error': 'Query vazia'}), 400

    idx = _get_idx(dir_col)
    rec = RecuperadorVetorial(idx, ProcessadorTexto())

    v_q = rec.gerar_vetor_query(query)
    if not v_q:
        return jsonify({'results': [], 'total': 0, 'info': 'Nenhum termo relevante encontrado.'})

    norma_q = math.sqrt(sum(p ** 2 for p in v_q.values()))

    candidatos: set = set()
    for t in v_q:
        candidatos.update(idx.indice[t]['postings'].keys())

    ranking = []
    for doc_id in candidatos:
        sim = rec.calcular_similaridade(doc_id, v_q, norma_q)
        if sim > 0:
            ranking.append({'doc': doc_id, 'score': round(sim, 4)})

    ranking.sort(key=lambda x: x['score'], reverse=True)
    top = ranking[:10]

    query_terms = list(v_q.keys())
    for item in top:
        item['snippet'] = _get_snippet(dir_col, item['doc'], query_terms)

    return jsonify({
        'results':  top,
        'total':    len(ranking),
        'time_ms':  round((time.time() - t0) * 1000),
        'terms':    query_terms,
    })


@app.route('/api/reindex', methods=['POST'])
def reindex():
    body    = request.json or {}
    dir_col = body.get('collection_path', DEFAULT_DIR)
    path    = _db_path(dir_col)
    _cache.pop(path, None)
    indexador.executar(dir_col, path)
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)

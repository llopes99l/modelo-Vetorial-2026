import json
import math
import os

class IndiceInvertido:
    def __init__(self):
        self.total_docs = 0
        self.indice = {}      # {termo: {"df": N, "postings": {id: freq}}}
        self.docs_info = {}   # {id: {"max_tf": N, "norma": N, "termos": []}}
        
        # Atributos temporários para construção
        self._temp_termos = {} 
        self._temp_max_tf = {}

    def adicionar_documento(self, id_doc, tokens):
        if not tokens: 
            return
        id_doc = str(id_doc)
        self.total_docs += 1
        
        contagem = {}
        for t in tokens:
            contagem[t] = contagem.get(t, 0) + 1
            if t not in self.indice:
                self.indice[t] = {"df": 0, "postings": {}}
            self.indice[t]["postings"][id_doc] = contagem[t]
        
        self._temp_max_tf[id_doc] = max(contagem.values())
        self._temp_termos[id_doc] = list(contagem.keys())

    def salvar(self, caminho):
        # 1. Atualiza DF
        for t in self.indice:
            self.indice[t]["df"] = len(self.indice[t]["postings"])

        # 2. Consolida metadados (Coesão de Dados)
        for id_doc, tf_max in self._temp_max_tf.items():
            soma_quadrados = 0
            termos_doc = self._temp_termos[id_doc]
            
            for termo in termos_doc:
                tf = self.indice[termo]["postings"][id_doc]
                df = self.indice[termo]["df"]
                # IDF calculado uma única vez por termo
                idf = math.log10(self.total_docs / df)
                w = (tf / tf_max) * idf
                soma_quadrados += w ** 2
            
            self.docs_info[id_doc] = {
                "max_tf": tf_max,
                "norma": math.sqrt(soma_quadrados),
                "termos": termos_doc
            }

        dados_finais = {
            "total_docs": self.total_docs,
            "indice": self.indice,
            "docs_info": self.docs_info
        }

        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados_finais, f, ensure_ascii=False, indent=4)

    def carregar(self, caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            self.total_docs = dados["total_docs"]
            self.indice = dados["indice"]
            self.docs_info = dados["docs_info"]
            # Reconstrói temporários para manter coesão se precisar salvar novamente
            self._temp_max_tf = {id: info["max_tf"] for id, info in self.docs_info.items()}
            self._temp_termos = {id: info["termos"] for id, info in self.docs_info.items()}

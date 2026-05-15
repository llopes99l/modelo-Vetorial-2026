import json
import math
import os

class IndiceInvertido:
    def __init__(self):
        # Guarda a quantidade de documentos já adicionados ao índice.
        self.total_docs = 0

        # Estrutura principal do índice invertido:
        # para cada termo, guarda em quais documentos ele aparece e sua frequência.
        self.indice = {}      # {termo: {"df": N, "postings": {id: freq}}}

        # Metadados usados depois para calcular a similaridade do cosseno.
        self.docs_info = {}   # {id: {"max_tf": N, "norma": N, "termos": []}}
        
        # Atributos temporários para construção do índice antes de salvar.
        self._temp_termos = {} 
        self._temp_max_tf = {}

    def adicionar_documento(self, id_doc, tokens):
        # Ignora documentos vazios, pois eles não contribuem para o índice.
        if not tokens: 
            return

        # Usa string como identificador para manter compatibilidade com JSON.
        id_doc = str(id_doc)
        self.total_docs += 1
        
        # Conta quantas vezes cada termo aparece no documento atual.
        contagem = {}
        for t in tokens:
            contagem[t] = contagem.get(t, 0) + 1

            # Cria a entrada do termo no índice quando ele aparece pela primeira vez.
            if t not in self.indice:
                self.indice[t] = {"df": 0, "postings": {}}

            # Atualiza o posting do documento com a frequência atual do termo.
            self.indice[t]["postings"][id_doc] = contagem[t]
        
        # Guarda a maior frequência do documento e a lista de termos únicos.
        # Esses dados serão usados no cálculo dos pesos TF-IDF.
        self._temp_max_tf[id_doc] = max(contagem.values())
        self._temp_termos[id_doc] = list(contagem.keys())

    def salvar(self, caminho):
        # 1. Atualiza o DF (document frequency): total de documentos que possuem o termo.
        for t in self.indice:
            self.indice[t]["df"] = len(self.indice[t]["postings"])

        # 2. Consolida metadados do documento, incluindo sua norma vetorial.
        for id_doc, tf_max in self._temp_max_tf.items():
            soma_quadrados = 0
            termos_doc = self._temp_termos[id_doc]
            
            for termo in termos_doc:
                tf = self.indice[termo]["postings"][id_doc]
                df = self.indice[termo]["df"]

                # IDF diminui o peso de termos que aparecem em muitos documentos.
                idf = math.log10(self.total_docs / df)

                # Peso TF-IDF do termo no documento, normalizado pelo maior TF local.
                w = (tf / tf_max) * idf

                # A norma do documento é a raiz da soma dos pesos ao quadrado.
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

        # Cria a pasta de armazenamento se ela ainda não existir.
        os.makedirs(os.path.dirname(caminho), exist_ok=True)

        # Persiste o índice em JSON para poder carregar sem reprocessar os textos.
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados_finais, f, ensure_ascii=False, indent=4)

    def carregar(self, caminho):
        # Lê do JSON o índice, os postings e os metadados dos documentos.
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            self.total_docs = dados["total_docs"]
            self.indice = dados["indice"]
            self.docs_info = dados["docs_info"]

            # Reconstrói temporários para manter coesão se precisar salvar novamente
            self._temp_max_tf = {id: info["max_tf"] for id, info in self.docs_info.items()}
            self._temp_termos = {id: info["termos"] for id, info in self.docs_info.items()}

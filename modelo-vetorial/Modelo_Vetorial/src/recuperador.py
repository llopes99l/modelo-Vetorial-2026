import math

class RecuperadorVetorial:
    def __init__(self, indice, processador):
        self.indice = indice
        self.processador = processador

    def _calcular_peso_query(self, tf, tf_max, df):
        if tf <= 0 or tf_max == 0: 
            return 0
        w_tf = 0.5 + 0.5 * (tf / tf_max)
        w_idf = math.log10(self.indice.total_docs / df)
        return w_tf * w_idf

    def _calcular_peso_documento(self, tf, tf_max, df):
        if tf <= 0 or tf_max == 0:
            return 0
        w_tf = tf / tf_max
        w_idf = math.log10(self.indice.total_docs / df)
        return w_tf * w_idf

    def gerar_vetor_query(self, query):
        tokens = self.processador.limpar(query)
        if not tokens: 
            return {}
        
        freqs = {t: tokens.count(t) for t in set(tokens)}
        tf_max_q = max(freqs.values())
        
        v_q = {}
        for t, tf in freqs.items():
            if t in self.indice.indice:
                df = self.indice.indice[t]["df"]
                v_q[t] = self._calcular_peso_query(tf, tf_max_q, df)
        return v_q

    def calcular_similaridade(self, id_doc, v_q, norma_q):
        info_d = self.indice.docs_info.get(str(id_doc))
        # Validação de segurança: evita divisão por zero
        if not info_d or norma_q == 0 or info_d["norma"] == 0: 
            return 0

        norma_d = info_d["norma"]
        tf_max_d = info_d["max_tf"]
        produto_escalar = 0
        
        for termo, peso_q in v_q.items():
            postings = self.indice.indice[termo]["postings"]
            if id_doc in postings:
                tf_d = postings[id_doc]
                df = self.indice.indice[termo]["df"]
                peso_d = self._calcular_peso_documento(tf_d, tf_max_d, df)
                produto_escalar += peso_d * peso_q

        return produto_escalar / (norma_d * norma_q)

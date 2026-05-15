import math

class RecuperadorVetorial:
    def __init__(self, indice, processador):
        # Recebe o índice já montado e o processador usado para limpar consultas.
        self.indice = indice
        self.processador = processador

    def _calcular_peso_query(self, tf, tf_max, df):
        # Evita pesos inválidos quando o termo não aparece ou a consulta está vazia.
        if tf <= 0 or tf_max == 0: 
            return 0

        # Peso TF suavizado para consulta: evita que repetição excessiva domine tudo.
        w_tf = 0.5 + 0.5 * (tf / tf_max)

        # IDF valoriza termos mais raros na coleção.
        w_idf = math.log10(self.indice.total_docs / df)
        return w_tf * w_idf

    def _calcular_peso_documento(self, tf, tf_max, df):
        # Evita divisão por zero e pesos sem sentido.
        if tf <= 0 or tf_max == 0:
            return 0

        # Peso TF do documento normalizado pela maior frequência do próprio documento.
        w_tf = tf / tf_max

        # Mesmo IDF usado na consulta, pois ambos precisam estar no mesmo espaço vetorial.
        w_idf = math.log10(self.indice.total_docs / df)
        return w_tf * w_idf

    def gerar_vetor_query(self, query):
        # Limpa a consulta usando a mesma regra aplicada aos documentos.
        tokens = self.processador.limpar(query)
        if not tokens: 
            return {}
        
        # Conta a frequência de cada termo da consulta.
        freqs = {t: tokens.count(t) for t in set(tokens)}
        tf_max_q = max(freqs.values())
        
        v_q = {}
        for t, tf in freqs.items():
            # Só entram no vetor termos que existem no índice da coleção.
            if t in self.indice.indice:
                df = self.indice.indice[t]["df"]
                v_q[t] = self._calcular_peso_query(tf, tf_max_q, df)
        return v_q

    def calcular_similaridade(self, id_doc, v_q, norma_q):
        # Busca os metadados vetoriais do documento.
        info_d = self.indice.docs_info.get(str(id_doc))

        # Validação de segurança: evita divisão por zero
        if not info_d or norma_q == 0 or info_d["norma"] == 0: 
            return 0

        norma_d = info_d["norma"]
        tf_max_d = info_d["max_tf"]
        produto_escalar = 0
        
        for termo, peso_q in v_q.items():
            postings = self.indice.indice[termo]["postings"]

            # Só soma no produto quando o termo da consulta aparece no documento.
            if id_doc in postings:
                tf_d = postings[id_doc]
                df = self.indice.indice[termo]["df"]
                peso_d = self._calcular_peso_documento(tf_d, tf_max_d, df)
                produto_escalar += peso_d * peso_q

        # Similaridade do cosseno: produto escalar dividido pelas normas dos vetores.
        return produto_escalar / (norma_d * norma_q)

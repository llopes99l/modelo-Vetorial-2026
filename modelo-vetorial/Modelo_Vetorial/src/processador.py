import re
import unicodedata

class ProcessadorTexto:
    def __init__(self):
        # Stopwords sem acento (o texto é normalizado antes da filtragem)
        # Essas palavras são removidas porque aparecem muito e costumam carregar
        # pouca informação para a busca vetorial.
        self.stopwords = {
            # artigos
            'a', 'o', 'as', 'os', 'um', 'uma', 'uns', 'umas',
            # preposições e contrações
            'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas',
            'ao', 'aos', 'pelo', 'pela', 'pelos', 'pelas',
            'para', 'com', 'por', 'sem', 'sob', 'sobre', 'entre', 'ate', 'apos',
            # conjunções
            'e', 'ou', 'mas', 'porem', 'nem', 'que', 'se', 'como', 'quando',
            # pronomes
            'eu', 'tu', 'ele', 'ela', 'nos', 'vos', 'eles', 'elas',
            'me', 'te', 'se', 'lhe', 'lhes',
            'meu', 'minha', 'meus', 'minhas', 'seu', 'sua', 'seus', 'suas',
            'nosso', 'nossa', 'nossos', 'nossas',
            'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas',
            'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'isso', 'aquilo',
            # advérbios comuns
            'nao', 'sim', 'ja', 'so', 'ainda', 'tambem', 'mais', 'menos',
            'muito', 'pouco', 'bem', 'mal', 'sempre', 'nunca', 'aqui', 'la',
            # verbos auxiliares (formas normalizadas sem acento)
            'e', 'sao', 'era', 'eram', 'foi', 'foram', 'sera', 'serao',
            'esta', 'estao', 'estava', 'estavam',
            'tem', 'tem', 'tinha', 'tinham', 'vai', 'vao',
            'ha', 'havia',
        }

    def limpar(self, texto):
        # Retorna uma lista vazia quando não há conteúdo para processar.
        if not texto: 
            return []

        # Normalização Unicode e conversão para minúsculas
        # Primeiro separa letras e acentos (NFD), depois remove os acentos.
        texto = unicodedata.normalize('NFD', texto)
        texto = "".join(c for c in texto if unicodedata.category(c) != 'Mn').lower()

        # Captura apenas palavras alfanuméricas
        tokens = re.findall(r'[a-z0-9]+', texto)

        # Remove stopwords para manter somente termos mais úteis na indexação.
        return [t for t in tokens if t not in self.stopwords]

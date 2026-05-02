import re
import unicodedata

class ProcessadorTexto:
    def __init__(self):
        self.stopwords = {
            'a', 'o', 'as', 'os', 'de', 'do', 'da', 'em', 'um', 'uma', 
            'para', 'com', 'e', 'é', 'que', 'no', 'na', 'sao'
        }

    def limpar(self, texto):
        if not texto: 
            return []
        # Normalização Unicode e conversão para minúsculas
        texto = unicodedata.normalize('NFD', texto)
        texto = "".join(c for c in texto if unicodedata.category(c) != 'Mn').lower()
        # Captura apenas palavras alfanuméricas
        tokens = re.findall(r'[a-z0-9]+', texto)
        return [t for t in tokens if t not in self.stopwords]
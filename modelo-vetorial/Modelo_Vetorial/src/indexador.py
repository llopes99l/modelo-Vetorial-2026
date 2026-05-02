import os
from processador import ProcessadorTexto
from indice import IndiceInvertido

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_DOCS = os.path.join(BASE_DIR, "../data")
DB_PATH  = os.path.join(BASE_DIR, "../storage", "indice_db.json")

def executar():
    proc, idx = ProcessadorTexto(), IndiceInvertido()
    
    if not os.path.exists(DIR_DOCS):
        os.makedirs(DIR_DOCS)
        print(f"Pasta '{DIR_DOCS}' criada. Adicione arquivos .txt.")
        return

    print("🛠️  Indexando e calculando normas...")
    arquivos = [f for f in os.listdir(DIR_DOCS) if f.endswith(".txt")]
    
    for nome in arquivos:
        with open(os.path.join(DIR_DOCS, nome), 'r', encoding='utf-8') as f:
            idx.adicionar_documento(nome, proc.limpar(f.read()))
            print(f"✅ {nome}")
    
    idx.salvar(DB_PATH)
    print(f"\n✨ Banco de dados otimizado salvo em {DB_PATH}")

if __name__ == "__main__": 
    executar()
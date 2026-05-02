import os
from processador import ProcessadorTexto
from indice import IndiceInvertido

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def executar(dir_docs=None, db_path=None):
    if dir_docs is None:
        dir_docs = os.path.join(BASE_DIR, "../data")
    if db_path is None:
        nome_colecao = os.path.basename(os.path.normpath(dir_docs))
        db_path = os.path.join(BASE_DIR, "../storage", f"indice_{nome_colecao}.json")

    proc, idx = ProcessadorTexto(), IndiceInvertido()

    if not os.path.exists(dir_docs):
        os.makedirs(dir_docs)
        print(f"Pasta '{dir_docs}' criada. Adicione arquivos .txt.")
        return db_path

    arquivos = [f for f in os.listdir(dir_docs) if f.endswith(".txt")]
    if not arquivos:
        print(f"⚠️  Nenhum arquivo .txt encontrado em '{dir_docs}'.")
        return db_path

    print("🛠️  Indexando e calculando normas...")
    for nome in arquivos:
        with open(os.path.join(dir_docs, nome), 'r', encoding='utf-8') as f:
            idx.adicionar_documento(nome, proc.limpar(f.read()))
            print(f"✅ {nome}")

    idx.salvar(db_path)
    print(f"\n✨ Banco de dados salvo em {db_path}")
    return db_path

if __name__ == "__main__":
    executar()
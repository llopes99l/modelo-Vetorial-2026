import os
from processador import ProcessadorTexto
from indice import IndiceInvertido

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def executar(dir_docs=None, db_path=None):
    # Define a pasta padrão dos documentos quando nenhuma coleção é informada.
    if dir_docs is None:
        dir_docs = os.path.join(BASE_DIR, "../data")

    # Define o arquivo JSON onde o índice da coleção será salvo.
    if db_path is None:
        nome_colecao = os.path.basename(os.path.normpath(dir_docs))
        db_path = os.path.join(BASE_DIR, "../storage", f"indice_{nome_colecao}.json")

    # O processador limpa os textos; o índice recebe os tokens já tratados.
    proc, idx = ProcessadorTexto(), IndiceInvertido()

    # Se a pasta ainda não existe, cria a estrutura e encerra a indexação.
    if not os.path.exists(dir_docs):
        os.makedirs(dir_docs)
        print(f"Pasta '{dir_docs}' criada. Adicione arquivos .txt.")
        return db_path

    # Considera apenas arquivos .txt como documentos da coleção.
    arquivos = [f for f in os.listdir(dir_docs) if f.endswith(".txt")]
    if not arquivos:
        print(f"⚠️  Nenhum arquivo .txt encontrado em '{dir_docs}'.")
        return db_path

    print("🛠️  Indexando e calculando normas...")
    for nome in arquivos:
        # Lê cada documento, limpa o texto e adiciona seus termos ao índice.
        with open(os.path.join(dir_docs, nome), 'r', encoding='utf-8') as f:
            idx.adicionar_documento(nome, proc.limpar(f.read()))
            print(f"✅ {nome}")

    # Salva o índice completo para as buscas usarem depois.
    idx.salvar(db_path)
    print(f"\n✨ Banco de dados salvo em {db_path}")
    return db_path

if __name__ == "__main__":
    executar()

import os
import math
from processador import ProcessadorTexto
from indice import IndiceInvertido
from recuperador import RecuperadorVetorial
import indexador

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.path.join(BASE_DIR, "../data")
COLLECTIONS_DIR  = os.path.join(BASE_DIR, "../collections")

def _listar_colecoes():
    # Monta a lista de coleções disponíveis para o modo terminal.
    colecoes = []
    if os.path.isdir(DEFAULT_DATA_DIR):
        colecoes.append(("data (padrão)", DEFAULT_DATA_DIR))
    if os.path.isdir(COLLECTIONS_DIR):
        for item in sorted(os.listdir(COLLECTIONS_DIR)):
            full = os.path.join(COLLECTIONS_DIR, item)
            if os.path.isdir(full):
                colecoes.append((item, full))
    return colecoes

def _escolher_colecao():
    # Mostra um menu simples para escolher a coleção de documentos.
    colecoes = _listar_colecoes()

    print("\n📚 Coleções disponíveis:")
    for i, (nome, _) in enumerate(colecoes, 1):
        print(f"  {i}. {nome}")
    print("  0. Informar caminho manualmente")

    while True:
        escolha = input("\nEscolha a coleção [1]: ").strip()

        # Enter usa a primeira coleção encontrada, geralmente a pasta data.
        if not escolha and colecoes:
            return colecoes[0][1]

        # Opção 0 permite informar uma pasta fora da lista automática.
        if escolha == '0':
            caminho = input("Caminho da pasta com os .txt: ").strip()
            if os.path.isdir(caminho):
                return caminho
            print("❌ Caminho inválido.")
        elif escolha.isdigit() and 1 <= int(escolha) <= len(colecoes):
            # Converte a opção digitada para o caminho real da coleção.
            return colecoes[int(escolha) - 1][1]
        else:
            print(f"❌ Opção inválida. Escolha entre 0 e {len(colecoes)}.")

def iniciar_busca():
    # Seleciona a coleção e monta o caminho do índice correspondente.
    dir_colecao = _escolher_colecao()
    nome_colecao = os.path.basename(os.path.normpath(dir_colecao))
    db_path = os.path.join(BASE_DIR, "../storage", f"indice_{nome_colecao}.json")

    # Se ainda não existe índice salvo, cria um antes de iniciar a busca.
    if not os.path.exists(db_path):
        print(f"🔍 Índice não encontrado para '{nome_colecao}'. Indexando agora...")
        indexador.executar(dir_colecao, db_path)

    # Carrega o índice e prepara o recuperador vetorial.
    idx = IndiceInvertido()
    idx.carregar(db_path)
    rec = RecuperadorVetorial(idx, ProcessadorTexto())

    print(f"\n--- SISTEMA DE BUSCA ATIVO — coleção: {nome_colecao} (digite 'sair' para parar) ---")

    while True:
        query = input("\n🔍 O que deseja buscar? ").strip()
        if query.lower() in ['sair', '0', 'exit']:
            break
        if not query:
            continue

        # Transforma a consulta em vetor TF-IDF usando os termos do índice.
        v_q = rec.gerar_vetor_query(query)
        if not v_q:
            print("⚠️  Nenhum termo relevante encontrado.")
            continue

        # Calcula a norma do vetor da consulta, necessária para o cosseno.
        norma_q = math.sqrt(sum(p**2 for p in v_q.values()))

        # Candidatos são apenas documentos que possuem pelo menos um termo buscado.
        candidatos = set()
        for t in v_q.keys():
            candidatos.update(idx.indice[t]["postings"].keys())

        # Calcula similaridade documento a documento e mantém apenas resultados positivos.
        ranking = []
        for doc_id in candidatos:
            sim = rec.calcular_similaridade(doc_id, v_q, norma_q)
            if sim > 0:
                ranking.append((doc_id, sim))

        # Ordena os documentos do mais parecido para o menos parecido.
        ranking.sort(key=lambda x: x[1], reverse=True)

        print(f"\n--- Resultados ({len(ranking)}) ---")
        if not ranking:
            print("Nenhum documento encontrado.")
        for i, (doc, score) in enumerate(ranking[:10], 1):
            print(f"{i}º [{score:.4f}] - {doc}")

if __name__ == "__main__":
    iniciar_busca()

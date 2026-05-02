import os
import math
from processador import ProcessadorTexto
from indice import IndiceInvertido
from recuperador import RecuperadorVetorial
import indexador 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../storage", "indice_db.json")

def iniciar_busca():
    if not os.path.exists(DB_PATH):
        print("🔍 Banco não encontrado. Indexando agora...")
        indexador.executar()

    idx = IndiceInvertido()
    idx.carregar(DB_PATH)
    rec = RecuperadorVetorial(idx, ProcessadorTexto())

    print("\n--- SISTEMA DE BUSCA ATIVO (digite 'sair' para parar) ---")

    while True:
        query = input("\n🔍 O que deseja buscar? ").strip()
        if query.lower() in ['sair', '0', 'exit']: 
            break
        if not query: 
            continue

        v_q = rec.gerar_vetor_query(query)
        if not v_q:
            print("⚠️  Nenhum termo relevante encontrado.") 
            continue

        norma_q = math.sqrt(sum(p**2 for p in v_q.values()))
        
        # Encontrar documentos candidatos
        candidatos = set()
        for t in v_q.keys():
            candidatos.update(idx.indice[t]["postings"].keys())

        ranking = []
        for doc_id in candidatos:
            sim = rec.calcular_similaridade(doc_id, v_q, norma_q)
            if sim > 0: 
                ranking.append((doc_id, sim))

        ranking.sort(key=lambda x: x[1], reverse=True)

        print(f"\n--- Resultados ({len(ranking)}) ---")
        for i, (doc, score) in enumerate(ranking[:10], 1):
            print(f"{i}º [{score:.4f}] - {doc}")

if __name__ == "__main__": 
    iniciar_busca()
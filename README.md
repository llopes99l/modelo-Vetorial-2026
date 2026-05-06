# Documentação do Sistema de Busca Vetorial

Sistema de recuperação de informação baseado no **Modelo Vetorial**, utilizando **TF-IDF** e **Similaridade do Cosseno**. Disponível em duas interfaces: web (Flask) e linha de comando (CLI).

---

## 1. Arquitetura

```
Modelo_Vetorial/
├── api.py                  # Servidor web Flask (interface web)
├── templates/
│   └── index.html          # Frontend da interface web
├── src/
│   ├── processador.py      # Pré-processamento de texto
│   ├── indice.py           # TAD: Índice Invertido
│   ├── recuperador.py      # TAD: Modelo Vetorial e Similaridade
│   ├── indexador.py        # Pipeline de indexação
│   └── buscador.py         # Interface CLI de busca
├── data/                   # Coleção padrão de documentos (.txt)
├── collections/            # Coleções adicionais (cada subpasta é uma coleção)
└── storage/                # Índices gerados automaticamente (JSON)
```

---

## 2. Componentes (`src/`)

### `processador.py` — Pré-processamento
**Classe `ProcessadorTexto`**
- Remove acentos via normalização Unicode (NFD)
- Converte para minúsculas e extrai tokens alfanuméricos
- Filtra stopwords do português (artigos, preposições, conjunções, pronomes, verbos auxiliares)

### `indice.py` — TAD Índice Invertido
**Classe `IndiceInvertido`**

Estrutura interna:
```json
{
  "total_docs": 5,
  "indice": {
    "cavalo": { "df": 2, "postings": { "fazenda.txt": 3, "xadrez.txt": 1 } }
  },
  "docs_info": {
    "fazenda.txt": { "max_tf": 3, "norma": 0.847, "termos": ["cavalo", ...] }
  }
}
```

Métodos:
- `adicionar_documento(id_doc, tokens)` — contabiliza frequências brutas (TF) por documento
- `salvar(caminho)` — calcula DF, IDF, pesos TF-IDF e norma vetorial de cada doc; persiste em JSON
- `carregar(caminho)` — reconstrói o índice a partir do JSON

### `recuperador.py` — TAD Modelo Vetorial
**Classe `RecuperadorVetorial`**

Fórmula de peso aplicada aos documentos:

$$w_d = \frac{tf}{tf_{max}} \times \log_{10}\left(\frac{N}{df}\right)$$

Fórmula de peso aplicada às consultas:

$$w_q = \left(0.5 + 0.5 \times \frac{tf}{tf_{max}}\right) \times \log_{10}\left(\frac{N}{df}\right)$$

Métodos:
- `gerar_vetor_query(query)` — processa e vetoriza a consulta
- `calcular_similaridade(id_doc, v_q, norma_q)` — similaridade do cosseno usando norma pré-calculada

### `indexador.py` — Pipeline de Indexação
Função `executar(dir_docs, db_path)`:
- Lê todos os `.txt` da pasta indicada
- Processa cada documento via `ProcessadorTexto`
- Constrói e salva o `IndiceInvertido`
- Aceita caminhos parametrizados para suportar múltiplas coleções

### `buscador.py` — Interface CLI
- Lista coleções disponíveis e permite escolha interativa
- Indexa automaticamente se o índice não existir
- Loop de consultas com exibição do ranking (top 10 por score)

---

## 3. Interface Web (`api.py` + `templates/index.html`)

Servidor Flask com três endpoints:

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Serve o frontend |
| GET | `/api/collections` | Lista coleções disponíveis |
| POST | `/api/search` | Executa busca; retorna ranking com snippet e score |
| POST | `/api/reindex` | Força reindexação de uma coleção |
| POST | `/api/upload` | Insere um novo arquivo `.txt` na coleção selecionada e reindexa automaticamente |

O frontend exibe:
- Seletor de coleção
- Upload de novos arquivos `.txt`
- Campo de busca com resultado em tempo real
- Ranking com score, barra de relevância e trecho do documento com termos destacados

---

## 4. Fluxo de Dados

```
Arquivos .txt
     │
     ▼
ProcessadorTexto.limpar()       ← normalização + remoção de stopwords
     │
     ▼
IndiceInvertido.adicionar_documento()   ← contagem de TF
     │
     ▼
IndiceInvertido.salvar()        ← cálculo de DF, IDF, pesos e normas → JSON
     │
     ▼  (momento da consulta)
RecuperadorVetorial.gerar_vetor_query()     ← vetoriza a query
     │
     ▼
RecuperadorVetorial.calcular_similaridade() ← cosseno por candidato
     │
     ▼
Ranking ordenado por similaridade decrescente
```

---

## 5. Como Executar

### Interface Web (recomendado)

```bash
cd Modelo_Vetorial
python api.py
```

Acesse **http://localhost:5000** no navegador.  
O índice é gerado automaticamente na primeira busca.

### Interface CLI

```bash
cd Modelo_Vetorial/src
python buscador.py
```

---

## 6. Adicionando Coleções

Coloque arquivos `.txt` em:
- `data/` — coleção padrão
- `collections/<nome>/` — coleções adicionais (aparecem automaticamente no seletor)

Após adicionar ou alterar documentos manualmente, clique em **"Reindexar coleção"** na interface web.

Também é possível inserir novos `.txt` diretamente pela interface web usando o campo **"Novo arquivo .txt"**. O sistema salva o arquivo na coleção selecionada e reindexa automaticamente.

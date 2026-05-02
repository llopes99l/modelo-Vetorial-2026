# Documentação do Sistema de Busca Vetorial

Esta documentação descreve o sistema de recuperação de informação vetorial composto pelos scripts Python fornecidos. O sistema utiliza a técnica de **TF-IDF** (*Term Frequency-Inverse Document Frequency*) e a **Similaridade do Cosseno** para realizar buscas textuais otimizadas.

---

## 1. Visão Geral da Arquitetura

O sistema está dividido em componentes de lógica central (TADs) e scripts de execução (*pipelines*). A principal otimização implementada é o **pré-cálculo da norma dos documentos** durante a indexação, o que reduz drasticamente o custo computacional no momento da busca.

---

## 2. Componentes de Lógica Central (`src/`)

### `processador.py`
Responsável pelo tratamento inicial dos textos.
* **Classe `ProcessadorTexto`**:
    * **Atributo `stopwords`**: Conjunto de palavras irrelevantes (artigos, preposições) que são descartadas.
    * **Método `limpar(texto)`**: Realiza a normalização Unicode (remove acentos), converte para minúsculas e remove pontuação e *stopwords*, retornando uma lista de tokens válidos.

### `indice.py`
Gera a estrutura de dados do índice invertido e os metadados dos documentos.
* **Classe `IndiceInvertido`**:
    * **Atributos**: Mantém o índice invertido (termos e suas frequências por documento) e o dicionário `docs_info`.
    * **Método `adicionar_documento(id_doc, tokens)`**: Contabiliza as frequências brutas (TF) e identifica o termo mais frequente de cada documento.
    * **Método `salvar(caminho)`**: Calcula o IDF de cada termo e a **norma vetorial** de cada documento, consolidando tudo num arquivo JSON.
    * **Método `carregar(caminho)`**: Reconstrói o estado do índice a partir do arquivo JSON salvo.

### `recuperador.py`
Implementa o modelo vetorial para cálculo de relevância.
* **Classe `RecuperadorVetorial`**:
    * **Método `_calcular_peso(tf, tf_max, df)`**: Calcula o peso normalizado de um termo usando a fórmula: $w = (0.5 + 0.5 \times \frac{tf}{tf\_max}) \times \log_{10}(\frac{N}{df})$.
    * **Método `gerar_vetor_query(query)`**: Transforma a consulta do utilizador num vetor de pesos.
    * **Método `calcular_similaridade(id_doc, v_q, norma_q)`**: Calcula o cosseno entre o vetor da consulta e o vetor do documento, utilizando a norma pré-calculada para otimização.

---

## 3. Scripts de Execução (Pipelines)

### `indexador.py`
Estes scripts automatizam a criação do banco de dados de busca.
* Lêem todos os ficheiros `.txt` presentes na pasta `../data`.
* Utilizam o `ProcessadorTexto` para limpar o conteúdo e o `IndiceInvertido` para gerar as estatísticas.
* Gravam o resultado final em `../storage/indice_db.json`.

### `buscador.py`
Interface de interação com o utilizador.
* **Automatização**: Verifica se o índice existe; caso contrário, invoca o indexador automaticamente.
* **Loop de Busca**: Permite realizar múltiplas consultas sem reiniciar o programa.
* **Processamento**:
    1. Gera o vetor da consulta.
    2. Identifica documentos candidatos (que contêm pelo menos um termo da consulta).
    3. Calcula a similaridade e exibe um ranking dos 10 melhores resultados ordenados por *score*.

---

## 4. Fluxo de Dados

1. **Entrada**: Ficheiros de texto bruto (`.txt`).
2. **Indexação (Offline)**: O `indexador.py` processa os textos e gera o `indice_db.json` com normas e pesos pré-calculados.
3. **Consulta (Online)**: O utilizador insere uma frase no `buscador.py`.
4. **Recuperação**: O sistema compara o vetor da frase com os vetores dos documentos via similaridade do cosseno.
5. **Saída**: Ranking de documentos relevantes com os respetivos *scores*.

---

## 5. Execução

Coloque todos os documentos que você deseja indexar (em formato .txt) dentro da pasta data/.

Você pode iniciar o programa diretamente pelo buscador. O sistema foi projetado para ser inteligente: se ele não encontrar um índice pronto, ele chamará o indexador por conta própria.

No terminal, execute:

python buscador.py

## 6. Realizando Consultas

O programa abrirá um prompt perguntando: 🔍 O que deseja buscar?.

Digite sua frase ou palavra-chave e pressione Enter.

O sistema exibirá um ranking dos documentos mais relevantes com seus respectivos scores de similaridade.

Para encerrar o programa, digite sair, exit ou 0.

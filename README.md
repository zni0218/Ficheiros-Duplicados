
# SISTEMA MULTIMODAL DE DETEÇÃO DE FICHEIROS DUPLICADOS


Sistema automático para:
- deteção de duplicados exatos
- deteção de ficheiros semelhantes
- validação de ficheiros
- benchmarking de métodos

 Projeto desenvolvido no contexto do estágio ARMIS Group.


 # VISÃO GERAL


O sistema utiliza múltiplos métodos:

- SHA-256 → duplicados exatos
- SSDEEP / TLSH → fuzzy hashing
- fuzzy_chunks → comparação texto/documentos
- image_phash → imagens
- audio_phash → áudio
- video_phash → vídeo
- text_simhash → texto

Inclui ainda:
- pipeline otimizado (optimized)
- benchmark completo
- modo interativo em tempo real


# INSTALAÇÃO

1. Criar ambiente virtual:

python -m venv .venv

Windows:
.venv\Scripts\activate

Linux/macOS:
source .venv/bin/activate

-----------------------------------------------------------

2. Instalar dependências:

pip install -r requirements.txt

-----------------------------------------------------------

 SSDEEP (Windows)

Pode falhar instalação normal.

Usar:
pip install ssdeep-windows

Se não funcionar:
→ sistema continua sem esse método


# EXECUÇÃO: RUN_ALL (MODO COMPLETO)


Comando:

python -m core.run_all

ou:

python -m core.run_all --base data/original_files --out data/outputs/run_all

-----------------------------------------------------------


Pipeline completo:

VALIDATION → INDEX → DETECTION → RESULTADOS → PERFORMANCE

-----------------------------------------------------------

 1. VALIDATION

- remove ficheiros inválidos
- verifica corrupção
- valida MIME vs extensão

Output:
data/outputs/run_all/validation/

-----------------------------------------------------------

 2. INDEX

- gera fingerprints para todos os métodos
- cria:

data/outputs/run_all/dataset_index/combined_index.csv

-----------------------------------------------------------

 3. DETECTION

- compara todos os pares de ficheiros
- usa todos os métodos

-----------------------------------------------------------

 OUTPUTS (IMPORTANTE)

 data/outputs/run_all/results/

-----------------------------------------------------------

 CSV POR MÉTODO

Exemplo:
hashing_exato.csv
image_phash.csv
audio_phash.csv
tlsh.csv
ssdeep.csv

→ comparações de cada método individual

-----------------------------------------------------------

 CSV PRINCIPAL

ALL_combined.csv

Contém:
- file_a
- file_b
- method
- raw_score
- normalized_score
- is_exact_duplicate
- is_near_duplicate
- execution_time_ms


-----------------------------------------------------------

 OUTROS CSVs

ALL_exact.csv → apenas duplicados
ALL_near.csv → semelhantes
ALL_strong_near.csv → semelhantes fortes

-----------------------------------------------------------

 PERFORMANCE

performance_methods.csv

- tempo por método
- index + detection

performance_global.csv

- tempo total pipeline
- validation
- index
- detection
- nº ficheiros

-----------------------------------------------------------

 RESUMO RUN_ALL

- analisa dataset completo
- gera todos os CSVs
- permite benchmark
- execução mais pesada


# MODO INTERATIVO (interactive_compare.py)


Comando:

python -m core.interactive_compare

-----------------------------------------------------------

 OBJETIVO

Simular receção de ficheiros em tempo real.

-----------------------------------------------------------

 COMO USAR

Inserir ficheiros um a um:

file> caminho_do_ficheiro

Digite:
0 → sair

-----------------------------------------------------------

 FLUXO POR FICHEIRO

INPUT
 ↓
VALIDATION
 ↓
FAST CHECK (SHA-256)
 ↓
DEEP CHECK (se necessário)
 ↓
CLASSIFICAÇÃO
 ↓
ADICIONAR À SESSÃO

-----------------------------------------------------------

 FAST vs DEEP

FAST:
- hashing_exato
- deteta duplicados imediatos

DEEP:
- tlsh
- image_phash
- audio_phash
- video_phash
- text_simhash

-----------------------------------------------------------

 RESULTADO NO TERMINAL

[DUPLICATE] → duplicado exato
[STRONG] → muito semelhante
[SIMILAR] → semelhante
[INFO] sem matches → diferente

-----------------------------------------------------------

 OUTPUT

data/outputs/interactive/results/ALL_combined.csv

→ histórico da sessão

-----------------------------------------------------------

 COMPORTAMENTO IMPORTANTE

- o primeiro ficheiro cria o index
- sessão é incremental
- ficheiros são guardados automaticamente
- não repete ficheiros iguais

-----------------------------------------------------------

DIFERENÇA VS RUN_ALL

run_all:
- dataset fixo
- análise completa
- benchmarking

interactive:
- entrada manual
- incremental
- mais rápido
- simula produção real

# BENCHMARK


1. Criar ground truth:

python benchmark_cross_files.py

Output:
benchmark_cross_files.csv

-----------------------------------------------------------

2. Avaliar métodos:

python benchmark_methods.py

Output:
benchmark_methods_final.csv

-----------------------------------------------------------

 MÉTRICAS

duplicate_success_rate → duplicados detetados
similarity_success_rate → semelhantes detetados
total_execution_time_ms → tempo


# PIPELINE OTIMIZADO


Método: optimized

- escolhe métodos por tipo:
  imagem → image_phash
  áudio → audio_phash
  vídeo → video_phash
  texto → text_simhash

- combina scores

Resultado:
- muito mais rápido
- eficiente



# AUTOR


Zhixu Ni - Fcup
Projeto desenvolvido no contexto de estágio — ARMIS Group
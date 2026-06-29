SISTEMA MULTIMODAL DE DETEÇÃO DE FICHEIROS DUPLICADOS

Sistema automático para:
- deteção de duplicados exatos
- deteção de ficheiros semelhantes
- validação de ficheiros
- benchmarking de métodos

Projeto desenvolvido no contexto de estágio na ARMIS Group.


VISÃO GERAL

O sistema combina múltiplas técnicas:

- SHA-256 → duplicados exatos
- SSDEEP / TLSH → fuzzy hashing (dados binários)
- fuzzy_chunks → comparação de conteúdos
- image_phash → imagens
- audio_phash → áudio
- video_phash → vídeo
- text_simhash → texto

Inclui ainda:
- pipeline completo (run_all)
- pipeline otimizado (run_optimized)
- modo interativo em tempo real
- benchmarking automático


INSTALAÇÃO


1. Criar ambiente virtual:

python -m venv .venv

Windows:
.venv\Scripts\activate

Linux/macOS:
source .venv/bin/activate


--------------------------------------------------

2. Instalar dependências:

pip install -r requirements.txt


--------------------------------------------------

3. SSDEEP (Windows)

A instalação do ssdeep pode falhar no Windows.

Opção recomendada:

pip install ssdeep-windows

Alternativa (fork compatível 32/64 bits):

Repo:
https://github.com/Bw3ll/ssdeep-windows-32_64

Instalação:

git clone https://github.com/Bw3ll/ssdeep-windows-32_64
cd ssdeep-windows-32_64
python setup.py install

Se necessário:
pip install six

Nota:
- baseado em ssdeep (Jesse Kornblum)
- adaptado para Python no Windows

Se não funcionar, o sistema continua sem esse método.


EXECUÇÃO


1. run_all (pipeline completo)

python -m core.run_all

ou:

python -m core.run_all --base data/original_files --out data/outputs/run_all


Pipeline:

VALIDATION → INDEX → DETECTION → RESULTADOS → PERFORMANCE


Características:
- processa dataset completo
- executa todos os métodos
- gera todos os CSVs
- ideal para benchmark
- mais pesado


--------------------------------------------------

2. run_optimized (pipeline otimizado)

python -m core.run_optimized


Estratégia FAST → DEEP

FAST:
- SHA-256
- deteta duplicados imediatos

DEEP (se necessário):
- tlsh
- image_phash
- audio_phash
- video_phash
- text_simhash


Seleção por tipo:
- imagem → image_phash
- áudio → audio_phash
- vídeo → video_phash
- texto → text_simhash


Vantagens:
- mais rápido
- evita processamento redundante
- mantém precisão


--------------------------------------------------

3. Modo interativo

python -m core.interactive_compare


Fluxo:

INPUT
→ VALIDATION
→ FAST (SHA-256)
→ DEEP (se necessário)
→ RESULTADO
→ UPDATE INDEX


Resultado:

[DUPLICATE] → duplicado exato
[STRONG] → semelhante forte
[SIMILAR] → semelhante
[INFO] → sem correspondência


Características:
- incremental
- mantém sessão
- não repete ficheiros
- simula ambiente real


OUTPUTS


Resultados:

data/outputs/.../results/


CSV principal:

ALL_combined.csv

Contém:
- file_a, file_b
- method
- raw_score
- normalized_score
- classificação
- execution_time


Outros:
- ALL_exact.csv
- ALL_near.csv
- ALL_strong_near.csv


--------------------------------------------------

PERFORMANCE

performance_methods.csv
- index_time
- detection_time
- total_time

performance_global.csv
- total_pipeline_time
- validation
- index
- detection
- nº ficheiros


BENCHMARK


1. Criar ground truth:

python benchmark_cross_files.py


2. Avaliar métodos:

python benchmark_methods.py


Métricas:
- duplicate_success_rate
- similarity_success_rate
- total_time



DIFERENÇA ENTRE MODOS


run_all:
- completo
- pesado
- benchmarking

run_optimized:
- rápido
- eficiente

interactive:
- incremental
- tempo real


AUTOR


Zhixu Ni
FCUP — Licenciatura em Inteligência Artificial e Ciência de Dados
Estágio — ARMIS Group
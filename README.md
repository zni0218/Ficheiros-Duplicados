<<<<<<< HEAD
# 📦 Sistema de Deteção de Ficheiros Duplicados e Inconsistências  
### Pack completo de scripts — Versão Final

Este pack contém um conjunto completo de scripts Python para analisar ficheiros enviados por clientes, detetar duplicados, quase duplicados, inconsistências e validar conteúdos multimédia (vídeo, áudio, documentos, texto, imagens).

Foi criado para suportar o projeto:
**“Sistema Automático de Deteção de Ficheiros Duplicados e Inconsistentes na Receção de Ficheiros de Clientes — ARMIS Group”**

---

## 🧩 Funcionalidades incluídas

### 🔍 1. Duplicados exatos
- Hashing com **SHA‑256**
- Deteta ficheiros binariamente iguais
- CSV: `duplicados_exatos.csv`

### 🔍 2. Quase duplicados (Fuzzy via chunk hashing)
- Método compatível com Windows  
- Compara ficheiros por sequência de hashes dos blocos  
- CSV: `quase_duplicados_fuzzy.csv`

### 🖼️ 3. Similaridade perceptual de imagens
- `imagehash` (pHash)
- Deteta imagens iguais ou parecidas
- CSV: `imagens_perceptual.csv`

### 📄 4. Similaridade de ficheiros de texto
- SimHash  
- Suporta JSON, CSV, XML, LOG, TXT
- CSV: `texto_simhash.csv`

### 🔧 5. Validação geral
- Valida PDFs (corrupção)
- Valida ZIPs
- Verifica incoerências MIME vs extensão
- CSV: `inconsistencias.csv`

### 🎥 6. Hashing de vídeo
- SHA‑256 para duplicados exatos  
- Chunk hashing fuzzy para vídeos parecidos  
- CSV: `video_duplicados_exatos.csv`, `video_quase_duplicados.csv`

### 🎞️ 7. Similaridade visual entre vídeos (pHash de keyframes)
- Extração automática de keyframes
- Hash perceptual para cada frame
- CSV: `video_phash.csv`

### 🎧 8. Hashing de áudio
- SHA‑256 e chunk hashing (fuzzy)
- CSV: `audio_duplicados_exatos.csv`, `audio_quase_duplicados.csv`

### 🔊 9. Similaridade perceptual de áudio (espectrograma Mel)
- Converte áudio → espectrograma → imagem → pHash
- CSV: `audio_phash.csv`

### 🛠️ 10. Validação multimédia completa
- Verifica:
  - corrupção de vídeos  
  - corrupção de áudio  
  - duração  
  - FPS  
  - resoluções  
  - sample rate  
  - mime real vs extensão  
- CSV: `validacao_multimedia.csv`

---

## ▶️ Execução completa

Para correr todos os módulos automaticamente:

```bash
python run_all.py --base ../teste_ficheiros --out ./resultados
```

Isto irá gerar:

- todos os CSVs
- um relatório final em:  
  **`resultados/relatorio_final.md`**

---

## 📁 Estrutura da pasta

```
scripts_teste/
  README.md
  requirements.txt
  run_all.py
  utils/
    file_utils.py
  test_hashing_exato.py
  test_fuzzy_chunks.py
  test_image_perceptual.py
  test_simhash_textual.py
  test_validacao.py
  test_video_hashing.py
  test_video_phash.py
  test_audio_hashing.py
  test_audio_phash.py
  test_video_audio_validacao.py
```

---

## 🧪 Como instalar dependências

Criar ambiente virtual (opcional mas recomendado):

```bash
python -m venv .venv
```

Ativar:

**Windows**
```bash
.venv\Scripts\activate
```

**Linux/macOS**
```bash
source .venv/bin/activate
```

Instalar dependências:

```bash
pip install -r requirements.txt
```

---

## ⚠️ Notas importantes

- `librosa` exige `numpy` instalado.  
- No Windows, `python-magic` pode não funcionar — mas o sistema trabalha com fallback automático.  
- `opencv-python` é necessário para vídeo.  
- `imagehash` + `PIL` precisam de `pillow`.  

Todos estes já estão incluídos em `requirements.txt`.

---
=======
# Ficheiros-Duplicados
Sistema Automático de Deteção de Ficheiros Duplicados e Inconsistentes na Receção de Ficheiros de Clientes
>>>>>>> 5a564043640c361e41f373164530e94d9bb8e29e

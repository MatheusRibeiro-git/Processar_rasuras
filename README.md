# Audit & Redaction Tools for DANFE (PDF)

Conjunto de scripts em Python desenvolvidos para automatizar a verificação de conformidade de anonimização e auditoria de rasuras em Documentos Auxiliares da Nota Fiscal Eletrônica (DANFE) no formato PDF[cite: 1, 2].

## 📑 Descrição dos Projetos

### 1. Verificador de Conformidade (`processar_rasuras.py`)
Focado na **validação de privacidade e conformidade** (ex.: LGPD).
- **Extração Recursiva:** Identifica e descompacta ficheiros `.zip` aninhados automaticamente[cite: 1].
- **Validação de Coordenadas:** Analisa regiões específicas da DANFE (Chave de Acesso, CNPJ, Razão Social, Valores, etc.)[cite: 1].
- **Relatório no Terminal:** Assinala quais documentos não cumprem os requisitos de rasura/ocultação[cite: 1].

### 2. Auditor e Extrator de Rasuras (`descompacta.py`)
Focado na **segurança da informação e auditoria**.
- **Detecção de Tarjas Inefetivas:** Identifica se as rasuras aplicadas são apenas elementos visuais cobrindo a camada de texto original[cite: 2].
- **Mapeamento de Conteúdo:** Mapeia os campos da DANFE (Rótulo vs. Valor)[cite: 2].
- **Relatório em Excel:** Gera um ficheiro `.xlsx` detalhado com o estado dos documentos e os valores recuperados sob as rasuras[cite: 2].

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **PyMuPDF (`fitz`)** — Manipulação e extração de texto/vetores de PDFs[cite: 1, 2]
- **Pandas** — Geração de relatórios em Excel[cite: 2]

## 🚀 Como Executar

1. Instale as dependências necessárias:
```bash
pip install pymupdf pandas openpyxl

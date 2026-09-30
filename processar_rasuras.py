"""
processar_rasuras.py

Versão simplificada:
1. extrair_zips_recursivo()  -> extrai todos os .zip encontrados em pastas/subpastas
2. listar_pdfs_recursivo()   -> lista o caminho de todos os .pdf encontrados em pastas/subpastas
3. loop final chamando is_pdf_redacted() para cada PDF encontrado
"""

import fitz  # PyMuPDF
import zipfile
import os
import sys
from pathlib import Path
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Configuração das áreas de rasura 
# ---------------------------------------------------------------------------
def get_redaction_areas() -> List[Tuple[float, float, float, float]]:
    """Coordenadas dos campos que devem estar rasurados (x0, y0, x1, y1)"""
    return [
        (358, 120, 560, 129),  # Chave de acesso
        (13, 248, 350, 259),   # Razão social
        (370, 252, 480, 263),  # CNPJ
        (13, 276, 280, 287),   # Endereço
        (304, 273, 410, 283),  # Bairro
        (424, 273, 480, 283),  # CEP
        (13, 296, 180, 307),   # Município
        (322, 297, 350, 308),  # UF
        (358, 297, 480, 307),  # Inscrição Estadual (IE)
        (280, 520, 309, 528),  # Quantidade
        (320, 520, 357, 528),  # Valor unitário
    ]


def is_pdf_redacted(pdf_path: str, tolerance: int = 5) -> bool:
    """
    Verifica se o PDF está corretamente rasurado.
    Retorna True se TODAS as áreas sensíveis estiverem sem texto legível.
    """
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        areas = get_redaction_areas()
        for x0, y0, x1, y1 in areas:
            rect = fitz.Rect(x0, y0, x1, y1)
            text = page.get_text('text', clip=rect).strip()
            if len(text) > tolerance:  # tolerância para espaços ou artefatos
                doc.close()
                return False
        doc.close()
        return True
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {e}")
        return False


# ---------------------------------------------------------------------------
# Função 1: extrair todos os ZIPs de uma pasta (incluindo subpastas)
# ---------------------------------------------------------------------------
def extrair_zips_recursivo(pasta_raiz: str) -> None:
    """
    Percorre pasta_raiz e todas as subpastas procurando arquivos .zip.
    Cada zip é extraído para uma subpasta com o mesmo nome do zip,
    no mesmo diretório onde o zip está.
    Repete o processo para tratar zips que estejam dentro de outros zips.
    """
    while True:
        zips_encontrados = []
        for dirpath, _, filenames in os.walk(pasta_raiz):
            for fname in filenames:
                if fname.lower().endswith(".zip"):
                    zips_encontrados.append(os.path.join(dirpath, fname))

        if not zips_encontrados:
            break  # não há mais zips para extrair

        for zip_path in zips_encontrados:
            destino = os.path.join(os.path.dirname(zip_path), Path(zip_path).stem)
            os.makedirs(destino, exist_ok=True)
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(destino)
                print(f"Extraído: {zip_path} -> {destino}")
            except zipfile.BadZipFile:
                print(f"[AVISO] ZIP inválido/corrompido, ignorado: {zip_path}")
            finally:
                os.remove(zip_path)  # remove o zip já extraído para não reprocessar


# ---------------------------------------------------------------------------
# Função 2: listar todos os PDFs de uma pasta (incluindo subpastas)
# ---------------------------------------------------------------------------
def listar_pdfs_recursivo(pasta_raiz: str) -> List[str]:
    """Retorna uma lista com o caminho completo de todos os .pdf encontrados em pasta_raiz e subpastas."""
    pdfs = []
    for dirpath, _, filenames in os.walk(pasta_raiz):
        for fname in filenames:
            if fname.lower().endswith(".pdf"):
                pdfs.append(os.path.join(dirpath, fname))
    return pdfs


# ---------------------------------------------------------------------------
# Execução principal
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    pasta_raiz = sys.argv[1] if len(sys.argv) > 1 else r"C:\Desenvolvimentos\processar_rasuras\NF Arinos"

    # 1. extrai todos os zips (inclusive zips dentro de zips)
    extrair_zips_recursivo(pasta_raiz)

    # 2. lista todos os pdfs encontrados
    pdfs = listar_pdfs_recursivo(pasta_raiz)
    print(f"\nTotal de PDFs encontrados: {len(pdfs)}\n")

    # 3. loop verificando rasura de cada pdf
    nao_rasurados = []
    for pdf_path in pdfs:
        rasurado = is_pdf_redacted(pdf_path)
        status = "OK (rasurado)" if rasurado else "FALHOU (NÃO rasurado)"
        print(f"{status} - {pdf_path}")
        if not rasurado:
            nao_rasurados.append(pdf_path)

    print("\n" + "=" * 60)
    if nao_rasurados:
        print(f"ATENÇÃO: {len(nao_rasurados)} PDF(s) NÃO estão rasurados:")
        for p in nao_rasurados:
            print(f"  - {p}")
    else:
        print("Todos os PDFs estão rasurados corretamente.")
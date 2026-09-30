"""
Script DANFE - Detecção e Burla de Rasuras
Mostra claramente os valores recuperados sob as tarjas pretas.
"""

import os
import zipfile
import fitz  # PyMuPDF
import pandas as pd
from datetime import datetime
import re

# ==================== RÓTULOS ====================
# Lista de termos que identificam os campos/rótulos da DANFE
TERMOS_ROTULO = [
    "RECEBEMOS DE", "DATA DE RECEBIMENTO", "IDENTIFICAÇÃO E ASSINATURA DO RECEBEDOR",
    "NATUREZA DA OPERAÇÃO", "INSCRIÇÃO ESTADUAL DO SUBST. TRIBUT.",
    "INSCR. ESTADUAL DO SUBST. TRIBUT.", "INSCRIÇÃO ESTADUAL", "CNPJ/CPF", "CNPJ",
    "DESTINATÁRIO/REMETENTE", "NOME/RAZÃO SOCIAL", "DATA DA EMISSÃO",
    "ENDEREÇO", "BAIRRO/DISTRITO", "CEP", "DATA DA ENTRADA/SAÍDA",
    "MUNICIPIO", "MUNICÍPIO", "FONE/FAX", "UF", "HORA DA SAÍDA",
    "FATURA/DUPLICATA", "FATURA", "PEDIDO CLIENTE",
    "CÁLCULO DO IMPOSTO", "BASE DE CÁLCULO DO ICMS", "VALOR DO ICMS",
    "BASE DE CÁLCULO DO ICMS ST", "VALOR DO ICMS ST", "VALOR TOTAL DOS PRODUTOS",
    "VALOR DO FRETE", "VALOR DO SEGURO", "DESCONTO", "OUTRAS DESPESAS ACESSÓRIAS",
    "VALOR TOTAL DO IPI", "VALOR TOTAL DA NOTA",
    "TRANSPORTADOR/VOLUMES TRANSPORTADOS", "FRETE POR CONTA", "CÓDIGO ANTT",
    "PLACA DO VEÍCULO", "QUANTIDADE", "ESPÉCIE", "MARCA", "NUMERAÇÃO",
    "PESO BRUTO", "PESO LÍQUIDO", "PROTOCOLO DE AUTORIZAÇÃO DE USO",
    "CHAVE DE ACESSO", "DADOS ADICIONAIS", "INFORMAÇÕES COMPLEMENTARES",
    "RESERVADO AO FISCO",
]
# Ordena do maior para o menor para priorizar termos mais longos na busca
TERMOS_ROTULO.sort(key=len, reverse=True)


def extrair_linhas(pagina):
    """
    Extrai todas as linhas de texto de uma página do PDF,
    retornando uma lista de tuplas (x0, y0, x1, y1, texto).
    """
    linhas = []
    dados = pagina.get_text("dict")
    for bloco in dados.get("blocks", []):
        for linha in bloco.get("lines", []):
            texto = "".join(s.get("text", "") for s in linha.get("spans", [])).strip()
            if texto:
                x0, y0, x1, y1 = linha["bbox"]
                linhas.append((x0, y0, x1, y1, texto))
    # Ordena as linhas de cima para baixo e da esquerda para a direita
    linhas.sort(key=lambda l: (round(l[1], 1), l[0]))
    return linhas


def ler_danfe(caminho_arquivo):
    """
    Lê o conteúdo de uma DANFE e tenta associar cada rótulo
    ao valor correspondente logo abaixo.
    Retorna uma lista de páginas, cada uma contendo pares (rótulo, valor).
    """
    try:
        doc = fitz.open(caminho_arquivo)
        resultado = []
        for p in range(doc.page_count):
            pagina = doc.load_page(p)
            linhas = extrair_linhas(pagina)
            pagina_resultado = []
            for i, (_, _, _, _, texto) in enumerate(linhas):
                # Verifica se a linha atual é um rótulo conhecido
                if any(t.upper() in texto.upper() or texto.upper().strip().rstrip(":").strip() in t.upper() for t in TERMOS_ROTULO):
                    valor = None
                    # Procura o valor na próxima linha abaixo (com tolerância de posição)
                    for j in range(i+1, len(linhas)):
                        if linhas[j][1] > linhas[i][3] + 5 and abs(linhas[j][0] - linhas[i][0]) < 250:
                            valor = linhas[j][4]
                            break
                    pagina_resultado.append((texto.rstrip(":"), valor or "(não encontrado)"))
            resultado.append(pagina_resultado)
        doc.close()
        return resultado
    except:
        return []

if __name__ == "__main__":
    folder_path = r"...\PROCESSAR_RASURAS\NF Arindos"  # <<< ALTERE AQUI
    
    print("🚀 Iniciando análise de rasuras em DANFEs...\n")
    results = []
    
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            
            # Trata arquivos ZIP: extrai e processa os PDFs de dentro
            if filename.lower().endswith('.zip'):
                extract_dir = os.path.join(dirpath, f"extracted_{filename[:-4]}")
                os.makedirs(extract_dir, exist_ok=True)
                try:
                    with zipfile.ZipFile(full_path, 'r') as z:
                        z.extractall(extract_dir)
                    print(f"ZIP extraído: {filename}")
                except:
                    continue
                # Processa PDFs extraídos
                for dp, _, fs in os.walk(extract_dir):
                    for f in fs:
                        if f.lower().endswith('.pdf'):
                            full_path = os.path.join(dp, f)
                            # continua abaixo...
            
            # Processa arquivos PDF
            if filename.lower().endswith('.pdf'):
                print(f"\n📄 Processando: {filename}")
                try:
                    doc = fitz.open(full_path)
                    pagina = doc[0]
                    
                    # Chama a função de burla de rasura (deve estar definida em outro lugar)
                    num_rasuras, textos_sob, full = burlar_rasura(pagina)
                    danfe_data = ler_danfe(full_path)
                    
                    # Define o status com base na existência de rasuras e textos recuperados
                    status = "⚠️ RASURA BURLADA" if num_rasuras > 0 and textos_sob else "✅ Rasura efetiva"
                    
                    print(f"   → Status: {status}")
                    print(f"   → Rasuras encontradas: {num_rasuras}")
                    
                    if textos_sob:
                        print("   🔓 VALORES RECUPERADOS SOB RASURA:")
                        for t in textos_sob[:20]:  # mostra os primeiros 20
                            if len(t.strip()) > 2:
                                print(f"      • {t}")
                    
                    print("   --- Dados DANFE ---")
                    if danfe_data:
                        for campos in danfe_data:
                            for rotulo, valor in campos:
                                if valor and valor != "(não encontrado)":
                                    print(f"      {rotulo}: {valor}")
                    
                    # Monta a linha para o relatório Excel
                    row = {
                        "Arquivo": filename,
                        "Status": status,
                        "Qtd_Rasuras": num_rasuras,
                        "Valores_Recuperados": " | ".join(textos_sob[:30]) if textos_sob else "",
                    }
                    results.append(row)
                    doc.close()
                except Exception as e:
                    print(f"   Erro: {e}")
    
    # Gera o relatório Excel com os resultados
    if results:
        df = pd.DataFrame(results)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        excel_path = f"relatorio_rasura_{ts}.xlsx"
        df.to_excel(excel_path, index=False)
        print(f"\n✅ Relatório Excel gerado: {excel_path}")
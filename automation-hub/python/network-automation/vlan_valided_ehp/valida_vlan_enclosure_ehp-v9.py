from pathlib import Path
import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog, messagebox


COLUNAS_FIXAS = {"VLAN", "Encontrado", "NAGs", "Network"}


def selecionar_arquivos_e_saida():
    """Solicita os arquivos de VLANs, comparação, termos de Profiles e diretório de saída."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    arquivo_base = filedialog.askopenfilename(
        title="Selecione o arquivo base com a lista de VLANs",
        filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
    )
    if not arquivo_base:
        root.destroy()
        raise SystemExit("Operação cancelada: arquivo base não selecionado.")

    arquivo_comparacao = filedialog.askopenfilename(
        title="Selecione o arquivo de comparação (configuração completa)",
        filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
    )
    if not arquivo_comparacao:
        root.destroy()
        raise SystemExit("Operação cancelada: arquivo de comparação não selecionado.")

    arquivo_profiles = filedialog.askopenfilename(
        title="Selecione o arquivo com os nomes/termos de Profiles a pesquisar",
        filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
    )
    if not arquivo_profiles:
        root.destroy()
        raise SystemExit("Operação cancelada: arquivo de Profiles não selecionado.")

    diretorio_saida = filedialog.askdirectory(title="Selecione o diretório de saída")
    if not diretorio_saida:
        root.destroy()
        raise SystemExit("Operação cancelada: diretório de saída não selecionado.")

    root.destroy()
    return Path(arquivo_base), Path(arquivo_comparacao), Path(arquivo_profiles), Path(diretorio_saida)


def limpar_valor(valor):
    if valor is None:
        return ""
    return valor.strip().strip('"\'')


def extrair_campo(linha, nome_campo):
    """Extrai CAMPO=valor, aceitando valor sem aspas, entre aspas simples ou duplas."""
    padrao = rf"\b{re.escape(nome_campo)}\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s]+))"
    match = re.search(padrao, linha, re.IGNORECASE)
    if not match:
        return ""
    return next((limpar_valor(g) for g in match.groups() if g is not None), "")


def expandir_vlans(valor):
    """Expande listas/ranges como 1001-1005,1006,1007 em VLANs individuais."""
    vlans = []
    for parte in re.split(r"[,;|\s]+", valor.strip()):
        if not parte:
            continue
        intervalo = re.fullmatch(r"(\d+)\s*-\s*(\d+)", parte)
        if intervalo:
            inicio = int(intervalo.group(1))
            fim = int(intervalo.group(2))
            passo = 1 if fim >= inicio else -1
            vlans.extend(str(v) for v in range(inicio, fim + passo, passo))
        elif parte.isdigit():
            vlans.append(parte)
    return vlans


def extrair_vlans_da_linha(linha):
    """Extrai VLanID/VLanIDs/VLanID(s), inclusive ranges."""
    match = re.search(
        r"\bVLanID(?:s|\(s\))?\s*=\s*([0-9][0-9\s,;|\-]*)",
        linha,
        re.IGNORECASE,
    )
    return expandir_vlans(match.group(1)) if match else []


def processar_linha_network(linha):
    """Retorna (vlans, NAGs, Network, tipo) para add network/add network-range."""
    linha_limpa = linha.strip()

    if re.match(r"^add\s+network-range\b", linha_limpa, re.IGNORECASE):
        network = extrair_campo(linha_limpa, "nameprefix")
        nags = extrair_campo(linha_limpa, "NAGs")
        vlans = extrair_vlans_da_linha(linha_limpa)
        return vlans, nags, network, "network-range"

    if re.match(r"^add\s+network\b", linha_limpa, re.IGNORECASE):
        match_network = re.match(
            r"^add\s+network\s+(?:\"([^\"]+)\"|'([^']+)'|([^\s]+))",
            linha_limpa,
            re.IGNORECASE,
        )
        network = ""
        if match_network:
            network = next((limpar_valor(g) for g in match_network.groups() if g is not None), "")
        nags = extrair_campo(linha_limpa, "NAGs")
        vlans = extrair_vlans_da_linha(linha_limpa)
        return vlans, nags, network, "network"

    return None


def ler_termos_profiles(arquivo_profiles):
    """Lê uma lista de termos de busca de Profile, um por linha."""
    termos = [
        linha.strip()
        for linha in arquivo_profiles.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        if linha.strip()
    ]
    return list(dict.fromkeys(termos))


def identificar_profiles(linhas_comparacao, termos_busca):
    """
    Localiza profiles no arquivo de comparação.

    Cada linha do arquivo de Profiles é tratada como termo de busca (*termo*),
    sem diferenciar maiúsculas/minúsculas. Ex.: esxi0001 encontra PROD-ESXi0001.

    Retorna:
      - profiles: {nome_profile_completo: set(vlans)}
      - termos_sem_match: termos que não localizaram nenhum 'add profile'.
    """
    nomes_profiles_config = []

    for linha in linhas_comparacao:
        match = re.match(
            r"^\s*add\s+profile\s+(?:\"([^\"]+)\"|'([^']+)'|([^\s]+))",
            linha,
            re.IGNORECASE,
        )
        if match:
            nome = next((limpar_valor(g) for g in match.groups() if g is not None), "")
            if nome and nome not in nomes_profiles_config:
                nomes_profiles_config.append(nome)

    profiles = {}
    termos_sem_match = []

    for termo in termos_busca:
        encontrados = [p for p in nomes_profiles_config if termo.casefold() in p.casefold()]
        if not encontrados:
            termos_sem_match.append(termo)
            continue
        for profile in encontrados:
            profiles.setdefault(profile, set())

    return profiles, termos_sem_match


def mapear_network_para_vlans(vlans_info):
    """Cria mapa auxiliar Network exata -> VLAN(s) para linhas server-port-map."""
    mapa = {}
    for vlan, info in vlans_info.items():
        nome = info.get("Network", "")
        tipo = info.get("Tipo", "")
        if not nome:
            continue

        if tipo == "network":
            mapa.setdefault(nome.casefold(), set()).add(vlan)
        elif tipo == "network-range":
            # No VC, o nome efetivo da network gerada pelo range é normalmente nameprefix + VLAN.
            nome_efetivo = f"{nome}{vlan}"
            mapa.setdefault(nome_efetivo.casefold(), set()).add(vlan)

    return mapa


def coletar_vlans_dos_profiles(linhas_comparacao, profiles, network_para_vlans):
    """
    Preenche as VLANs de cada profile diretamente do arquivo de comparação.

    Formatos principais suportados:
      add server-port-map-range PROFILE:porta ... vlanids=...
      add server-port-map PROFILE:porta NOME_DA_NETWORK ...
    """
    if not profiles:
        return profiles

    profiles_casefold = {nome.casefold(): nome for nome in profiles}

    for linha in linhas_comparacao:
        linha_limpa = linha.strip()

        # Ex.: add server-port-map-range PROD-ESXi0001:3 UplinkSet=... vlanids=...
        match_range = re.match(
            r"^add\s+server-port-map-range\s+(?:\"([^\"]+)\"|'([^']+)'|([^\s]+))",
            linha_limpa,
            re.IGNORECASE,
        )
        if match_range:
            alvo = next((limpar_valor(g) for g in match_range.groups() if g is not None), "")
            nome_profile_linha = alvo.split(":", 1)[0]
            profile_real = profiles_casefold.get(nome_profile_linha.casefold())
            if profile_real:
                profiles[profile_real].update(extrair_vlans_da_linha(linha_limpa))
            continue

        # Ex.: add server-port-map PROD-ESXi0001:7 VC5-DOM-DMZ-VMOTION-2691 ...
        match_map = re.match(
            r"^add\s+server-port-map\s+"
            r"(?:\"([^\"]+)\"|'([^']+)'|([^\s]+))\s+"
            r"(?:\"([^\"]+)\"|'([^']+)'|([^\s]+))",
            linha_limpa,
            re.IGNORECASE,
        )
        if match_map:
            grupos = match_map.groups()
            alvo = next((limpar_valor(g) for g in grupos[:3] if g is not None), "")
            network = next((limpar_valor(g) for g in grupos[3:] if g is not None), "")
            nome_profile_linha = alvo.split(":", 1)[0]
            profile_real = profiles_casefold.get(nome_profile_linha.casefold())
            if profile_real and network:
                profiles[profile_real].update(network_para_vlans.get(network.casefold(), set()))

    return profiles


def main():
    arquivo_base, arquivo_comparacao, arquivo_profiles, diretorio_saida = selecionar_arquivos_e_saida()
    arquivo_saida = diretorio_saida / "resultado_comparacao_profiles.xlsx"

    vlans_base = [
        linha.strip()
        for linha in arquivo_base.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        if linha.strip()
    ]
    vlans_base = list(dict.fromkeys(vlans_base))

    linhas_comparacao = arquivo_comparacao.read_text(
        encoding="utf-8-sig", errors="replace"
    ).splitlines()

    # 1) VLAN -> NAGs / Network.
    vlans_info = {}
    for linha in linhas_comparacao:
        dados = processar_linha_network(linha)
        if dados is None:
            continue
        vlans, nags, network, tipo = dados
        for vlan in vlans:
            vlans_info[vlan] = {"NAGs": nags, "Network": network, "Tipo": tipo}

    # 2) Arquivo de Profiles = lista de termos a localizar no MESMO arquivo de comparação.
    termos_profiles = ler_termos_profiles(arquivo_profiles)
    profiles, termos_sem_match = identificar_profiles(linhas_comparacao, termos_profiles)

    # 3) Coleta VLANs dos profiles nas linhas server-port-map-range/server-port-map.
    network_para_vlans = mapear_network_para_vlans(vlans_info)
    profiles = coletar_vlans_dos_profiles(linhas_comparacao, profiles, network_para_vlans)

    # 4) Resultado final.
    resultado = []
    for vlan in vlans_base:
        info_vlan = vlans_info.get(vlan)
        linha_resultado = {
            "VLAN": vlan,
            "Encontrado": "VERDADEIRO" if info_vlan else "FALSO",
            "NAGs": info_vlan["NAGs"] if info_vlan else "",
            "Network": info_vlan["Network"] if info_vlan else "",
        }

        for nome_profile, vlans_profile in profiles.items():
            nome_coluna = nome_profile if nome_profile not in COLUNAS_FIXAS else f"Profile - {nome_profile}"
            linha_resultado[nome_coluna] = "VERDADEIRO" if vlan in vlans_profile else "FALSO"

        resultado.append(linha_resultado)

    df = pd.DataFrame(resultado)
    df.to_excel(arquivo_saida, index=False)

    detalhes_profiles = "\n".join(
        f"  - {profile}: {len(vlans)} VLAN(s) identificada(s)"
        for profile, vlans in profiles.items()
    ) or "  - Nenhum profile identificado"

    mensagem = (
        f"Arquivo gerado com sucesso:\n{arquivo_saida}\n\n"
        f"VLANs do arquivo base: {len(vlans_base)}\n"
        f"VLANs mapeadas em Networks: {len(vlans_info)}\n"
        f"Termos de Profile pesquisados: {len(termos_profiles)}\n"
        f"Profiles completos identificados: {len(profiles)}\n\n"
        f"Profiles:\n{detalhes_profiles}"
    )

    if termos_sem_match:
        mensagem += "\n\nTermos de Profile sem correspondência:\n  - " + "\n  - ".join(termos_sem_match)

    print(mensagem)

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo("Processamento concluído", mensagem)
    root.destroy()


if __name__ == "__main__":
    main()

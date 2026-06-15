#!/usr/bin/env python3
"""
Auto Paste - Envia arquivos permanecendo sempre na janela do Discord (Com tempo de upload seguro)
Dependencias: xdotool, xclip
Instalar: sudo apt install xdotool xclip
"""

import os
import subprocess
import time
import sys
import math
import re


def check_deps():
    missing = []
    for tool in ("xdotool", "xclip"):
        if subprocess.run(["which", tool], capture_output=True).returncode != 0:
            missing.append(tool)
    if missing:
        print(f"\n[ERRO] Ferramentas faltando: {', '.join(missing)}")
        print(f"Instale com: sudo apt install {' '.join(missing)}")
        sys.exit(1)


def copy_files_to_clipboard(filepaths: list):
    """Copia os arquivos para o clipboard em segundo plano (funciona em qualquer janela)."""
    uris = "\r\n".join(f"file://{os.path.abspath(f)}" for f in filepaths) + "\r\n"
    proc = subprocess.Popen(
        ["xclip", "-selection", "clipboard", "-t", "text/uri-list"],
        stdin=subprocess.PIPE
    )
    proc.communicate(uris.encode())
    time.sleep(0.3)


def alt_tab():
    """Dá Alt+Tab apenas para entrar no Discord no início."""
    subprocess.run(["xdotool", "key", "alt+Tab"], capture_output=True)
    time.sleep(0.7)


def ctrl_v():
    subprocess.run(["xdotool", "key", "ctrl+v"], capture_output=True)
    time.sleep(0.5)


def ctrl_r():
    subprocess.run(["xdotool", "key", "ctrl+r"], capture_output=True)
    time.sleep(0.5)


def press_enter():
    subprocess.run(["xdotool", "key", "Return"], capture_output=True)
    time.sleep(0.3)


def countdown(seconds: int, label: str = ""):
    for i in range(seconds, 0, -1):
        print(f"\r  Aguardando {label}: {i:3d}s ", end="", flush=True)
        time.sleep(1)
    print()


def get_all_files(directory: str):
    try:
        entries = os.listdir(directory)
    except FileNotFoundError:
        print(f"\n[ERRO] Diretorio nao encontrado: {directory}")
        sys.exit(1)

    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    entries.sort(key=natural_sort_key)
    files = [os.path.join(directory, f) for f in entries if os.path.isfile(os.path.join(directory, f))]

    if not files:
        print("\n[ERRO] Nenhum arquivo encontrado no diretorio.")
        sys.exit(1)
    return files


def chunk(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def main():
    print("=" * 55)
    print("  AUTO PASTE - Modo Focado no Discord (Com Upload Seguro)")
    print("=" * 55)

    check_deps()

    print()
    directory = input("Diretorio dos arquivos: ").strip()
    directory = os.path.expanduser(directory)

    wait_input = input("Aguardar entre cada lote de 10 em segundos [padrao 30]: ").strip()
    wait_secs = int(wait_input) if wait_input.isdigit() else 30

    reset_input = input("Deseja dar Ctrl+R no Discord periodicamente? (s/n) [padrao s]: ").strip().lower()
    do_reset = reset_input != 'n'

    if do_reset:
        lotes_reset_input = input("Dar Ctrl+R a cada quantos lotes enviados? [padrao 50]: ").strip()
        lotes_to_reset = int(lotes_reset_input) if lotes_reset_input.isdigit() else 50

        tempo_reset_input = input("Quantos segundos o Discord leva para recarregar apos o Ctrl+R? [padrao 30]: ").strip()
        wait_reset_secs = int(tempo_reset_input) if tempo_reset_input.isdigit() else 30
    else:
        lotes_to_reset = 99999
        wait_reset_secs = 0

    delay_input = input("\nDelay inicial para você ir ao Discord a primeira vez [padrão 5]: ").strip()
    delay_start = int(delay_input) if delay_input.isdigit() else 5

    all_files = get_all_files(directory)
    total = len(all_files)
    total_lotes = math.ceil(total / 10)

    print(f"\n{total} arquivo(s) — {total_lotes} lote(s) de ate 10")
    print("-" * 55)

    print()
    input("Pressione ENTER para iniciar... (Deixe a janela do Discord logo atrás deste terminal)")
    print()

    # Contagem inicial ainda no terminal
    countdown(delay_start, "para mudar para o Discord")
    
    # Entra na janela do Discord apenas uma vez no início
    alt_tab()

    for lote_num, lote in enumerate(chunk(all_files, 10), 1):
        # 1. Copia o lote atual em segundo plano
        copy_files_to_clipboard(lote)

        # 2. Cola na janela do Discord
        ctrl_v()

        # 3. Aguarda o Discord carregar os arquivos na caixa de texto antes de enviar
        time.sleep(2.5)

        # 4. Envia o lote
        press_enter()
        print(f"  OK! Lote {lote_num} enviado.")

        # 5. GERENCIAMENTO DE ESPERA SEGURO
        # Se for o lote do reset:
        if do_reset and lote_num % lotes_to_reset == 0 and lote_num < total_lotes:
            # Primeiro espera o tempo normal para os arquivos terminarem de subir pro servidor
            countdown(wait_secs, f"para concluir o upload do lote {lote_num} antes do reset")
            
            # Agora que está seguro, reinicia a interface
            print(f"  -> Lote limite atingido. Aplicando Ctrl+R no Discord...")
            ctrl_r()
            
            # Espera o tempo do reset para o Discord reabrir
            countdown(wait_reset_secs, "para recarregamento da interface do Discord")
        
        # Se NÃO for lote de reset, apenas espera o tempo normal do próximo lote
        elif lote_num < total_lotes:
            countdown(wait_secs, f"proximo lote ({lote_num + 1}/{total_lotes})")

    print("\n[FIM] Todos os arquivos foram processados!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INTERROMPIDO] Automacao cancelada.")
        sys.exit(0)

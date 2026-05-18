#!/usr/bin/env python3
"""
Auto Paste - Envia TODOS os arquivos para o Discord em lotes de 10 de uma vez
Dependencias: xdotool, xclip
Instalar: sudo apt install xdotool xclip
"""

import os
import subprocess
import time
import sys
import math


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
    """Copia vários arquivos de uma vez para o clipboard como URI list."""
    uris = "\r\n".join(f"file://{os.path.abspath(f)}" for f in filepaths) + "\r\n"
    proc = subprocess.Popen(
        ["xclip", "-selection", "clipboard", "-t", "text/uri-list"],
        stdin=subprocess.PIPE
    )
    proc.communicate(uris.encode())
    time.sleep(0.3)


def alt_tab():
    subprocess.run(["xdotool", "key", "alt+Tab"], capture_output=True)
    time.sleep(0.7)


def ctrl_v():
    subprocess.run(["xdotool", "key", "ctrl+v"], capture_output=True)
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
        entries = sorted(os.listdir(directory))
    except FileNotFoundError:
        print(f"\n[ERRO] Diretorio nao encontrado: {directory}")
        sys.exit(1)

    files = [
        os.path.join(directory, f)
        for f in entries
        if os.path.isfile(os.path.join(directory, f))
    ]

    if not files:
        print("\n[ERRO] Nenhum arquivo encontrado no diretorio.")
        sys.exit(1)

    return files


def chunk(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def main():
    print("=" * 55)
    print("  AUTO PASTE - Enviar todos os arquivos pro Discord")
    print("  Modo: 10 arquivos de uma vez")
    print("=" * 55)

    check_deps()

    print()
    directory = input("Diretorio dos arquivos: ").strip()
    directory = os.path.expanduser(directory)

    wait_input = input("Aguardar entre cada lote de 10 em segundos [padrao 30]: ").strip()
    wait_secs = int(wait_input) if wait_input.isdigit() else 30

    delay_input = input("Delay inicial para voce ir ao Discord em segundos [padrao 5]: ").strip()
    delay_start = int(delay_input) if delay_input.isdigit() else 5

    all_files = get_all_files(directory)
    total = len(all_files)
    total_lotes = math.ceil(total / 10)

    print(f"\n{total} arquivo(s) — {total_lotes} lote(s) de ate 10")
    print("-" * 55)
    for lote_num, lote in enumerate(chunk(all_files, 10), 1):
        print(f"  Lote {lote_num}:")
        for f in lote:
            print(f"    - {os.path.basename(f)}")
    print("-" * 55)

    print()
    input("Pressione ENTER para iniciar...")
    print()

    countdown(delay_start, "comecando em")

    for lote_num, lote in enumerate(chunk(all_files, 10), 1):
        nomes = ", ".join(os.path.basename(f) for f in lote)
        print(f"\n[Lote {lote_num}/{total_lotes}] Copiando {len(lote)} arquivo(s):")
        for f in lote:
            print(f"  - {os.path.basename(f)}")

        # 1. Copia os 10 arquivos de uma vez
        copy_files_to_clipboard(lote)

        # 2. Alt+Tab pro Discord
        print("\n  -> Alt+Tab...")
        alt_tab()

        # 3. Ctrl+V — cola os 10 de uma vez
        print("  -> Ctrl+V...")
        ctrl_v()

        # 4. Aguarda o Discord processar os arquivos antes do Enter
        time.sleep(2.0)

        # 5. Enter para enviar
        print("  -> Enter...")
        press_enter()

        print(f"  OK! Lote {lote_num} enviado.")

        # Volta pro terminal
        time.sleep(0.5)
        alt_tab()

        # Aguarda antes do proximo lote (exceto no ultimo)
        if lote_num < total_lotes:
            countdown(wait_secs, f"lote {lote_num + 1}")

    print(f"\n{'=' * 55}")
    print(f"  Concluido! {total} arquivo(s) em {total_lotes} lote(s) enviados.")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INTERROMPIDO] Automacao cancelada pelo usuario.")
        sys.exit(0)

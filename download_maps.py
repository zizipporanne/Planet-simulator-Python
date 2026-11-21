#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baixa as texturas do Earth Simulator na resolução original.
Não redimensiona nem recomprime: os arquivos são salvos como vieram da NASA.

Uso:
    python download_maps.py           # baixa só o que estiver faltando
    python download_maps.py --force   # baixa de novo (guarda a versão atual como *.bak.jpg)
"""

import sys
import os
import urllib.request
import urllib.error
from io import BytesIO
from pathlib import Path

from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
TIMEOUT = 60
RETRIES = 3

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ),
    "Accept": "image/jpeg,image/png,image/*;q=0.8",
}

MAPS = {
    "earth_texture.jpg": "https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73909/world.topo.bathy.200412.3x5400x2700.jpg",
    "earth_political.jpg": "https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57752/land_shallow_topo_2048.jpg",
    "earth_detailed.jpg": "https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57730/land_ocean_ice_2048.jpg",
}


def fetch(url: str) -> bytes:
    """Baixa a URL com nova tentativa em caso de falha de rede."""
    request = urllib.request.Request(url, headers=HEADERS)
    last_error = None
    for attempt in range(1, RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as e:
            last_error = e
            print(f"  tentativa {attempt}/{RETRIES} falhou: {e}")
    raise last_error


def validate(data: bytes) -> bytes:
    """Confirma que os bytes são uma imagem válida, sem alterá-la."""
    Image.open(BytesIO(data)).verify()
    return data


def download_maps(force: bool = False) -> bool:
    all_ok = True
    for filename, url in MAPS.items():
        dest = SCRIPT_DIR / filename

        if dest.exists():
            if not force:
                print(f"{filename} já existe, pulando")
                continue
            backup = dest.with_name(dest.stem + ".bak" + dest.suffix)
            os.replace(dest, backup)
            print(f"  versão anterior guardada em {backup.name}")

        print(f"Baixando {filename}...")
        tmp = dest.with_suffix(".part")
        try:
            data = validate(fetch(url))
            tmp.write_bytes(data)
            os.replace(tmp, dest)
            size = Image.open(dest).size
            print(f"  OK: {dest.name} ({size[0]}x{size[1]})")
        except Exception as e:
            all_ok = False
            print(f"  ERRO em {filename}: {e}")
            print(f"  Baixe manualmente em: {url}")
            print(f"  e salve como: {dest}")
            if tmp.exists():
                tmp.unlink()
    return all_ok


if __name__ == "__main__":
    ok = download_maps(force="--force" in sys.argv)
    sys.exit(0 if ok else 1)
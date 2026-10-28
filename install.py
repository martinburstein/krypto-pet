#!/usr/bin/env python3
"""Install the canonical Krypto desktop pet using Python's standard library."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import uuid

ROOT = Path(__file__).resolve().parent
FILES = {
    'pet.json': 'b81a81a830aa61e921423cda44614da6703bc4b79e574bf7d83ecec58b1f7e3e',
    'spritesheet.webp': '49b0a5a1e4f34d26c9cc39bd14b6508cb85a3407f179f0e0364b6c59ab7c732d',
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def install(codex_home):
    source = ROOT / 'codex' / 'krypto-four-paws'
    for name, expected in FILES.items():
        if digest(source / name) != expected:
            raise SystemExit('Source checksum mismatch: ' + name)
    manifest = json.loads((source / 'pet.json').read_text(encoding='utf-8'))
    if manifest['id'] != 'krypto-four-paws' or manifest['spritesheetPath'] != 'spritesheet.webp':
        raise SystemExit('Unexpected pet manifest.')
    home = Path(codex_home).expanduser().resolve()
    pets = home / 'pets'
    destination = pets / 'krypto-four-paws'
    if destination.is_symlink():
        raise SystemExit('The destination is a symlink; inspect it before installing.')
    if destination.exists():
        if all((destination / name).is_file() and digest(destination / name) == expected
               for name, expected in FILES.items()):
            print('Canonical Krypto is already installed: ' + str(destination))
            return destination
        raise SystemExit('A different Krypto installation already exists. It was left untouched: '
                         + str(destination))
    pets.mkdir(parents=True, exist_ok=True)
    staging = home / ('.krypto-install-' + uuid.uuid4().hex)
    staging.mkdir()
    for name, expected in FILES.items():
        shutil.copyfile(source / name, staging / name)
        if digest(staging / name) != expected:
            raise SystemExit('Staged checksum mismatch; the existing pet collection is untouched.')
    if destination.exists():
        raise SystemExit('The destination appeared during installation; inspect it before retrying.')
    staging.rename(destination)
    print('Installed Krypto: ' + str(destination))
    print('In the desktop app: Settings > Pets > Refresh, then choose Krypto · Four Paws.')
    return destination

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-home', default=os.environ.get('CODEX_HOME', str(Path.home() / '.codex')),
                        help='Custom Codex home directory; defaults to CODEX_HOME or ~/.codex')
    install(parser.parse_args().codex_home)

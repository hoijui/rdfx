from pathlib import Path
from rdfx_cli import clean_ttl

if __name__ == "__main__":
    inputPath = Path('./test.ttl')
    clean_ttl(inputPath)

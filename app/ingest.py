from pathlib import Path


def run(path: str = "data") -> None:
    p = Path(path)
    print(f"[ingest] placeholder: future file processing will run under {p.resolve()}")


if __name__ == "__main__":
    run()

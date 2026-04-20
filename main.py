# Thin root entrypoint so the repo can be run with `python main.py`.
import argparse
from app.main import run


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    run(port=args.port)

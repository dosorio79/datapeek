# Thin root entrypoint so the repo can be run with `python main.py`.
from app.main import run


if __name__ == "__main__":
    run()

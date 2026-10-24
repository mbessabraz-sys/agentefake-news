import uvicorn

from config.settings import HOST, PORT
from src.utils.logger import configure_logging


def main() -> None:
    configure_logging()
    uvicorn.run("api:app", host=HOST, port=PORT)


if __name__ == "__main__":
    main()
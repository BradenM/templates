import httpx
from github import Github
from loguru import logger
from pathlib import Path

from pydantic import BaseModel, BaseSettings, SecretStr


github_graphql_url = "https://api.github.com/graphql"


class Settings(BaseSettings):
    input_user_token: SecretStr
    input_token: SecretStr
    github_workspace: Path
    github_output: Path
    httpx_timeout: int = 30


def get_graphql_response(*, settings: Settings, query: str, **variables):
    headers = {"Authorization": f"token {settings.input_token.get_secret_value()}"}
    response = httpx.post(
        github_graphql_url,
        headers=headers,
        timeout=settings.httpx_timeout,
        json={"query": query, "variables": variables, "operationName": "Q"},
    )
    if response.status_code != 200:
        logger.error(f"Response was not 200, vars: {variables}")
        logger.error(response.text)
        raise RuntimeError(response.text)
    data = response.json()
    return data


def set_output(settings: Settings, **values) -> None:
    with settings.github_output.open("a") as f:
        for key, value in values.items():
            cmd = f"{key}={value}\n"
            f.write(cmd)


def main():
    settings = Settings()
    logger.info("config: {}", settings)


if __name__ == "__main__":
    main()

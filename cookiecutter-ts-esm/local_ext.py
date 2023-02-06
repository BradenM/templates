import sh
from typing import Sequence
from cookiecutter.utils import simple_filter
import requests
import re
from dataclasses import dataclass, asdict


@dataclass
class Version:
    major: str | None = None
    minor: str | None = None
    patch: str | None = None
    prerelease: str | None = None
    buildmetadata: str | None = None


VERSION_REGEX = r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)(\.(?P<patch>0|[1-9]\d*))?(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"


def _get_asdf_latest(plugin: str) -> str:
    latest = sh.asdf.latest(plugin, _nl=False)  # type: ignore
    return str(latest).strip()


def _get_latest_npm_package(package: str, default: str) -> str:
    url = "https://registry.npmjs.org/-/package/{}/dist-tags"
    response = requests.get(url.format(package))
    version = default.lstrip("^")
    if response.ok:
        version = response.json().get("latest", version)
    return f"^{version}"


def _parse_version(input: str) -> Version:
    if matches := re.match(VERSION_REGEX, input):
        return Version(**matches.groupdict())
    return Version()


@simple_filter
def asdf_latest(v: str, *, plugin: str) -> str:
    if v == "latest":
        return _get_asdf_latest(plugin)
    return v


@simple_filter
def nodejs_major(v: str) -> str:
    if "lts" in v:
        return v
    return v.split(".")[0].strip()


@simple_filter
def npm_latest(v: str, default: str = "") -> str:
    return _get_latest_npm_package(v, default)


@simple_filter
def dict_merge(v: dict, other: dict) -> dict:
    return v | other


@simple_filter
def zip_dict(v: Sequence, other: Sequence) -> dict:
    return dict(zip(v, other))


@simple_filter
def version_dict(v: str) -> dict[str, str | None]:
    result = _parse_version(v)
    return asdict(result)

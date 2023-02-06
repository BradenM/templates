from collections.abc import Iterator
from pathlib import Path
from enum import Enum
from typing import NamedTuple
from cookiecutter.utils import rmtree


RENDER_TYPE = "{{ cookiecutter.project_type }}"


class RenderSet(NamedTuple):
    override: str | None
    exclude: set[str]


class RenderMode(Enum):
    PACKAGE = RenderSet(override=None, exclude=set())
    SUB_PACKAGE = RenderSet(
        override="sub",
        exclude={
            "LICENSE",
            "pnpm-workspace.yaml",
            "release-please-config.json",
            ".github",
            ".gitignore",
            ".envrc",
            ".tool-versions",
            ".npmrc",
        },
    )

    @property
    def exclude_paths(self) -> Iterator[Path]:
        for str_path in self.value.exclude:
            path = Path.cwd() / Path(str_path)
            if path.is_dir():
                yield from path.rglob("*")
            yield path

    @property
    def override_paths(self) -> Iterator[tuple[Path, Path]]:
        if self.value.override is None:
            return
        for override in Path.cwd().rglob(f"{self.value.override}.*"):
            target = override.parent / override.name[len(self.value.override) + 1 :]
            if override.exists():
                yield override, target

    def override_for(self, path: Path) -> Path | None:
        if self.value.override is None:
            return None
        override_name = f"{self.value.override}.{path.name}"
        override_path = path.parent / override_name
        return override_path if override_path.exists() else None


def rel_cwd(path: Path):
    return path.relative_to(Path.cwd())


render_mode = RenderMode[RENDER_TYPE]
other_modes = [i for i in RenderMode if i != render_mode]

# override
for override, target in render_mode.override_paths:
    print("override: {} ==> {}".format(rel_cwd(override), rel_cwd(target)))
    target.unlink()
    override.rename(target)

# drop
for drop in render_mode.exclude_paths:
    print("dropping: {}".format(rel_cwd(drop)))
    if drop.is_dir():
        rmtree(drop)
    else:
        drop.unlink(missing_ok=True)

# cleanup unused overrides.
for other in other_modes:
    for override, _ in other.override_paths:
        override.unlink(missing_ok=True)

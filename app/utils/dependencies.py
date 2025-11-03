"""Utility helpers to ensure optional runtime dependencies are installed."""

from __future__ import annotations

import importlib
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class DependencyCheck:
    module: str
    package: str
    optional: bool = True


PYPI_DEPENDENCIES: Dict[str, DependencyCheck] = {
    "pygame": DependencyCheck(module="pygame", package="pygame", optional=True),
}


def ensure_optional_dependencies() -> None:
    """Attempt to install any missing optional dependencies from PyPI."""

    for check in PYPI_DEPENDENCIES.values():
        try:
            importlib.import_module(check.module)
        except ModuleNotFoundError:
            install_dependency(check)


def install_dependency(check: DependencyCheck) -> None:
    """Install ``check.package`` via pip using the current interpreter."""

    print(f"Instalando dependencia opcional '{check.package}'...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", check.package],
        check=False,
    )
    if result.returncode != 0 and not check.optional:
        raise RuntimeError(f"No se pudo instalar la dependencia requerida: {check.package}")
    if result.returncode != 0:
        print(
            f"Advertencia: no se pudo instalar '{check.package}'. Algunas características opcionales pueden no funcionar."
        )

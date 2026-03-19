from __future__ import annotations

import platform
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DeviceInfo:
    label: str
    detail: str
    uses_gpu: bool


def detect_compute_device() -> DeviceInfo:
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Darwin" and machine in {"arm64", "aarch64"}:
        return DeviceInfo(
            label="Apple Silicon",
            detail="GPU detectada por plataforma; la simulación actual corre en CPU.",
            uses_gpu=True,
        )

    nvidia_name = _run_probe(
        ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
        required_binary="nvidia-smi",
    )
    if nvidia_name:
        first_name = nvidia_name.splitlines()[0].strip()
        return DeviceInfo(
            label="NVIDIA",
            detail=f"{first_name} detectada; la simulación actual corre en CPU.",
            uses_gpu=True,
        )

    if system == "Linux":
        lspci_output = _run_probe(["lspci"], required_binary="lspci")
        if "amd" in lspci_output.lower() or "radeon" in lspci_output.lower():
            return DeviceInfo(
                label="AMD",
                detail="GPU AMD detectada; la simulación actual corre en CPU.",
                uses_gpu=True,
            )
        if "nvidia" in lspci_output.lower():
            return DeviceInfo(
                label="NVIDIA",
                detail="GPU NVIDIA detectada; la simulación actual corre en CPU.",
                uses_gpu=True,
            )

    if system == "Windows":
        wmic_output = _run_probe(
            ["wmic", "path", "win32_VideoController", "get", "name"],
            required_binary="wmic",
        )
        lowered = wmic_output.lower()
        if "nvidia" in lowered:
            return DeviceInfo(
                label="NVIDIA",
                detail="GPU NVIDIA detectada; la simulación actual corre en CPU.",
                uses_gpu=True,
            )
        if "amd" in lowered or "radeon" in lowered:
            return DeviceInfo(
                label="AMD",
                detail="GPU AMD detectada; la simulación actual corre en CPU.",
                uses_gpu=True,
            )

    return DeviceInfo(
        label="CPU only",
        detail="No se detectó una GPU compatible o no fue posible sondearla.",
        uses_gpu=False,
    )


def _run_probe(command: list[str], required_binary: str) -> str:
    if shutil.which(required_binary) is None:
        return ""
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=1.5,
        )
    except (subprocess.SubprocessError, OSError):
        return ""
    return completed.stdout.strip()

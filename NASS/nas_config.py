from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import yaml


@dataclass(frozen=True)
class NasConfig:
    nas_ip: str
    nas_share: str
    unidad_temp: str

    @classmethod
    def load(cls, config_path: Optional[Union[str, Path]] = None) -> "NasConfig":
        # Determine the path to the configuration file
        path = (
            Path(config_path)
            if config_path
            else Path(__file__).resolve().parent.parent / "config.yaml"
        )

        with path.open(encoding="utf-8") as config_file:
            values = yaml.safe_load(config_file)

        if not isinstance(values, dict):
            raise ValueError(f"La configuración YAML no contiene un objeto válido: {path}")

        required_keys = ("nas_ip", "nas_share", "unidad_temp")
        missing_keys = [
            key
            for key in required_keys
            if not isinstance(values.get(key), str) or not values[key].strip()
        ]
        if missing_keys:
            raise ValueError(f"Faltan valores válidos en {path}: {', '.join(missing_keys)}")

        return cls(**{key: values[key] for key in required_keys})
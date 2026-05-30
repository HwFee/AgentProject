from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SkillPackage:
    name: str
    description: str
    full_content: str
    scripts_dir: Optional[Path] = None
    source_path: Optional[Path] = None

import yaml
from pathlib import Path
from typing import List, Optional

from skills.package import SkillPackage


class SkillPackageLoader:
    def __init__(self, skills_dir: str = "../skills"):
        self.skills_dir = Path(skills_dir).resolve()

    def discover(self) -> List[SkillPackage]:
        packages = []
        if not self.skills_dir.exists():
            return packages
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                pkg = self._parse(skill_md)
                if pkg:
                    packages.append(pkg)
        return packages

    def _parse(self, path: Path) -> Optional[SkillPackage]:
        try:
            content = path.read_text(encoding="utf-8")
            name = path.parent.name
            description = ""
            body = content

            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    name = frontmatter.get("name", name)
                    description = frontmatter.get("description", "")
                    body = parts[2].strip()

            return SkillPackage(
                name=name,
                description=description,
                full_content=body,
                scripts_dir=path.parent / "scripts",
                source_path=path,
            )
        except Exception:
            return None

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Skill:
    name: str
    description: str
    full_content: str
    scripts_dir: Path


class SkillRegistry:
    def __init__(self, skills_dir: str = "skills"):
        self.skills: Dict[str, Skill] = {}
        self.metadata: List[Dict[str, str]] = []
        self.skills_dir = Path(skills_dir)
        self.discover_skills()

    def discover_skills(self):
        if not self.skills_dir.exists():
            return
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                skill = self._parse_skill_md(skill_md)
                self.skills[skill.name] = skill
                self.metadata.append({"name": skill.name, "description": skill.description})

    def _parse_skill_md(self, path: Path) -> Skill:
        content = path.read_text(encoding="utf-8")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return Skill(
                    name=frontmatter.get("name", path.parent.name),
                    description=frontmatter.get("description", ""),
                    full_content=body,
                    scripts_dir=path.parent / "scripts",
                )
        return Skill(
            name=path.parent.name, description="",
            full_content=content, scripts_dir=path.parent / "scripts",
        )

    def get_system_prompt_section(self) -> str:
        if not self.metadata:
            return ""
        lines = ["You have access to the following skills. They will be activated when relevant:"]
        for meta in self.metadata:
            lines.append(f"- {meta['name']}: {meta['description']}")
        return "\n".join(lines)

    def match_skills(self, context: str) -> List[Skill]:
        context_lower = context.lower()
        matched = []
        for skill in self.skills.values():
            keywords = self._extract_keywords(skill.description)
            if any(kw in context_lower for kw in keywords):
                matched.append(skill)
        return matched

    def _extract_keywords(self, description: str) -> List[str]:
        words = description.lower().split()
        stop_words = {"the", "a", "an", "is", "are", "to", "for", "of", "in", "on", "this", "when", "or", "and", "with", "use", "you", "can", "that", "it"}
        return [w.strip(".,()[]") for w in words if w.strip(".,()[]") not in stop_words and len(w) > 2]


# Global singleton
skill_registry = SkillRegistry()

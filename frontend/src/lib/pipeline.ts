export const SKILL_LABELS: Record<string, string> = {
  'requirement.intake': '需求理解',
  'planning.outline': '生成大纲',
  'research.collect': '资料收集',
  'data.analyze': '数据分析',
  'writing.draft_report': '撰写初稿',
  'writing.de_ai_polish': '去 AI 化润色',
  'review.quality_check': '质量检查',
  'export.report_files': '导出文件',
}

export const LEGACY_AGENT_LABELS: Record<string, string> = {
  research: 'ResearchAgent',
  write: 'WriterAgent',
  review: 'ReviewerAgent',
  data: 'DataAgent',
  simple: 'SimpleAgent',
}

export function getSkillLabel(skillId: string): string {
  return SKILL_LABELS[skillId] || LEGACY_AGENT_LABELS[skillId] || skillId
}

export function isPipelineSkill(skillId: string): boolean {
  return skillId.includes('.')
}

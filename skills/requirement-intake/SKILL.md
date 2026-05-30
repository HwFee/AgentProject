---
name: requirement-intake
description: >
  Cleanse and analyze user requirements for report generation.
  Extract topics, objectives, scope, format, constraints, and keywords.
  Use when starting any report generation task to understand what the user needs.
metadata:
  version: 1.0.0
  category: planning
---

# Requirement Intake

Analyze user report requirements and extract structured information.

## When to Use

- Starting a new report generation task
- User provides a vague or unstructured request
- Clarifying ambiguous requirements
- Normalizing user input for downstream processing

## Output Format

Extract and output as JSON:

```json
{
  "topic": "报告主题",
  "objectives": ["目标1", "目标2"],
  "scope": "范围描述",
  "format": "期望格式",
  "constraints": ["约束1", "约束2"],
  "keywords": ["关键词1", "关键词2"],
  "normalized_text": "整理后的完整需求描述"
}
```

## Analysis Steps

1. **Identify Core Topic**
   - What is the report about?
   - What domain/industry?

2. **Extract Objectives**
   - What should the report achieve?
   - What decisions will it inform?

3. **Define Scope**
   - What's included?
   - What's explicitly excluded?
   - Time period covered?

4. **Determine Format**
   - Expected output format (PDF, DOCX, Markdown)
   - Approximate length
   - Required sections
   - Style (academic, business, technical, casual)

5. **Identify Constraints**
   - Deadline
   - Budget/tokens
   - Language requirements
   - Confidentiality level
   - Source restrictions

6. **Extract Keywords**
   - Core concepts
   - Named entities
   - Technical terms
   - Geographic references

## Requirements

- Output in Chinese
- Only output JSON, no other text
- Infer implicit requirements
- Supplement missing dimensions

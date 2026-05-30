---
name: data-analyst
description: >
  Data visualization, report generation, SQL queries, and spreadsheet analysis.
  Use when analyzing datasets, creating charts, running SQL, building dashboards,
  or generating data-driven reports. Supports CSV, Excel, JSON, and database sources.
metadata:
  version: 1.0.0
  category: data-analysis
---

# Data Analyst

Analyze data, create visualizations, and generate insights from structured datasets.

## When to Use

- Analyzing CSV, Excel, JSON, or database tables
- Creating charts, graphs, or dashboards
- Running SQL queries
- Generating statistical summaries
- Building data-driven reports

## Workflow

1. **Load Data**
   - Read CSV/Excel/JSON into pandas DataFrame
   - Inspect structure: columns, types, missing values
   - Handle encoding issues (UTF-8, GBK for Chinese)

2. **Explore**
   - Summary statistics (mean, median, std, min, max)
   - Missing value analysis
   - Distribution of key columns
   - Correlation matrix for numeric columns

3. **Analyze**
   - Group-by aggregations
   - Time-series trends (if date columns exist)
   - Top-N rankings
   - Segmentation analysis

4. **Visualize**
   - Line charts for trends
   - Bar charts for comparisons
   - Pie charts for proportions
   - Heatmaps for correlations
   - Histograms for distributions
   - Scatter plots for relationships

5. **Report**
   - Executive summary of key findings
   - Methodology note
   - Data quality assessment
   - Recommendations based on insights

## Coding Standards

- Use pandas, numpy, matplotlib, seaborn
- Handle exceptions gracefully
- Save charts as PNG with descriptive filenames
- Print key results for logging
- Comment complex transformations

## Output Format

```markdown
## Data Analysis Report

### Dataset Overview
- Rows: X, Columns: Y
- Date range: [if applicable]
- Missing values: X%

### Key Findings
1. ...
2. ...

### Visualizations
[Attach generated charts]

### Recommendations
- ...
```

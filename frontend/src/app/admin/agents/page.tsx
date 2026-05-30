import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const pipelineSteps = [
  { id: 'requirement.intake', label: '需求理解', model: 'Pro' },
  { id: 'planning.outline', label: '生成大纲', model: 'Pro' },
  { id: 'research.collect', label: '资料收集', model: 'Pro' },
  { id: 'data.analyze', label: '数据分析', model: 'Pro' },
  { id: 'writing.draft_report', label: '撰写初稿', model: 'Flash' },
  { id: 'writing.de_ai_polish', label: '去 AI 化润色', model: 'Flash' },
  { id: 'review.quality_check', label: '质量检查', model: 'Pro' },
  { id: 'export.report_files', label: '导出文件', model: '-' },
]

export default function AdminAgentsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Skill Pipeline</h1>
        <p className="text-sm text-gray-500">查看报告生成的 Pipeline 步骤和 Skill 配置</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Pipeline 执行流程</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-3">
            {pipelineSteps.map((step, index) => (
              <div key={step.id} className="flex items-center gap-3">
                <div className="flex flex-col items-center rounded-lg border bg-white p-4 shadow-sm">
                  <div className="mb-2 text-sm font-medium">{step.label}</div>
                  <div className="mb-1 text-xs text-gray-400">{step.id}</div>
                  <Badge variant="outline">{step.model}</Badge>
                </div>
                {index < pipelineSteps.length - 1 && (
                  <div className="h-px w-6 bg-gray-300" />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Skill 列表</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {pipelineSteps.map((step) => (
              <div key={step.id} className="flex items-center justify-between rounded-md border p-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-xs font-medium">
                    {step.label[0]}
                  </div>
                  <div>
                    <p className="font-medium">{step.label}</p>
                    <p className="text-xs text-gray-500">{step.id}</p>
                  </div>
                </div>
                <div className="text-right">
                  <Badge variant="outline">模型: {step.model}</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

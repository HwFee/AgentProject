import { CheckCircle, XCircle, Trophy } from 'lucide-react'
import type { AgentType } from '@/types'
import { getAgentConfig } from '@/lib/utils'

interface ResultCardProps {
  fromAgent: AgentType
  summary: string
  details?: string
  status?: 'completed' | 'failed'
}

function tryParseScores(details?: string): Record<string, Record<string, number>> | null {
  if (!details) return null
  try {
    const parsed = JSON.parse(details)
    if (typeof parsed === 'object' && parsed !== null) {
      return parsed
    }
  } catch {
    // not JSON
  }
  return null
}

function ScoreTable({ scores }: { scores: Record<string, Record<string, number>> }) {
  const allDimensions = new Set<string>()
  for (const reportScores of Object.values(scores)) {
    for (const dim of Object.keys(reportScores)) {
      allDimensions.add(dim)
    }
  }
  const dimensions = Array.from(allDimensions)

  // Calculate totals
  const totals: Record<string, number> = {}
  for (const [reportId, reportScores] of Object.entries(scores)) {
    totals[reportId] = Object.values(reportScores).reduce((a, b) => a + b, 0)
  }

  return (
    <div className="mt-2 overflow-hidden rounded border border-gray-200">
      <table className="w-full text-xs">
        <thead>
          <tr className="bg-gray-50">
            <th className="px-2 py-1 text-left font-medium text-gray-600">报告</th>
            {dimensions.map((dim) => (
              <th key={dim} className="px-2 py-1 text-center font-medium text-gray-600">{dim}</th>
            ))}
            <th className="px-2 py-1 text-center font-medium text-gray-700">总分</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(scores).map(([reportId, reportScores]) => (
            <tr key={reportId} className="border-t border-gray-100">
              <td className="px-2 py-1 font-medium text-gray-700">{reportId}</td>
              {dimensions.map((dim) => (
                <td key={dim} className="px-2 py-1 text-center text-gray-600">
                  {reportScores[dim] ?? '-'}/10
                </td>
              ))}
              <td className="px-2 py-1 text-center font-semibold text-blue-600">{totals[reportId]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function ResultCard({ fromAgent, summary, details, status = 'completed' }: ResultCardProps) {
  const config = getAgentConfig(fromAgent)
  const isFailed = status === 'failed'
  const scores = tryParseScores(details)
  const isWinner = summary.includes('最佳报告')

  return (
    <div className={`rounded-lg border bg-white ${isFailed ? 'border-red-200 border-l-[3px] border-l-red-400' : 'border-gray-200 border-l-[3px] border-l-green-400'}`}>
      <div className="px-3 py-2">
        <div className="flex items-center gap-2 mb-1">
          {isFailed ? (
            <XCircle size={14} className="text-red-500" />
          ) : isWinner ? (
            <Trophy size={14} className="text-amber-500" />
          ) : (
            <CheckCircle size={14} className="text-green-500" />
          )}
          <span className={`text-sm font-semibold ${isFailed ? 'text-red-600' : 'text-gray-700'}`}>
            {config.name}
          </span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${isFailed ? 'text-red-600 bg-red-50' : isWinner ? 'text-amber-600 bg-amber-50' : 'text-green-600 bg-green-50'}`}>
            {isFailed ? '执行失败' : isWinner ? '评审完成' : '已完成'}
          </span>
        </div>
        <div className="text-sm text-gray-700">{summary}</div>
        {scores && <ScoreTable scores={scores} />}
        {details && !scores && (
          <div className="mt-1.5 text-xs text-gray-500">
            {details}
          </div>
        )}
      </div>
    </div>
  )
}

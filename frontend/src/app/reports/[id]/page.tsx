import { useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  CheckCircle2,
  ChevronRight,
  Clipboard,
  Download,
  File,
  FileSpreadsheet,
  FileText,
  Globe2,
  Loader2,
  PenLine,
  RotateCcw,
  Search,
  Send,
  Wrench,
} from 'lucide-react'
import { useArtifactVersions, useReport, useReportArtifacts, useReportStatus, useToolEvents } from '@/api/queries'
import { useChatEdit, useRestoreVersion } from '@/api/mutations'
import { useNow } from '@/hooks/useNow'
import { Skeleton } from '@/components/ui/skeleton'
import { StatusBadge } from '@/components/ui/StatusBadge'

type NodeStatus = {
  node_id: string
  agent_type?: string
  status: string
  started_at?: string | null
  completed_at?: string | null
  output_data?: Record<string, unknown>
}

type ArtifactVersion = {
  id: number
  version: number
  content?: string
  change_reason?: string
  created_at?: string
}

type Artifact = {
  id: number
  report_id: number
  step_id: string
  skill_id: string
  logical_name: string
  filename: string
  artifact_type: string
  current_version_id?: number
  current_version?: ArtifactVersion
  version_count?: number
  created_at: string
  updated_at: string
}

type ToolEvent = {
  id: number
  report_id: number
  step_id: string
  skill_id: string
  event_type: string
  title: string
  description?: string
  status: string
  input_data?: Record<string, unknown>
  output_data?: Record<string, unknown>
  artifact_id?: number | null
  artifact_version_id?: number | null
  started_at?: string | null
  completed_at?: string | null
  sort_order?: number
}

type StepRow = {
  id: string
  name: string
  status: string
  durationText: string
  startedAt?: string | null
  completedAt?: string | null
  events: ToolEvent[]
  completedEvents: number
  artifacts: Artifact[]
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const stepOrder = [
  'requirement_intake',
  'outline_plan',
  'research_collect',
  'data_analyze',
  'draft_report',
  'de_ai_polish',
  'quality_check',
  'export_files',
]

const stepNameFallback: Record<string, string> = {
  requirement_intake: '需求理解',
  outline_plan: '生成大纲',
  research_collect: '资料收集',
  data_analyze: '数据分析',
  draft_report: '撰写初稿',
  de_ai_polish: '去 AI 化润色',
  quality_check: '质量检查',
  export_files: '导出文件',
}

const eventLabels: Record<string, string> = {
  analyze_requirement: '解析需求',
  search: '搜索资料',
  read_url: '读取网页',
  read_file: '读取文件',
  create_file: '创建文件',
  edit_file: '编辑文件',
  analyze_data: '分析数据',
  generate_chart: '生成图表',
  review: '质量检查',
  export_pdf: '导出 PDF',
  export_docx: '导出 DOCX',
}

const stepTone: Record<string, string> = {
  requirement_intake: 'cyan',
  outline_plan: 'indigo',
  research_collect: 'emerald',
  data_analyze: 'blue',
  draft_report: 'violet',
  de_ai_polish: 'pink',
  quality_check: 'orange',
  export_files: 'teal',
}

const toneClasses: Record<string, { dot: string; border: string; title: string; soft: string }> = {
  cyan: { dot: 'bg-cyan-500', border: 'border-cyan-200', title: 'text-cyan-700', soft: 'bg-cyan-50/55' },
  indigo: { dot: 'bg-indigo-500', border: 'border-indigo-200', title: 'text-indigo-700', soft: 'bg-indigo-50/55' },
  emerald: { dot: 'bg-emerald-500', border: 'border-emerald-200', title: 'text-emerald-700', soft: 'bg-emerald-50/55' },
  blue: { dot: 'bg-blue-500', border: 'border-blue-200', title: 'text-blue-700', soft: 'bg-blue-50/55' },
  violet: { dot: 'bg-violet-500', border: 'border-violet-200', title: 'text-violet-700', soft: 'bg-violet-50/55' },
  pink: { dot: 'bg-pink-500', border: 'border-pink-200', title: 'text-pink-700', soft: 'bg-pink-50/55' },
  orange: { dot: 'bg-orange-500', border: 'border-orange-200', title: 'text-orange-700', soft: 'bg-orange-50/55' },
  teal: { dot: 'bg-teal-500', border: 'border-teal-200', title: 'text-teal-700', soft: 'bg-teal-50/55' },
}

const toneColors: Record<string, string> = {
  cyan: '#06b6d4',
  indigo: '#6366f1',
  emerald: '#10b981',
  blue: '#3b82f6',
  violet: '#8b5cf6',
  pink: '#ec4899',
  orange: '#f97316',
  teal: '#14b8a6',
}

function StepMarker({ status, tone }: { status: string; tone: string }) {
  const color = toneColors[tone] || toneColors.blue
  const isCompleted = status === 'completed'
  const isRunning = status === 'running' || status === 'planning'
  const isFailed = status === 'failed'

  return (
    <svg className="h-5 w-5 drop-shadow-sm" viewBox="0 0 20 20" aria-hidden="true">
      <circle cx="10" cy="10" r="8.5" fill="white" stroke={isRunning ? color : '#e5e7eb'} strokeWidth="1.5" />
      {isRunning && <circle cx="10" cy="10" r="5.25" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeDasharray="18 18" />}
      {isCompleted && (
        <>
          <circle cx="10" cy="10" r="6" fill={color} />
          <path d="M6.8 10.1 8.8 12.1 13.4 7.6" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </>
      )}
      {isFailed && (
        <>
          <circle cx="10" cy="10" r="6" fill="#ef4444" />
          <path d="m7.7 7.7 4.6 4.6M12.3 7.7l-4.6 4.6" fill="none" stroke="white" strokeWidth="1.7" strokeLinecap="round" />
        </>
      )}
      {!isCompleted && !isRunning && !isFailed && <circle cx="10" cy="10" r="4" fill="white" stroke={color} strokeWidth="2" />}
    </svg>
  )
}

function parseDate(value?: string | null) {
  if (!value) return NaN
  return new Date(value).getTime()
}

function formatDateTime(value?: string | null) {
  const time = parseDate(value)
  if (!isFinite(time)) return '-'
  const date = new Date(time)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

function formatDuration(ms: number) {
  if (!isFinite(ms) || ms < 0) return '-'
  const sec = Math.floor(ms / 1000)
  if (sec < 60) return `${sec}s`
  const min = Math.floor(sec / 60)
  const rem = sec % 60
  if (min < 60) return `${min}m ${rem}s`
  const hr = Math.floor(min / 60)
  return `${hr}h ${min % 60}m`
}

function prettyJson(value: unknown) {
  if (!value) return '{}'
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}

function staticUrl(path?: string | null) {
  return path ? `${API_BASE_URL}/static/${path}` : undefined
}

function getArtifactIcon(type?: string) {
  if (type === 'json') return <FileSpreadsheet className="h-4 w-4" />
  if (type === 'markdown') return <FileText className="h-4 w-4" />
  return <File className="h-4 w-4" />
}

function getEventIcon(type: string) {
  if (type === 'search') return <Search className="h-4 w-4" />
  if (type === 'read_url') return <Globe2 className="h-4 w-4" />
  if (type.includes('file') || type === 'create_file' || type === 'edit_file') return <FileText className="h-4 w-4" />
  if (type === 'export_pdf' || type === 'export_docx') return <Download className="h-4 w-4" />
  return <Wrench className="h-4 w-4" />
}

function getEventFilename(event: ToolEvent, artifact?: Artifact) {
  if (artifact?.filename) return artifact.filename
  const output = event.output_data || {}
  return String(output.filename || event.title || eventLabels[event.event_type] || '工具调用')
}

export default function ReportDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const reportId = Number(id)
  const now = useNow()

  const { data: report, isLoading } = useReport(reportId)
  const { data: statusData } = useReportStatus(reportId)
  const { data: artifactData } = useReportArtifacts(reportId)
  const { data: toolEventData } = useToolEvents(reportId)

  const artifacts = useMemo<Artifact[]>(() => Array.isArray(artifactData) ? artifactData : [], [artifactData])
  const toolEvents = useMemo<ToolEvent[]>(() => Array.isArray(toolEventData) ? toolEventData : [], [toolEventData])

  const [expandedSteps, setExpandedSteps] = useState<Record<string, boolean>>({})
  const [expandedEvents, setExpandedEvents] = useState<Record<number, boolean>>({})
  const [selectedArtifactId, setSelectedArtifactId] = useState<number | null>(null)
  const [selectedEventId, setSelectedEventId] = useState<number | null>(null)
  const [chatMessage, setChatMessage] = useState('')

  const chatMutation = useChatEdit()
  const restoreMutation = useRestoreVersion()

  const isRunning = report?.status === 'running' || report?.status === 'planning' || statusData?.status === 'running'
  const nodes = useMemo<NodeStatus[]>(() => (statusData?.nodes || []) as NodeStatus[], [statusData])
  const attachments = statusData?.attachments || []

  const artifactsById = useMemo(() => new Map(artifacts.map((art) => [art.id, art])), [artifacts])
  const finalArtifact = useMemo(
    () => artifacts.find((art) => art.logical_name === '最终报告') || artifacts[artifacts.length - 1] || null,
    [artifacts]
  )
  const selectedEvent = useMemo(
    () => toolEvents.find((event) => event.id === selectedEventId) || null,
    [selectedEventId, toolEvents]
  )
  const selectedArtifact = useMemo(() => {
    if (selectedArtifactId) return artifactsById.get(selectedArtifactId) || null
    if (selectedEvent?.artifact_id) return artifactsById.get(selectedEvent.artifact_id) || null
    return finalArtifact
  }, [artifactsById, finalArtifact, selectedArtifactId, selectedEvent])
  const { data: versions } = useArtifactVersions(reportId, selectedArtifact?.id)

  const eventsByStep = useMemo(() => {
    const grouped = new Map<string, ToolEvent[]>()
    for (const event of toolEvents) {
      const list = grouped.get(event.step_id) || []
      list.push(event)
      grouped.set(event.step_id, list)
    }
    for (const list of grouped.values()) {
      list.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0) || a.id - b.id)
    }
    return grouped
  }, [toolEvents])

  const stepRows = useMemo<StepRow[]>(() => {
    // Deduplicate nodes: prefer completed over running over pending
    const statusPriority = (s: string) =>
      s === 'completed' ? 3 : s === 'running' || s === 'planning' ? 2 : s === 'failed' ? 0 : 1
    const nodeByStep = new Map<string, NodeStatus>()
    for (const node of nodes) {
      const existing = nodeByStep.get(node.node_id)
      if (!existing || statusPriority(node.status) > statusPriority(existing.status)) {
        nodeByStep.set(node.node_id, node)
      }
    }
    const allStepIds = new Set<string>()
    nodes.forEach((node) => allStepIds.add(node.node_id))
    artifacts.forEach((art) => allStepIds.add(art.step_id))
    toolEvents.forEach((event) => allStepIds.add(event.step_id))

    return Array.from(allStepIds)
      .sort((a, b) => {
        const ia = stepOrder.indexOf(a)
        const ib = stepOrder.indexOf(b)
        if (ia === -1 && ib === -1) return a.localeCompare(b)
        if (ia === -1) return 1
        if (ib === -1) return -1
        return ia - ib
      })
      .map((stepId) => {
        const node = nodeByStep.get(stepId)
        const events = eventsByStep.get(stepId) || []
        const stepArtifacts = artifacts.filter((art) => art.step_id === stepId)
        const started = node?.started_at || events[0]?.started_at || events[0]?.completed_at
        const completed = node?.completed_at || events[events.length - 1]?.completed_at
        const startMs = parseDate(started)
        const endMs = completed ? parseDate(completed) : now
        return {
          id: stepId,
          name: stepNameFallback[stepId] || stepId,
          status: node?.status || (events.length ? 'completed' : 'pending'),
          durationText: started ? formatDuration(endMs - startMs) : '-',
          startedAt: started,
          completedAt: completed,
          events,
          completedEvents: events.filter((event) => event.status === 'completed').length,
          artifacts: stepArtifacts,
        }
      })
  }, [artifacts, eventsByStep, nodes, now, toolEvents])

  const previewMarkdown = selectedArtifact?.current_version?.content || report?.final_report_md || ''
  const downloadPdf = staticUrl(report?.pdf_path)
  const downloadDocx = staticUrl(report?.docx_path)

  const handleSend = () => {
    const message = chatMessage.trim()
    if (!message || chatMutation.isPending) return
    const mentionedStep = stepRows.find((step) => message.includes(`@${step.name}`) || message.includes(`@${step.id}`))
    chatMutation.mutate({
      taskId: reportId,
      message,
      targetStepId: mentionedStep?.id,
      targetArtifactId: mentionedStep ? undefined : selectedArtifact?.id,
    }, {
      onSuccess: () => setChatMessage(''),
    })
  }

  const handleCopyMarkdown = async () => {
    if (!previewMarkdown) return
    await navigator.clipboard?.writeText(previewMarkdown)
  }

  if (isLoading) {
    return (
      <div className="h-[calc(100vh-2rem)] p-4">
        <Skeleton className="mb-4 h-12 w-72" />
        <div className="grid h-[calc(100%-4rem)] grid-cols-[320px_minmax(0,1fr)_360px] gap-4">
          <Skeleton className="h-full" />
          <Skeleton className="h-full" />
          <Skeleton className="h-full" />
        </div>
      </div>
    )
  }

  if (!report) {
    return <div className="p-8">报告不存在</div>
  }

  return (
    <div className="-m-6 h-[calc(100vh-4rem)] overflow-hidden bg-gray-50 px-7 py-5">
      <header className="mb-5 flex items-start justify-between">
        <div className="flex items-start gap-3">
          <button
            onClick={() => navigate('/reports')}
            className="mt-1 flex h-9 w-9 items-center justify-center rounded-md border border-gray-200 bg-white text-gray-700 shadow-sm hover:bg-gray-50"
            aria-label="返回"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-950">报告详情 - {report.status === 'completed' ? '已完成' : report.status === 'running' ? '运行中' : report.status}</h1>
              <StatusBadge status={report.status} />
            </div>
            <div className="mt-1 text-sm text-gray-500">报告列表 &gt; 报告详情</div>
          </div>
        </div>
      </header>

      <div className="grid h-[calc(100%-4.5rem)] min-h-0 grid-cols-[320px_minmax(0,1fr)_360px] gap-4">
        <aside className="flex min-h-0 flex-col rounded-lg border border-gray-200 bg-white shadow-sm">
          <div className="min-h-0 flex-1 overflow-y-auto px-5 py-5">
            <section>
              <h2 className="text-lg font-semibold text-gray-950">报告信息</h2>
              <div className="mt-8 flex items-center gap-2">
                <h3 className="text-xl font-bold text-gray-950">{report.title}</h3>
                <PenLine className="h-4 w-4 text-gray-400" />
              </div>
              <dl className="mt-8 space-y-5 text-sm">
                <div className="flex justify-between gap-4">
                  <dt className="text-gray-500">创建时间</dt>
                  <dd className="text-gray-950">{formatDateTime(report.created_at)}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-gray-500">更新时间</dt>
                  <dd className="text-gray-950">{formatDateTime(report.updated_at)}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-gray-500">生成模式</dt>
                  <dd className="text-gray-950">{report.mode === 'generate' ? '从零生成' : report.mode || '-'}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-gray-500">状态</dt>
                  <dd><StatusBadge status={report.status} /></dd>
                </div>
              </dl>
            </section>

            {attachments.length > 0 && (
              <section className="mt-7 border-t border-gray-100 pt-5">
                <h2 className="text-lg font-semibold text-gray-950">附件 ({attachments.length})</h2>
                <div className="mt-4 divide-y divide-gray-100 rounded-md border border-gray-100">
                  {attachments.map((att) => (
                    <div key={att.id} className="flex items-center gap-3 px-3 py-2 text-sm">
                      <FileSpreadsheet className="h-4 w-4 shrink-0 text-emerald-600" />
                      <span className="min-w-0 flex-1 truncate text-gray-900">{att.filename}</span>
                      <span className="text-xs text-gray-400">{att.status}</span>
                    </div>
                  ))}
                </div>
              </section>
            )}

            <section className="mt-7 border-t border-gray-100 pt-5">
              <h2 className="text-lg font-semibold text-gray-950">执行步骤</h2>
              <div className="mt-4 space-y-3">
                {stepRows.map((step) => {
                  const tone = toneClasses[stepTone[step.id] || 'blue']
                  return (
                    <button
                      key={step.id}
                      onClick={() => setExpandedSteps((prev) => ({ ...prev, [step.id]: true }))}
                      className="flex w-full items-center gap-3 rounded-md px-1 py-1 text-left"
                    >
                      <span className={`h-3 w-3 rounded-full ${tone.dot}`} />
                      <span className={`min-w-0 flex-1 truncate text-sm font-semibold ${tone.title}`}>{step.name}</span>
                      <StatusBadge status={step.status} />
                    </button>
                  )
                })}
              </div>
            </section>
          </div>

          <div className="shrink-0 border-t border-gray-100 p-5">
            <button
              className="flex h-11 w-full items-center justify-center rounded-md border border-gray-200 bg-white text-sm font-semibold text-gray-900 hover:bg-gray-50"
              onClick={() => navigate('/reports')}
            >
              返回报告列表
            </button>
          </div>
        </aside>

        <main className="flex min-h-0 flex-col rounded-lg border border-gray-200 bg-white shadow-sm">
          <div className="shrink-0 border-b border-gray-100 px-5 py-4">
            <h2 className="text-lg font-semibold text-gray-950">执行过程</h2>
          </div>

          <div className="scrollbar-none min-h-0 flex-1 overflow-y-auto px-6 py-4">
            <div className="relative pl-7">
              {stepRows.length > 1 && <div className="absolute left-[7px] top-5 bottom-5 w-px bg-gray-200" />}
              <div className="space-y-1">
                {stepRows.map((step) => {
                  const expanded = !!expandedSteps[step.id]
                  const toneKey = stepTone[step.id] || 'blue'
                  return (
                    <div key={step.id} className="relative">
                      <span className="absolute -left-[28px] top-3.5 z-10 flex h-5 w-5 items-center justify-center bg-white">
                        <StepMarker status={step.status} tone={toneKey} />
                      </span>
                      <div className={`rounded-md border border-transparent bg-white transition-colors ${expanded ? 'border-gray-200 shadow-sm' : 'hover:bg-gray-50'}`}>
                        <button
                          className="flex w-full items-center gap-3 px-3 py-3 text-left"
                          onClick={() => setExpandedSteps((prev) => ({ ...prev, [step.id]: !prev[step.id] }))}
                        >
                          <ChevronRight className={`h-4 w-4 shrink-0 text-gray-400 transition-transform ${expanded ? 'rotate-90' : ''}`} />
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2">
                              <h3 className="font-semibold text-gray-950">{step.name}</h3>
                              <StatusBadge status={step.status} />
                            </div>
                            {step.events.length > 0 && (
                              <p className="mt-0.5 text-xs text-gray-500">
                                {step.completedEvents}/{step.events.length} 个工具调用
                                {step.artifacts.length ? `，生成 ${step.artifacts.length} 个文件` : ''}
                              </p>
                            )}
                          </div>
                          <span className="shrink-0 rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-500">{step.durationText}</span>
                        </button>

                        {expanded && step.events.length > 0 && (
                          <div className="border-t border-gray-100 px-3 pb-3">
                            <div className="divide-y divide-gray-100">
                              {step.events.map((event) => {
                                const artifact = event.artifact_id ? artifactsById.get(event.artifact_id) : undefined
                                const eventExpanded = !!expandedEvents[event.id]
                                const isFailed = event.status === 'failed'
                                const isSearch = event.event_type === 'search'
                                const isFileEvent = ['read_file', 'create_file', 'edit_file', 'export_pdf', 'export_docx'].includes(event.event_type)
                                const query = isSearch ? String(event.input_data?.query || event.title) : ''
                                const searchResults = ((event.output_data?.results || event.output_data?.sources || []) as Array<{ title?: string; link?: string; url?: string; snippet?: string }>)
                                const filename = getEventFilename(event, artifact)
                                const startMs = parseDate(event.started_at)
                                const endMs = parseDate(event.completed_at)
                                const eventDuration = isFinite(startMs) && isFinite(endMs) ? formatDuration(endMs - startMs) : ''

                                return (
                                  <div key={event.id} className={isFailed ? 'bg-red-50/40' : 'bg-white'}>
                                    <div className="flex items-center gap-3 py-2.5">
                                      <button
                                        onClick={() => setExpandedEvents((prev) => ({ ...prev, [event.id]: !prev[event.id] }))}
                                        className="text-gray-400 transition-colors hover:text-gray-700"
                                        title="展开详情"
                                      >
                                        <ChevronRight className={`h-4 w-4 transition-transform ${eventExpanded ? 'rotate-90' : ''}`} />
                                      </button>
                                      <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gray-100 text-gray-500">
                                        {getEventIcon(event.event_type)}
                                      </span>
                                      <div className="min-w-0 flex-1 text-left">
                                        <div className="flex items-center gap-2">
                                          <span className="text-sm font-medium text-gray-900">{eventLabels[event.event_type] || event.title}</span>
                                          <span className={`rounded px-1.5 py-0.5 text-xs ${isFailed ? 'bg-red-100 text-red-700' : 'bg-gray-50 text-gray-500'}`}>
                                            {event.status}
                                          </span>
                                        </div>
                                        <div className="mt-0.5 truncate text-xs text-gray-500">
                                          {isSearch ? (
                                            <span className="font-medium text-gray-700">{query}</span>
                                          ) : isFileEvent ? (
                                            <button
                                              onClick={() => {
                                                setSelectedEventId(event.id)
                                                if (event.artifact_id) setSelectedArtifactId(event.artifact_id)
                                              }}
                                              className="font-semibold text-blue-600 hover:text-blue-800 hover:underline"
                                            >
                                              {filename}
                                            </button>
                                          ) : (
                                            event.description || event.title
                                          )}
                                        </div>
                                      </div>
                                      {artifact && (
                                        <button
                                          onClick={() => {
                                            setSelectedEventId(event.id)
                                            setSelectedArtifactId(artifact.id)
                                          }}
                                          className="flex items-center gap-1 rounded border border-gray-200 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50"
                                        >
                                          {getArtifactIcon(artifact.artifact_type)}
                                          v{artifact.current_version?.version || 1}
                                        </button>
                                      )}
                                      {eventDuration && <span className="text-xs text-gray-400">{eventDuration}</span>}
                                    </div>

                                    {eventExpanded && (
                                      <div className="border-t border-gray-100 py-3 pl-10">
                                        {isSearch && searchResults.length > 0 ? (
                                          <div className="space-y-2">
                                            <div>
                                              <div className="mb-1 text-xs font-medium text-gray-500">搜索 query</div>
                                              <div className="rounded-md bg-gray-50 px-3 py-2 text-sm font-medium text-gray-700">{query}</div>
                                            </div>
                                            <div>
                                              <div className="mb-1 text-xs font-medium text-gray-500">搜索结果 ({searchResults.length})</div>
                                              <ul className="space-y-1.5">
                                                {searchResults.map((r, i) => (
                                                  <li key={i} className="flex items-start gap-2 text-xs">
                                                    <Globe2 className="mt-0.5 h-3 w-3 shrink-0 text-gray-400" />
                                                    <div className="min-w-0">
                                                      <a
                                                        href={r.link || r.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="line-clamp-1 text-blue-600 hover:underline"
                                                      >
                                                        {r.title || r.link || r.url}
                                                      </a>
                                                      {r.snippet && <p className="mt-0.5 line-clamp-2 text-gray-500">{r.snippet}</p>}
                                                    </div>
                                                  </li>
                                                ))}
                                              </ul>
                                            </div>
                                          </div>
                                        ) : (
                                          <div className="grid gap-3 md:grid-cols-2">
                                            <div>
                                              <div className="mb-1 text-xs font-medium text-gray-500">输入</div>
                                              <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-words rounded-md bg-gray-50 p-3 text-xs text-gray-700">
                                                {prettyJson(event.input_data || {})}
                                              </pre>
                                            </div>
                                            <div>
                                              <div className="mb-1 text-xs font-medium text-gray-500">输出</div>
                                              <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-words rounded-md bg-gray-50 p-3 text-xs text-gray-700">
                                                {prettyJson(event.output_data || {})}
                                              </pre>
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                    )}
                                  </div>
                                )
                              })}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          <div className="shrink-0 border-t border-gray-100 p-4">
            <div className="flex items-end gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2">
              <textarea
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                placeholder="输入修改指令，支持 @ 指定步骤..."
                rows={1}
                className="max-h-24 min-h-8 flex-1 resize-none border-0 bg-transparent py-1 text-sm text-gray-900 outline-none placeholder:text-gray-400"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSend()
                  }
                }}
              />
              <button
                onClick={handleSend}
                disabled={!chatMessage.trim() || chatMutation.isPending}
                className="flex h-8 w-8 items-center justify-center rounded-md text-gray-500 hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-300"
                aria-label="发送"
              >
                {chatMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </button>
            </div>
          </div>
        </main>

        <aside className="flex min-h-0 flex-col gap-4">
          <section className="flex min-h-0 flex-1 flex-col rounded-lg border border-gray-200 bg-white shadow-sm">
            <div className="shrink-0 border-b border-gray-100 px-5 py-4">
              <h2 className="text-lg font-semibold text-gray-950">{selectedArtifact ? '内容预览' : '报告预览'}</h2>
            </div>
            <div className="scrollbar-none min-h-0 flex-1 overflow-y-auto p-5">
              {previewMarkdown ? (
                <div className="prose prose-sm max-w-none text-gray-900">
                  <ReactMarkdown>{previewMarkdown}</ReactMarkdown>
                </div>
              ) : isRunning ? (
                <div className="flex h-full flex-col items-center justify-center text-center text-gray-500">
                  <Loader2 className="mb-4 h-10 w-10 animate-spin text-blue-600" />
                  <div className="font-semibold text-gray-900">生成中</div>
                </div>
              ) : (
                <div className="flex h-full flex-col items-center justify-center text-center text-gray-400">
                  <FileText className="mb-3 h-10 w-10" />
                  <div>暂无内容</div>
                </div>
              )}
            </div>
          </section>

          <section className="shrink-0 rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-950">操作</h2>
            <div className="mt-4 space-y-3">
              <a
                href={downloadPdf}
                target="_blank"
                rel="noopener noreferrer"
                className={`flex h-11 items-center justify-center gap-2 rounded-md border border-gray-200 text-sm font-medium ${downloadPdf ? 'text-gray-700 hover:bg-gray-50' : 'pointer-events-none text-gray-300'}`}
              >
                <Download className="h-4 w-4" />
                下载 PDF
              </a>
              <a
                href={downloadDocx}
                target="_blank"
                rel="noopener noreferrer"
                className={`flex h-11 items-center justify-center gap-2 rounded-md border border-gray-200 text-sm font-medium ${downloadDocx ? 'text-gray-700 hover:bg-gray-50' : 'pointer-events-none text-gray-300'}`}
              >
                <FileText className="h-4 w-4" />
                下载 DOCX
              </a>
              <button
                onClick={handleCopyMarkdown}
                disabled={!previewMarkdown}
                className="flex h-11 w-full items-center justify-center gap-2 rounded-md border border-gray-200 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:text-gray-300"
              >
                <Clipboard className="h-4 w-4" />
                复制 Markdown
              </button>
            </div>
          </section>

          {selectedArtifact && (versions || []).length > 1 && (
            <section className="max-h-52 shrink-0 overflow-y-auto rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-950">版本</h2>
              <div className="mt-3 space-y-2">
                {(versions || []).map((version: ArtifactVersion) => (
                  <div key={version.id} className="flex items-center gap-2 rounded-md border border-gray-100 px-3 py-2 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                    <span className="flex-1">v{version.version}</span>
                    <button
                      onClick={() => restoreMutation.mutate({ taskId: reportId, artifactId: selectedArtifact.id, versionId: version.id })}
                      className="rounded p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-900"
                      title="恢复版本"
                    >
                      <RotateCcw className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            </section>
          )}
        </aside>
      </div>
    </div>
  )
}

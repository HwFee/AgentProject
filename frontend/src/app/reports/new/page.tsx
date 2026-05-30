import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCreateReport } from '@/api/mutations'
import { Button } from '@/components/ui/button'
import { Sparkles, LayoutTemplate, BookOpen, Edit3, Upload, X } from 'lucide-react'
import type { ReportMode } from '@/types'

const modes: {
  id: ReportMode
  label: string
  desc: string
  icon: typeof Sparkles
}[] = [
  { id: 'generate', label: '从零生成', desc: '从零开始，AI 根据您的需求生成完整的报告内容。', icon: Sparkles },
  { id: 'template', label: '基于模板', desc: '使用预设模板为基础，快速生成标准化报告。', icon: LayoutTemplate },
  { id: 'reference', label: '参考资料', desc: '基于上传的参考文档，生成带引用的专业报告。', icon: BookOpen },
  { id: 'edit', label: '迭代修改', desc: '基于已有报告或初稿，进行优化和扩展。', icon: Edit3 },
]

export default function CreateReportPage() {
  const [title, setTitle] = useState('')
  const [requirement, setRequirement] = useState('')
  const [mode, setMode] = useState<ReportMode>('generate')
  const [files, setFiles] = useState<File[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const createReport = useCreateReport()
  const navigate = useNavigate()

  const handleFileChange = (newFiles: FileList | null) => {
    const fileArray = Array.from(newFiles || [])
    if (files.length + fileArray.length > 10) {
      alert('最多上传 10 个文件')
      return
    }
    setFiles([...files, ...fileArray])
  }

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const result = await createReport.mutateAsync({ title, requirement, mode, files })
      navigate(`/reports/${result.task_id}`)
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      {/* Title */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">创建新报告</h1>
        <p className="mt-1 text-sm text-gray-500">输入报告需求，选择生成模式，AI 将为您生成专业报告</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Report Title */}
        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">报告标题</label>
          <input
            type="text"
            placeholder="输入报告标题"
            className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        {/* Requirement */}
        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">需求描述</label>
          <textarea
            placeholder="详细描述报告需求，如报告目的、目标受众、格式要求等。"
            className="h-32 w-full resize-none rounded-lg border border-gray-200 px-4 py-3 text-sm text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            required
            maxLength={5000}
          />
          <div className="mt-1 text-right text-xs text-gray-400">{requirement.length}/5000</div>
        </div>

        {/* Mode Selection */}
        <div>
          <label className="mb-3 block text-sm font-medium text-gray-700">生成模式</label>
          <div className="grid grid-cols-4 gap-4">
            {modes.map((m) => (
              <div
                key={m.id}
                className={`cursor-pointer rounded-lg border-2 p-4 transition-all ${
                  mode === m.id
                    ? 'border-blue-500 bg-blue-50/50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setMode(m.id)}
              >
                <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${
                  mode === m.id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-500'
                }`}>
                  <m.icon className="h-5 w-5" />
                </div>
                <p className="mt-3 text-sm font-semibold text-gray-900">{m.label}</p>
                <p className="mt-1 text-xs leading-relaxed text-gray-500">{m.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* File Upload */}
        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">附件上传</label>
          <div
            className={`relative rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
              isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
            }`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => { e.preventDefault(); setIsDragging(false); handleFileChange(e.dataTransfer.files) }}
          >
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
              <Upload className="h-5 w-5 text-gray-500" />
            </div>
            <p className="mt-3 text-sm text-gray-600">拖拽文件到此处，或点击上传</p>
            <p className="mt-1 text-xs text-gray-400">支持 PDF、DOCX、TXT、XLSX 格式</p>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="absolute inset-0 cursor-pointer opacity-0"
              onChange={(e) => handleFileChange(e.target.files)}
              accept=".pdf,.docx,.txt,.xlsx"
            />
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="mt-3 space-y-2">
              {files.map((file, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 px-3 py-2">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-gray-700">{file.name}</span>
                    <span className="text-xs text-gray-400">({(file.size / 1024).toFixed(1)} KB)</span>
                  </div>
                  <button type="button" onClick={() => removeFile(i)} className="text-gray-400 hover:text-red-500">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
          <p className="mt-2 text-xs text-gray-400">已上传 {files.length}/10 个文件</p>
        </div>

        {/* Submit */}
        <div className="flex justify-end">
          <Button
            type="submit"
            disabled={createReport.isPending}
            className="h-10 bg-blue-600 px-6 text-sm font-medium hover:bg-blue-700"
          >
            {createReport.isPending ? '生成中...' : '开始生成'}
          </Button>
        </div>
      </form>
    </div>
  )
}

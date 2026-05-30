import { FileDown, X } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

interface ReportPreviewProps {
  markdown: string
  pdfUrl?: string
  docxUrl?: string
  onClose?: () => void
}

export function ReportPreview({ markdown, pdfUrl, docxUrl, onClose }: ReportPreviewProps) {
  return (
    <div className="flex h-full flex-col border-l border-gray-200 bg-gray-50/50">
      <div className="flex items-center justify-between border-b border-gray-200 px-3 py-2">
        <span className="text-xs font-medium text-gray-500">报告预览</span>
        {onClose && (
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={14} />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {markdown ? (
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{markdown}</ReactMarkdown>
            </div>
          </div>
        ) : (
          <div className="flex h-32 items-center justify-center text-xs text-gray-400">
            报告生成中...
          </div>
        )}
      </div>

      <div className="border-t border-gray-200 p-3">
        <div className="flex gap-2">
          {pdfUrl && (
            <a
              href={pdfUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-1 items-center justify-center gap-1 rounded-md border border-gray-200 bg-white px-2 py-1.5 text-xs text-gray-600 transition-colors hover:bg-gray-50"
            >
              <FileDown size={12} />
              PDF
            </a>
          )}
          {docxUrl && (
            <a
              href={docxUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-1 items-center justify-center gap-1 rounded-md border border-gray-200 bg-white px-2 py-1.5 text-xs text-gray-600 transition-colors hover:bg-gray-50"
            >
              <FileDown size={12} />
              DOCX
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

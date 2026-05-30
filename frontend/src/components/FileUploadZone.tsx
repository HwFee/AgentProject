import { useRef, useCallback } from 'react'
import { Upload, X, FileText } from 'lucide-react'
import { cn } from '@/lib/utils'

interface FileUploadZoneProps {
  files: File[]
  onFilesChange: (files: File[]) => void
  maxFiles: number
  accept?: string
}

export default function FileUploadZone({
  files,
  onFilesChange,
  maxFiles,
  accept = '.doc,.docx,.pdf,.txt',
}: FileUploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFiles = useCallback(
    (newFiles: FileList | null) => {
      if (!newFiles) return
      const fileArray = Array.from(newFiles)
      const combined = [...files, ...fileArray]
      onFilesChange(combined.slice(0, maxFiles))
    },
    [files, maxFiles, onFilesChange]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      e.stopPropagation()
      handleFiles(e.dataTransfer.files)
    },
    [handleFiles]
  )

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleClick = useCallback(() => {
    inputRef.current?.click()
  }, [])

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      handleFiles(e.target.files)
      e.target.value = ''
    },
    [handleFiles]
  )

  const removeFile = useCallback(
    (index: number) => {
      onFilesChange(files.filter((_, i) => i !== index))
    },
    [files, onFilesChange]
  )

  const isFull = files.length >= maxFiles

  return (
    <div className="space-y-3">
      <div
        onClick={isFull ? undefined : handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className={cn(
          'flex flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-8 transition-colors',
          isFull
            ? 'cursor-not-allowed border-gray-200 bg-gray-50'
            : 'cursor-pointer border-gray-300 bg-white hover:border-primary hover:bg-gray-50'
        )}
      >
        <Upload className="mb-2 h-8 w-8 text-gray-400" />
        <p className="text-sm text-gray-600">
          {isFull ? (
            '已达到最大文件数量限制'
          ) : (
            <>
              <span className="font-medium text-primary">点击上传</span> 或拖拽文件到此处
            </>
          )}
        </p>
        <p className="mt-1 text-xs text-gray-400">
          支持 Word、PDF、TXT 格式
        </p>
      </div>

      <input
        ref={inputRef}
        type="file"
        multiple={maxFiles > 1}
        accept={accept}
        onChange={handleInputChange}
        className="hidden"
        disabled={isFull}
      />

      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">已上传文件</span>
            <span className="text-gray-400">
              已上传 {files.length}/{maxFiles}
            </span>
          </div>
          <ul className="space-y-2">
            {files.map((file, index) => (
              <li
                key={`${file.name}-${index}`}
                className="flex items-center justify-between rounded-md border bg-white px-3 py-2"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <FileText className="h-4 w-4 shrink-0 text-gray-400" />
                  <span className="truncate text-sm text-gray-700">{file.name}</span>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="ml-2 shrink-0 rounded p-1 hover:bg-gray-100"
                >
                  <X className="h-4 w-4 text-gray-400" />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

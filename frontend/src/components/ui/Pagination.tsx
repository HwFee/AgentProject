import { useState, useRef, useEffect } from 'react'
import { Button } from './button'
import { ChevronLeft, ChevronRight, ChevronDown } from 'lucide-react'

interface PaginationProps {
  page: number
  pageSize: number
  total: number
  onPageChange: (page: number) => void
  onPageSizeChange: (size: number) => void
}

function getPageRange(current: number, total: number): (number | string)[] {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const pages: (number | string)[] = [1]
  if (current > 3) pages.push('...')
  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let i = start; i <= end; i++) pages.push(i)
  if (current < total - 2) pages.push('...')
  pages.push(total)
  return pages
}

const pageSizeOptions = [
  { value: 5, label: '5条/页' },
  { value: 10, label: '10条/页' },
  { value: 20, label: '20条/页' },
  { value: 50, label: '50条/页' },
]

export function Pagination({ page, pageSize, total, onPageChange, onPageSizeChange }: PaginationProps) {
  const safePageSize = pageSize > 0 ? pageSize : pageSizeOptions[0].value
  const safeTotal = Number.isFinite(total) ? total : 0
  const totalPages = Math.max(1, Math.ceil(safeTotal / safePageSize))
  const pages = getPageRange(page, totalPages)
  const [open, setOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const currentLabel = pageSizeOptions.find((o) => o.value === pageSize)?.label || `${pageSize}条/页`

  return (
    <div className="flex items-center justify-between border-t border-gray-100 px-4 py-3">
      <div className="text-sm text-gray-500">共 {safeTotal} 条</div>
      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm" onClick={() => onPageChange(page - 1)} disabled={page <= 1} className="h-8 w-8 p-0">
          <ChevronLeft className="h-4 w-4" />
        </Button>
        {pages.map((p, i) =>
          p === '...' ? (
            <span key={`ellipsis-${i}`} className="px-2 text-sm text-gray-400">...</span>
          ) : (
            <Button
              key={p}
              variant={p === page ? 'default' : 'outline'}
              size="sm"
              onClick={() => onPageChange(p as number)}
              className={`h-8 min-w-[32px] px-2.5 text-xs ${p === page ? 'bg-gray-900 text-white hover:bg-gray-800' : ''}`}
            >
              {p}
            </Button>
          )
        )}
        <Button variant="outline" size="sm" onClick={() => onPageChange(page + 1)} disabled={page >= totalPages} className="h-8 w-8 p-0">
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
      {/* Custom page size dropdown */}
      <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setOpen(!open)}
          className="flex h-8 items-center gap-1 rounded-md border border-gray-200 bg-white px-3 text-xs text-gray-700 hover:border-gray-300 focus:outline-none focus:ring-1 focus:ring-gray-300"
        >
          {currentLabel}
          <ChevronDown className={`h-3.5 w-3.5 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`} />
        </button>
        {open && (
          <div className="absolute bottom-full right-0 z-50 mb-1 w-full min-w-[80px] rounded-md border border-gray-200 bg-white py-1 shadow-lg">
            {pageSizeOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => {
                  onPageSizeChange(option.value)
                  setOpen(false)
                }}
                className={`flex w-full items-center px-3 py-1.5 text-xs hover:bg-gray-50 ${
                  option.value === pageSize ? 'font-medium text-gray-900' : 'text-gray-600'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

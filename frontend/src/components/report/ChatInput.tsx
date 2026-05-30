import { useState } from 'react'
import { Send } from 'lucide-react'
import { StopButton } from './StopButton'

interface ChatInputProps {
  onSend: (message: string) => void
  onStop?: () => void
  isRunning?: boolean
  disabled?: boolean
}

export function ChatInput({ onSend, onStop, isRunning, disabled }: ChatInputProps) {
  const [value, setValue] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!value.trim() || disabled) return
    onSend(value.trim())
    setValue('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2 rounded-xl border border-gray-200 bg-gray-50 px-3 py-2">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={isRunning ? 'Agent 执行中...' : '输入消息...'}
        disabled={disabled}
        className="flex-1 bg-transparent text-sm outline-none placeholder:text-gray-400 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="flex h-7 items-center gap-1 rounded-md bg-blue-600 px-3 text-xs font-medium text-white transition-opacity hover:bg-blue-700 disabled:opacity-50"
      >
        <Send size={12} />
        发送
      </button>
      {isRunning && onStop && <StopButton onStop={onStop} />}
    </form>
  )
}

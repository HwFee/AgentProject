import { Square } from 'lucide-react'

interface StopButtonProps {
  onStop: () => void
  disabled?: boolean
}

export function StopButton({ onStop, disabled }: StopButtonProps) {
  return (
    <button
      onClick={onStop}
      disabled={disabled}
      className="flex h-7 w-7 items-center justify-center rounded-md border-[1.5px] border-gray-400 bg-white transition-colors hover:border-red-500 hover:text-red-500 disabled:opacity-50"
      title="停止执行"
    >
      <Square size={10} className="fill-gray-500 stroke-gray-500 hover:fill-red-500 hover:stroke-red-500" />
    </button>
  )
}

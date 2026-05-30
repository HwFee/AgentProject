interface UserMessageProps {
  content: string
  timestamp?: string
}

export function UserMessage({ content, timestamp }: UserMessageProps) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[70%]">
        <div className="rounded-2xl rounded-br-sm bg-blue-50 px-4 py-2.5 text-sm text-gray-800">
          {content}
        </div>
        {timestamp && (
          <div className="mt-1 text-right text-xs text-gray-400">
            {new Date(timestamp).toLocaleTimeString()}
          </div>
        )}
      </div>
    </div>
  )
}

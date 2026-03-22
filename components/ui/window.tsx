"use client"

import * as React from "react"
import { X, Minus } from "lucide-react"

interface WindowProps {
  title: string
  icon: React.ReactNode
  children: React.ReactNode
  isOpen: boolean
  isMinimized: boolean
  zIndex: number
  onClose: () => void
  onMinimize: () => void
  onFocus: () => void
  initialPosition?: { x: number; y: number }
}

export function Window({
  title,
  icon,
  children,
  isOpen,
  isMinimized,
  zIndex,
  onClose,
  onMinimize,
  onFocus,
  initialPosition = { x: 100, y: 50 },
}: WindowProps) {
  const [position, setPosition] = React.useState(initialPosition)
  const [isDragging, setIsDragging] = React.useState(false)
  const [dragOffset, setDragOffset] = React.useState({ x: 0, y: 0 })

  React.useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return
      setPosition({
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y,
      })
    }

    const handleMouseUp = () => {
      setIsDragging(false)
    }

    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove)
      document.addEventListener("mouseup", handleMouseUp)
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
    }
  }, [isDragging, dragOffset])

  const handleMouseDown = (e: React.MouseEvent) => {
    onFocus()
    if ((e.target as HTMLElement).closest("button")) return
    setIsDragging(true)
    setDragOffset({
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    })
  }

  if (!isOpen || isMinimized) return null

  return (
    <div
      className="absolute flex flex-col bg-white dark:bg-zinc-900 rounded-lg shadow-2xl border border-zinc-200 dark:border-zinc-700 overflow-hidden"
      style={{
        left: position.x,
        top: position.y,
        width: 500,
        minHeight: 350,
        zIndex,
      }}
      onMouseDown={onFocus}
    >
      <div
        className="flex items-center justify-between px-3 py-2 bg-zinc-100 dark:bg-zinc-800 cursor-move select-none"
        onMouseDown={handleMouseDown}
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium text-zinc-700 dark:text-zinc-200">
            {title}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={onMinimize}
            className="p-1 rounded hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
          >
            <Minus className="w-4 h-4 text-zinc-500" />
          </button>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
          >
            <X className="w-4 h-4 text-zinc-500 hover:text-red-500" />
          </button>
        </div>
      </div>
      <div className="flex-1 p-4 overflow-auto">{children}</div>
    </div>
  )
}

interface DesktopIconProps {
  icon: React.ReactNode
  label: string
  onClick: () => void
}

export function DesktopIcon({ icon, label, onClick }: DesktopIconProps) {
  return (
    <button
      onDoubleClick={onClick}
      className="flex flex-col items-center gap-1 p-2 rounded-lg hover:bg-white/20 transition-colors group"
    >
      <div className="w-12 h-12 flex items-center justify-center rounded-lg bg-white/90 dark:bg-zinc-800/90 shadow-md text-2xl">
        {icon}
      </div>
      <span className="text-xs font-medium text-white drop-shadow-md group-hover:bg-zinc-900/70 px-1 rounded">
        {label}
      </span>
    </button>
  )
}

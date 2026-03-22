"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface TaskbarItem {
  id: string
  label: string
  icon: React.ReactNode
  isMinimized: boolean
}

interface TaskbarProps {
  items: TaskbarItem[]
  onItemClick: (id: string) => void
}

export function Taskbar({ items, onItemClick }: TaskbarProps) {
  return (
    <div className="fixed bottom-0 left-0 right-0 h-10 bg-zinc-900/95 backdrop-blur-sm border-t border-zinc-700 flex items-center px-2 gap-1 z-50">
      <button className="px-3 py-1 text-sm font-medium text-white hover:bg-zinc-700 rounded transition-colors">
        开始
      </button>
      <div className="w-px h-6 bg-zinc-700 mx-1" />
      {items.map((item) => (
        <button
          key={item.id}
          onClick={() => onItemClick(item.id)}
          className={cn(
            "flex items-center gap-2 px-3 py-1 text-sm rounded transition-colors",
            item.isMinimized
              ? "text-zinc-400 hover:bg-zinc-700 hover:text-white"
              : "bg-zinc-700 text-white"
          )}
        >
          {item.icon}
          <span className="hidden sm:inline">{item.label}</span>
        </button>
      ))}
    </div>
  )
}

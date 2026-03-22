"use client"

import * as React from "react"
import { Globe, BookOpen, Pencil, FileText, MessageCircle } from "lucide-react"
import { Window, DesktopIcon } from "@/components/ui/window"
import { Taskbar } from "@/components/ui/taskbar"
import { Translator } from "@/components/agent/translator"
import { Vocabulary } from "@/components/agent/vocabulary"
import { Grammar } from "@/components/agent/grammar"
import { Exercise } from "@/components/agent/exercise"
import { Chat } from "@/components/agent/chat"

interface WindowState {
  id: string
  title: string
  icon: React.ReactNode
  component: React.ReactNode
  isOpen: boolean
  isMinimized: boolean
  zIndex: number
}

const windowPositions: Record<string, { x: number; y: number }> = {
  translator: { x: 150, y: 80 },
  vocabulary: { x: 200, y: 100 },
  grammar: { x: 250, y: 120 },
  exercise: { x: 180, y: 90 },
  chat: { x: 220, y: 110 },
}

const initialWindows: WindowState[] = [
  {
    id: "translator",
    title: "翻译",
    icon: <Globe className="w-4 h-4 text-blue-500" />,
    component: <Translator />,
    isOpen: false,
    isMinimized: false,
    zIndex: 1,
  },
  {
    id: "vocabulary",
    title: "词汇",
    icon: <BookOpen className="w-4 h-4 text-green-500" />,
    component: <Vocabulary />,
    isOpen: false,
    isMinimized: false,
    zIndex: 1,
  },
  {
    id: "grammar",
    title: "语法",
    icon: <Pencil className="w-4 h-4 text-purple-500" />,
    component: <Grammar />,
    isOpen: false,
    isMinimized: false,
    zIndex: 1,
  },
  {
    id: "exercise",
    title: "练习",
    icon: <FileText className="w-4 h-4 text-orange-500" />,
    component: <Exercise />,
    isOpen: false,
    isMinimized: false,
    zIndex: 1,
  },
  {
    id: "chat",
    title: "对话",
    icon: <MessageCircle className="w-4 h-4 text-pink-500" />,
    component: <Chat />,
    isOpen: false,
    isMinimized: false,
    zIndex: 1,
  },
]

export default function AgentPage() {
  const [windows, setWindows] = React.useState<WindowState[]>(initialWindows)
  const [maxZIndex, setMaxZIndex] = React.useState(1)

  const openWindow = (id: string) => {
    setMaxZIndex((prev) => prev + 1)
    setWindows((prev) =>
      prev.map((w) =>
        w.id === id ? { ...w, isOpen: true, isMinimized: false, zIndex: maxZIndex + 1 } : w
      )
    )
  }

  const closeWindow = (id: string) => {
    setWindows((prev) =>
      prev.map((w) => (w.id === id ? { ...w, isOpen: false } : w))
    )
  }

  const minimizeWindow = (id: string) => {
    setWindows((prev) =>
      prev.map((w) => (w.id === id ? { ...w, isMinimized: true } : w))
    )
  }

  const focusWindow = (id: string) => {
    setMaxZIndex((prev) => prev + 1)
    setWindows((prev) =>
      prev.map((w) => (w.id === id ? { ...w, zIndex: maxZIndex + 1 } : w))
    )
  }

  const restoreWindow = (id: string) => {
    const win = windows.find((w) => w.id === id)
    if (win?.isMinimized) {
      openWindow(id)
    } else {
      focusWindow(id)
    }
  }

  const icons = [
    { id: "translator", icon: <Globe />, label: "翻译" },
    { id: "vocabulary", icon: <BookOpen />, label: "词汇" },
    { id: "grammar", icon: <Pencil />, label: "语法" },
    { id: "exercise", icon: <FileText />, label: "练习" },
    { id: "chat", icon: <MessageCircle />, label: "对话" },
  ]

  const taskbarItems = windows
    .filter((w) => w.isOpen)
    .map((w) => ({
      id: w.id,
      label: w.title,
      icon: w.icon,
      isMinimized: w.isMinimized,
    }))

  return (
    <div className="h-screen w-full bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 overflow-hidden relative pb-10">
      <div className="absolute top-4 left-4 grid grid-cols-2 gap-4">
        {icons.map((item) => (
          <DesktopIcon
            key={item.id}
            icon={item.icon}
            label={item.label}
            onClick={() => openWindow(item.id)}
          />
        ))}
      </div>

      {windows.map((win) => (
        <Window
          key={win.id}
          title={win.title}
          icon={win.icon}
          isOpen={win.isOpen}
          isMinimized={win.isMinimized}
          zIndex={win.zIndex}
          onClose={() => closeWindow(win.id)}
          onMinimize={() => minimizeWindow(win.id)}
          onFocus={() => focusWindow(win.id)}
          initialPosition={windowPositions[win.id]}
        >
          {win.component}
        </Window>
      ))}

      <Taskbar items={taskbarItems} onItemClick={restoreWindow} />
    </div>
  )
}

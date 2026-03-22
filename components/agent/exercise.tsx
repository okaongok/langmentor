"use client"

import * as React from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { streamSSE } from "@/lib/stream"

export function Exercise() {
  const [topic, setTopic] = React.useState("")
  const [result, setResult] = React.useState("")
  const [loading, setLoading] = React.useState(false)

  async function handleGenerate() {
    setLoading(true)
    setResult("")

    try {
      for await (const chunk of streamSSE("http://localhost:8000/api/exercise", {
        topic: topic || "general",
      })) {
        setResult((prev) => prev + chunk)
      }
    } catch {
      setResult("生成失败，请检查后端连接")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1 block">
          练习主题（可选）
        </label>
        <Input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g., past tense, vocabulary..."
        />
      </div>
      <Button onClick={handleGenerate} disabled={loading} className="w-full">
        {loading ? "生成中..." : "生成练习题"}
      </Button>
      {result && (
        <div className="p-3 bg-zinc-100 dark:bg-zinc-800 rounded-lg whitespace-pre-wrap">
          <p className="text-sm text-zinc-500 mb-1">练习题</p>
          <p className="text-sm">{result}</p>
        </div>
      )}
    </div>
  )
}

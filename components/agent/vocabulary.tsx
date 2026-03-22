"use client"

import * as React from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { MarkdownRenderer } from "@/components/ui/markdown-renderer"
import { streamSSE } from "@/lib/stream"

export function Vocabulary() {
  const [word, setWord] = React.useState("")
  const [result, setResult] = React.useState("")
  const [loading, setLoading] = React.useState(false)

  async function handleExplain() {
    if (!word.trim()) return
    setLoading(true)
    setResult("")

    try {
      for await (const chunk of streamSSE("http://localhost:8000/api/explain", { word })) {
        setResult((prev) => prev + chunk)
      }
    } catch {
      setResult("查询失败，请检查后端连接")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1 block">
          输入单词
        </label>
        <Input
          value={word}
          onChange={(e) => setWord(e.target.value)}
          placeholder="Enter a word..."
          onKeyDown={(e) => e.key === "Enter" && handleExplain()}
        />
      </div>
      <Button onClick={handleExplain} disabled={loading} className="w-full">
        {loading ? "查询中..." : "查询释义"}
      </Button>
      {result && (
        <div className="p-3 bg-zinc-100 dark:bg-zinc-800 rounded-lg whitespace-pre-wrap">
          <p className="text-sm text-zinc-500 mb-1">词汇解释</p>
          <MarkdownRenderer content={result} />
        </div>
      )}
    </div>
  )
}

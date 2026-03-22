"use client"

import * as React from "react"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { streamSSE } from "@/lib/stream"

export function Grammar() {
  const [text, setText] = React.useState("")
  const [result, setResult] = React.useState("")
  const [loading, setLoading] = React.useState(false)

  async function handleCheck() {
    if (!text.trim()) return
    setLoading(true)
    setResult("")

    try {
      for await (const chunk of streamSSE("http://localhost:8000/api/grammar", { text })) {
        setResult((prev) => prev + chunk)
      }
    } catch {
      setResult("检查失败，请检查后端连接")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1 block">
          输入需要检查的英文
        </label>
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text to check grammar..."
          rows={4}
        />
      </div>
      <Button onClick={handleCheck} disabled={loading} className="w-full">
        {loading ? "检查中..." : "检查语法"}
      </Button>
      {result && (
        <div className="p-3 bg-zinc-100 dark:bg-zinc-800 rounded-lg whitespace-pre-wrap">
          <p className="text-sm text-zinc-500 mb-1">语法检查结果</p>
          <p className="text-sm">{result}</p>
        </div>
      )}
    </div>
  )
}

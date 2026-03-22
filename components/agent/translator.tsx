"use client"

import * as React from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { streamSSE } from "@/lib/stream"

export function Translator() {
  const [input, setInput] = React.useState("")
  const [result, setResult] = React.useState("")
  const [loading, setLoading] = React.useState(false)

  async function handleTranslate() {
    if (!input.trim()) return
    setLoading(true)
    setResult("")

    try {
      for await (const chunk of streamSSE("http://localhost:8000/api/translate", {
        word: input,
        source_lang: "en",
        target_lang: "zh",
      })) {
        setResult((prev) => prev + chunk)
      }
    } catch {
      setResult("翻译失败，请检查后端连接")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1 block">
          输入英文
        </label>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter English text..."
          onKeyDown={(e) => e.key === "Enter" && handleTranslate()}
        />
      </div>
      <Button onClick={handleTranslate} disabled={loading} className="w-full">
        {loading ? "翻译中..." : "翻译成中文"}
      </Button>
      {result && (
        <div className="p-3 bg-zinc-100 dark:bg-zinc-800 rounded-lg">
          <p className="text-sm text-zinc-500 mb-1">翻译结果</p>
          <p className="text-lg font-medium">{result}</p>
        </div>
      )}
    </div>
  )
}

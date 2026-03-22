"use client"

import ReactMarkdown from "react-markdown"

interface MarkdownRendererProps {
  content: string
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      components={{
        h1: ({ children }) => (
          <h1 className="text-lg font-bold mb-2">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-base font-semibold mb-2 mt-3">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-sm font-semibold mb-1 mt-2">{children}</h3>
        ),
        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
        ul: ({ children }) => (
          <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>
        ),
        li: ({ children }) => <li className="text-sm">{children}</li>,
        strong: ({ children }) => (
          <strong className="font-semibold">{children}</strong>
        ),
        code: ({ children }) => (
          <code className="px-1 py-0.5 bg-zinc-200 dark:bg-zinc-700 rounded text-xs">
            {children}
          </code>
        ),
        pre: ({ children }) => (
          <pre className="p-2 bg-zinc-200 dark:bg-zinc-700 rounded text-xs overflow-x-auto mb-2">
            {children}
          </pre>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-2 border-zinc-400 pl-3 italic mb-2">
            {children}
          </blockquote>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

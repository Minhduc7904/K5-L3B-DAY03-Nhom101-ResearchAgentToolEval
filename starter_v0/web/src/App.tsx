import { useEffect, useRef, useState, type KeyboardEvent } from "react"
import Markdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { ArrowUp, ChevronRight, Loader2, RotateCcw, TriangleAlert, Wrench } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Separator } from "@/components/ui/separator"
import { Textarea } from "@/components/ui/textarea"

type ToolCall = { name: string; args: Record<string, unknown>; error: boolean }

type Message =
  | { role: "user"; text: string }
  | {
      role: "assistant"
      text: string
      status: string
      toolCalls: ToolCall[]
      error?: string | null
    }

type Info = { provider: string; model: string | null; artifact_version: string }

const EXAMPLES = [
  "Tin tức AI hôm nay có gì nổi bật?",
  "Tweet mới nhất của Sam Altman là gì?",
  "Tóm tắt bài viết này hộ mình",
  "Đăng bản tin này lên Telegram giúp mình",
]

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [pending, setPending] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [info, setInfo] = useState<Info | null>(null)
  const endRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    fetch("/api/info")
      .then((r) => (r.ok ? r.json() : null))
      .then(setInfo)
      .catch(() => setInfo(null))
  }, [])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" })
  }, [messages, pending])

  async function send(text: string) {
    const message = text.trim()
    if (!message || pending) return
    setInput("")
    setMessages((m) => [...m, { role: "user", text: message }])
    setPending(true)
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message }),
      })
      if (!res.ok) throw new Error(`Server responded ${res.status}`)
      const data = await res.json()
      setSessionId(data.session_id)
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: data.assistant_text,
          status: data.status,
          toolCalls: data.tool_calls ?? [],
          error: data.error,
        },
      ])
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: "",
          status: "provider_error",
          toolCalls: [],
          error: err instanceof Error ? err.message : String(err),
        },
      ])
    } finally {
      setPending(false)
      inputRef.current?.focus()
    }
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      send(input)
    }
  }

  function reset() {
    setMessages([])
    setSessionId(null)
    setInput("")
    inputRef.current?.focus()
  }

  return (
    <div className="flex h-dvh flex-col bg-background text-foreground">
      <header className="flex h-14 shrink-0 items-center justify-between gap-2 px-4">
        <div className="flex min-w-0 items-center gap-2">
          <h1 className="truncate text-sm font-semibold">Research Agent</h1>
          {info && (
            <Badge variant="secondary" className="font-mono" title={info.artifact_version}>
              {info.artifact_version.split("+")[0]}
            </Badge>
          )}
        </div>
        <Button variant="ghost" size="sm" onClick={reset} disabled={pending || messages.length === 0}>
          <RotateCcw />
          New chat
        </Button>
      </header>
      <Separator />

      <main className="min-h-0 flex-1 overflow-y-auto">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-6" aria-live="polite">
          {messages.length === 0 ? (
            <EmptyState onPick={send} />
          ) : (
            messages.map((m, i) => <MessageView key={i} message={m} />)
          )}
          {pending && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="size-4 animate-spin" />
              Thinking…
            </div>
          )}
          <div ref={endRef} />
        </div>
      </main>

      <div className="shrink-0 px-4 pb-4">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            send(input)
          }}
          className="mx-auto flex w-full max-w-3xl items-end gap-2 rounded-xl border bg-card p-2 shadow-xs focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/50"
        >
          <Textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ask the research agent…"
            aria-label="Message"
            rows={1}
            autoFocus
            className="max-h-48 min-h-9 resize-none border-0 bg-transparent shadow-none focus-visible:ring-0 dark:bg-transparent"
          />
          <Button type="submit" size="icon" disabled={pending || !input.trim()} aria-label="Send">
            <ArrowUp />
          </Button>
        </form>
        <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-muted-foreground">
          Enter to send · Shift+Enter for a new line
          {info?.model && <span className="hidden sm:inline"> · {info.model}</span>}
        </p>
      </div>
    </div>
  )
}

function EmptyState({ onPick }: { onPick: (text: string) => void }) {
  return (
    <div className="flex flex-col items-center gap-6 py-16 text-center">
      <div className="space-y-1">
        <h2 className="text-xl font-semibold">What do you want to research?</h2>
        <p className="text-sm text-muted-foreground">News, tweets, articles and papers — try one of these.</p>
      </div>
      <div className="grid w-full max-w-xl gap-2 sm:grid-cols-2">
        {EXAMPLES.map((q) => (
          <Button
            key={q}
            variant="outline"
            className="h-auto justify-start py-2.5 text-left whitespace-normal"
            onClick={() => onPick(q)}
          >
            {q}
          </Button>
        ))}
      </div>
    </div>
  )
}

function MessageView({ message }: { message: Message }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-2xl bg-primary px-4 py-2 text-sm whitespace-pre-wrap text-primary-foreground">
          {message.text}
        </div>
      </div>
    )
  }

  if (message.status === "provider_error") {
    return (
      <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
        <TriangleAlert className="mt-0.5 size-4 shrink-0" />
        <span className="break-words">{message.error || "Something went wrong."}</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      {message.toolCalls.length > 0 && <ToolCalls calls={message.toolCalls} />}
      {message.status === "waiting_for_user" && (
        <Badge variant="outline" className="w-fit">
          Needs your input
        </Badge>
      )}
      <div className="prose-chat text-sm leading-relaxed">
        <Markdown
          remarkPlugins={[remarkGfm]}
          components={{
            a: (props) => (
              <a {...props} target="_blank" rel="noreferrer" className="underline underline-offset-4" />
            ),
          }}
        >
          {message.text}
        </Markdown>
      </div>
    </div>
  )
}

function ToolCalls({ calls }: { calls: ToolCall[] }) {
  return (
    <Collapsible className="w-fit max-w-full">
      <CollapsibleTrigger asChild>
        <Button variant="ghost" size="xs" className="group -ml-2 text-muted-foreground">
          <Wrench />
          Used {calls.length} tool{calls.length > 1 ? "s" : ""}
          <ChevronRight className="transition-transform group-data-[state=open]:rotate-90" />
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <ul className="mt-1 flex flex-col gap-2 border-l pl-3">
          {calls.map((c, i) => (
            <li key={i} className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="font-mono">
                  {c.name}
                </Badge>
                {c.error && <Badge variant="destructive">error</Badge>}
              </div>
              <pre className="overflow-x-auto rounded-md bg-muted px-2 py-1 font-mono text-xs text-muted-foreground">
                {JSON.stringify(c.args, null, 2)}
              </pre>
            </li>
          ))}
        </ul>
      </CollapsibleContent>
    </Collapsible>
  )
}

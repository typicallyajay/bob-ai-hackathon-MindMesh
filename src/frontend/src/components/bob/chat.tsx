"use client"
import { useState, useRef, useEffect } from "react";
import { useBobChat } from "@/hooks/use-api";
import { BobMessage } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, User, Send, Wrench } from "lucide-react";
import { cn } from "@/lib/utils";

export function BobChat() {
  const [messages, setMessages] = useState<BobMessage[]>([]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const { mutate, isPending } = useBobChat();

  const suggestedPrompts = [
    "Find the highest-risk incident",
    "Why is it considered malicious?",
    "Show me the attack path",
    "What if alert ALT-0003 is false?",
    "Generate the BLUF summary"
  ];

  const handleSend = (text: string) => {
    if (!text.trim() || isPending) return;
    
    const userMsg: BobMessage = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMsg]);
    setInput("");

    mutate(text, {
      onSuccess: (data) => {
        const botMsg: BobMessage = {
          role: 'assistant',
          content: data.response,
          tool_calls: data.tool_calls,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, botMsg]);
      },
      onError: () => {
        const errMsg: BobMessage = {
          role: 'assistant',
          content: "Sorry, I encountered an error connecting to the system.",
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, errMsg]);
      }
    });
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isPending]);

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden" data-tour="bob-chat">
      <div className="bg-slate-50 border-b border-slate-200 p-4 flex items-center gap-3">
        <div className="bg-indigo-100 p-2 rounded-lg">
          <Bot className="h-5 w-5 text-indigo-600" />
        </div>
        <div>
          <h2 className="font-semibold text-slate-800">Bob (Security AI)</h2>
          <p className="text-xs text-slate-500">Ask questions, investigate incidents, or run what-if scenarios.</p>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-6 mt-20">
            <div className="w-16 h-16 rounded-2xl bg-indigo-50 flex items-center justify-center">
              <Bot className="h-8 w-8 text-indigo-400" />
            </div>
            <h3 className="text-lg font-medium text-slate-700">How can I help with your investigation?</h3>
            <div className="flex flex-wrap justify-center gap-2 max-w-xl">
              {suggestedPrompts.map(prompt => (
                <button
                  key={prompt}
                  onClick={() => handleSend(prompt)}
                  className="bg-slate-50 hover:bg-indigo-50 text-sm text-slate-600 hover:text-indigo-700 px-4 py-2 rounded-full border border-slate-200 hover:border-indigo-300 transition-all duration-200"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((msg, i) => (
              <div key={i} className={cn("flex gap-4 max-w-[85%]", msg.role === 'user' ? "ml-auto flex-row-reverse" : "")}>
                <div className={cn("shrink-0 h-8 w-8 rounded-full flex items-center justify-center", 
                  msg.role === 'user' ? "bg-indigo-600" : "bg-slate-100"
                )}>
                  {msg.role === 'user' ? <User className="h-4 w-4 text-white" /> : <Bot className="h-4 w-4 text-indigo-600" />}
                </div>
                <div className="space-y-2">
                  <div className={cn("px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap",
                    msg.role === 'user' ? "bg-indigo-600 text-white rounded-tr-sm" : "bg-slate-100 border border-slate-200 text-slate-800 rounded-tl-sm"
                  )}>
                    {msg.content}
                  </div>
                  {msg.tool_calls && msg.tool_calls.length > 0 && (
                    <div className="flex flex-col gap-1">
                      {msg.tool_calls.map((tool, j) => (
                        <div key={j} className="flex items-center gap-2 text-xs text-slate-500 font-mono bg-slate-50 px-2 py-1 rounded border border-slate-200 w-fit">
                          <Wrench className="h-3 w-3" />
                          Ran tool: {tool}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isPending && (
              <div className="flex gap-4 max-w-[85%]">
                <div className="shrink-0 h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-indigo-600" />
                </div>
                <div className="bg-slate-100 border border-slate-200 px-4 py-3 rounded-2xl rounded-tl-sm text-sm text-slate-400 flex items-center gap-2">
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}
            <div ref={scrollRef} />
          </div>
        )}
      </ScrollArea>

      <div className="p-4 border-t border-slate-200 bg-slate-50">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
          className="flex gap-2"
        >
          <Input 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 bg-white border-slate-200"
            disabled={isPending}
          />
          <Button type="submit" disabled={!input.trim() || isPending} size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}

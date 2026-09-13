"use client"
import { BobChat } from "@/components/bob/chat";

export default function InvestigatePage() {
  return (
    <div className="max-w-5xl mx-auto h-full flex flex-col">
      <h1 className="text-2xl font-bold tracking-tight text-slate-100 mb-6">Investigate with Bob</h1>
      <div className="flex-1">
        <BobChat />
      </div>
    </div>
  );
}

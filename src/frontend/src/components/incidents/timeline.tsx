import { TimelineEvent } from "@/lib/types";
import { formatTimestamp, severityColor } from "@/lib/utils";

export function Timeline({ events }: { events: TimelineEvent[] }) {
  if (!events || events.length === 0) return <div className="text-slate-500 p-4">No events found.</div>;

  return (
    <div className="space-y-6">
      {events.map((event, i) => (
        <div key={i} className="flex gap-4">
          <div className="w-24 shrink-0 text-right text-xs font-mono text-slate-400 pt-1">
            {formatTimestamp(event.timestamp)}
          </div>
          <div className="flex flex-col items-center">
            <div className={`h-3 w-3 rounded-full bg-current ${severityColor(event.severity)} z-10 shadow-[0_0_10px_currentColor]`} />
            {i !== events.length - 1 && <div className="w-px flex-1 bg-border my-1" />}
          </div>
          <div className="flex-1 pb-6">
            <div className="bg-surface-raised border border-border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {event.event_type}
                </span>
                <span className="text-xs font-mono text-slate-500">
                  {event.external_id}
                </span>
              </div>
              <p className="text-sm text-slate-200 mb-3">{event.message}</p>
              
              {(event.host || event.user) && (
                <div className="flex gap-4 text-xs text-slate-400">
                  {event.host && <div><span className="font-semibold">Host:</span> {event.host}</div>}
                  {event.user && <div><span className="font-semibold">User:</span> {event.user}</div>}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

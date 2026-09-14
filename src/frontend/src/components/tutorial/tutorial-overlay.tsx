"use client"
import { useEffect, useRef, useState, useCallback } from "react";
import { TUTORIAL_STEPS } from "@/hooks/use-demo";
import { X, ChevronLeft, ChevronRight, Sparkles, GraduationCap } from "lucide-react";
import { cn } from "@/lib/utils";

interface TutorialOverlayProps {
  currentStep: number;
  totalSteps: number;
  onNext: () => void;
  onPrev: () => void;
  onClose: () => void;
}

interface CardPos {
  top?: number;
  bottom?: number;
  left?: number;
  right?: number;
  arrowSide: "top" | "bottom" | "left" | "right" | "none";
  arrowOffset: number; // px from card left/top edge
}

const CARD_W = 360;
const CARD_H = 240; // approximate
const MARGIN = 16;

function computePosition(el: HTMLElement): CardPos {
  const rect = el.getBoundingClientRect();
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  // Try to place below the element first
  const spaceBelow = vh - rect.bottom;
  const spaceAbove = rect.top;
  const spaceRight = vw - rect.right;
  const spaceLeft = rect.left;

  // Horizontal centering aligned to element
  const clampLeft = (val: number) => Math.max(MARGIN, Math.min(val, vw - CARD_W - MARGIN));
  const cardLeft = clampLeft(rect.left + rect.width / 2 - CARD_W / 2);
  const arrowOffset = rect.left + rect.width / 2 - cardLeft; // where arrow points on card

  if (spaceBelow >= CARD_H + MARGIN) {
    return {
      top: rect.bottom + 14,
      left: cardLeft,
      arrowSide: "top",
      arrowOffset,
    };
  }
  if (spaceAbove >= CARD_H + MARGIN) {
    return {
      top: rect.top - CARD_H - 14,
      left: cardLeft,
      arrowSide: "bottom",
      arrowOffset,
    };
  }
  // Place right if wide enough
  if (spaceRight >= CARD_W + MARGIN) {
    const top = Math.max(MARGIN, Math.min(rect.top + rect.height / 2 - CARD_H / 2, vh - CARD_H - MARGIN));
    return {
      top,
      left: rect.right + 14,
      arrowSide: "left",
      arrowOffset: rect.top + rect.height / 2 - top,
    };
  }
  if (spaceLeft >= CARD_W + MARGIN) {
    const top = Math.max(MARGIN, Math.min(rect.top + rect.height / 2 - CARD_H / 2, vh - CARD_H - MARGIN));
    return {
      top,
      left: rect.left - CARD_W - 14,
      arrowSide: "right",
      arrowOffset: rect.top + rect.height / 2 - top,
    };
  }
  // Fallback: centre of screen
  return {
    top: vh / 2 - CARD_H / 2,
    left: vw / 2 - CARD_W / 2,
    arrowSide: "none",
    arrowOffset: CARD_W / 2,
  };
}

// Palette per step
const STEP_COLORS = [
  { from: "#6366f1", to: "#8b5cf6", label: "indigo" },
  { from: "#f59e0b", to: "#ef4444", label: "amber-red" },
  { from: "#10b981", to: "#3b82f6", label: "emerald-blue" },
  { from: "#06b6d4", to: "#3b82f6", label: "cyan-blue" },
  { from: "#f472b6", to: "#a78bfa", label: "pink-violet" },
  { from: "#ef4444", to: "#f97316", label: "red-orange" },
  { from: "#3b82f6", to: "#06b6d4", label: "blue-cyan" },
  { from: "#a78bfa", to: "#ec4899", label: "violet-pink" },
  { from: "#10b981", to: "#a78bfa", label: "emerald-violet" },
];

export function TutorialOverlay({ currentStep, totalSteps, onNext, onPrev, onClose }: TutorialOverlayProps) {
  const step = TUTORIAL_STEPS[currentStep];
  const colors = STEP_COLORS[currentStep % STEP_COLORS.length];
  const [pos, setPos] = useState<CardPos | null>(null);
  const [key, setKey] = useState(0); // triggers re-animation
  const prevElRef = useRef<HTMLElement | null>(null);

  const reposition = useCallback(() => {
    const el = document.querySelector(step.target) as HTMLElement | null;
    if (el) {
      // Remove ring from old element
      if (prevElRef.current && prevElRef.current !== el) {
        prevElRef.current.classList.remove("tutorial-target-ring");
      }
      el.classList.add("tutorial-target-ring");
      prevElRef.current = el;
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      // Wait for scroll to settle, then compute
      setTimeout(() => {
        setPos(computePosition(el));
        setKey(k => k + 1);
      }, 350);
    } else {
      // No element found — fallback to centred card
      setPos({
        top: window.innerHeight / 2 - CARD_H / 2,
        left: window.innerWidth / 2 - CARD_W / 2,
        arrowSide: "none",
        arrowOffset: CARD_W / 2,
      });
      setKey(k => k + 1);
    }
  }, [step.target]);

  useEffect(() => {
    reposition();
    window.addEventListener("resize", reposition);
    return () => {
      window.removeEventListener("resize", reposition);
      // Clean up ring on unmount
      if (prevElRef.current) {
        prevElRef.current.classList.remove("tutorial-target-ring");
      }
    };
  }, [reposition]);

  // Clean up ring when tutorial closes
  useEffect(() => {
    return () => {
      if (prevElRef.current) prevElRef.current.classList.remove("tutorial-target-ring");
    };
  }, []);

  const progress = ((currentStep + 1) / totalSteps) * 100;

  return (
    <>
      {/* Dim backdrop — pointer-events blocked so user can still see UI */}
      <div
        className="fixed inset-0 z-[9995] pointer-events-none"
        style={{ background: "rgba(2,6,23,0.72)", backdropFilter: "blur(1.5px)" }}
      />

      {/* Click-through shield so backdrop doesn't block buttons */}
      <div
        className="fixed inset-0 z-[9996]"
        onClick={onClose}
        style={{ cursor: "default" }}
      />

      {/* Floating card */}
      {pos && (
        <div
          key={key}
          className="fixed z-[9999] animate-pop-in pointer-events-auto"
          style={{
            top: pos.top,
            left: pos.left,
            width: CARD_W,
          }}
          onClick={e => e.stopPropagation()}
        >
          {/* Arrow pointing to element */}
          {pos.arrowSide === "top" && (
            <div
              className="absolute -top-2.5 w-0 h-0"
              style={{
                left: Math.max(12, Math.min(pos.arrowOffset - 10, CARD_W - 24)),
                borderLeft: "10px solid transparent",
                borderRight: "10px solid transparent",
                borderBottom: `10px solid ${colors.from}`,
                filter: "drop-shadow(0 -2px 4px rgba(0,0,0,0.4))",
              }}
            />
          )}
          {pos.arrowSide === "bottom" && (
            <div
              className="absolute -bottom-2.5 w-0 h-0"
              style={{
                left: Math.max(12, Math.min(pos.arrowOffset - 10, CARD_W - 24)),
                borderLeft: "10px solid transparent",
                borderRight: "10px solid transparent",
                borderTop: `10px solid ${colors.from}`,
                filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.4))",
              }}
            />
          )}
          {pos.arrowSide === "left" && (
            <div
              className="absolute -left-2.5 w-0 h-0"
              style={{
                top: Math.max(12, Math.min(pos.arrowOffset - 10, CARD_H - 24)),
                borderTop: "10px solid transparent",
                borderBottom: "10px solid transparent",
                borderRight: `10px solid ${colors.from}`,
                filter: "drop-shadow(-2px 0 4px rgba(0,0,0,0.4))",
              }}
            />
          )}
          {pos.arrowSide === "right" && (
            <div
              className="absolute -right-2.5 w-0 h-0"
              style={{
                top: Math.max(12, Math.min(pos.arrowOffset - 10, CARD_H - 24)),
                borderTop: "10px solid transparent",
                borderBottom: "10px solid transparent",
                borderLeft: `10px solid ${colors.from}`,
                filter: "drop-shadow(2px 0 4px rgba(0,0,0,0.4))",
              }}
            />
          )}

          {/* Card body */}
          <div
            className="rounded-2xl overflow-hidden shadow-2xl"
            style={{
              background: "#0f172a",
              border: `1.5px solid ${colors.from}44`,
              boxShadow: `0 0 40px 0 ${colors.from}22, 0 20px 60px rgba(0,0,0,0.6)`,
            }}
          >
            {/* Colourful header strip */}
            <div
              className="px-5 pt-4 pb-3 relative overflow-hidden"
              style={{
                background: `linear-gradient(135deg, ${colors.from}22 0%, ${colors.to}18 100%)`,
                borderBottom: `1px solid ${colors.from}30`,
              }}
            >
              {/* Floating orb background */}
              <div
                className="absolute -top-6 -right-6 w-20 h-20 rounded-full blur-2xl animate-float-slow"
                style={{ background: `${colors.to}30` }}
              />
              <div className="flex items-center justify-between relative">
                <div className="flex items-center gap-2.5">
                  <div
                    className="w-8 h-8 rounded-xl flex items-center justify-center"
                    style={{ background: `linear-gradient(135deg, ${colors.from}, ${colors.to})` }}
                  >
                    <GraduationCap className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <div className="text-[10px] font-semibold uppercase tracking-widest" style={{ color: colors.from }}>
                      Step {currentStep + 1} / {totalSteps}
                    </div>
                    <div className="text-xs text-slate-400">Interactive Tutorial</div>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="w-7 h-7 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-slate-400 hover:text-white transition-all"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>

            <div className="px-5 py-4">
              {/* Title */}
              <h3 className="text-base font-bold text-white mb-2 leading-tight">{step.title}</h3>
              {/* Description */}
              <p className="text-sm text-slate-300 leading-relaxed">{step.description}</p>

              {/* Progress bar */}
              <div className="mt-4 mb-3 h-1 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${progress}%`,
                    background: `linear-gradient(90deg, ${colors.from}, ${colors.to})`,
                  }}
                />
              </div>

              {/* Step dots */}
              <div className="flex items-center gap-1 mb-4">
                {Array.from({ length: totalSteps }).map((_, i) => (
                  <div
                    key={i}
                    className="transition-all duration-300 rounded-full"
                    style={{
                      width: i === currentStep ? 16 : 6,
                      height: 6,
                      background: i < currentStep
                        ? colors.from
                        : i === currentStep
                        ? `linear-gradient(90deg, ${colors.from}, ${colors.to})`
                        : "#1e293b",
                    }}
                  />
                ))}
              </div>

              {/* Controls */}
              <div className="flex items-center gap-2">
                <button
                  onClick={onPrev}
                  disabled={currentStep === 0}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-white/5 transition-all disabled:opacity-25 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Back
                </button>

                <button
                  onClick={onClose}
                  className="flex-1 text-center text-xs text-slate-600 hover:text-slate-400 transition-colors"
                >
                  skip
                </button>

                <button
                  onClick={onNext}
                  className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-sm font-semibold text-white transition-all hover:scale-105 active:scale-95"
                  style={{
                    background: `linear-gradient(135deg, ${colors.from}, ${colors.to})`,
                    boxShadow: `0 4px 14px ${colors.from}50`,
                  }}
                >
                  {currentStep < totalSteps - 1 ? (
                    <>Next <ChevronRight className="h-4 w-4" /></>
                  ) : (
                    <>Finish! <Sparkles className="h-4 w-4" /></>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

"use client"
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";
import { useDemo } from "@/hooks/use-demo";
import { TutorialOverlay } from "@/components/tutorial/tutorial-overlay";
import { DemoModeBar } from "@/components/demo/demo-mode-bar";
import { cn } from "@/lib/utils";

export function AppShell({ children }: { children: React.ReactNode }) {
  const {
    tutorialActive,
    currentStep,
    totalSteps,
    nextStep,
    prevStep,
    closeTutorial,
    startTutorial,
    demoMode,
    toggleDemoMode,
  } = useDemo();

  return (
    <div className={cn("min-h-screen bg-[#0c101d] flex text-slate-100", demoMode && "pt-7")}>
      {demoMode && (
        <DemoModeBar
          demoMode={demoMode}
          onToggle={toggleDemoMode}
          onStartTutorial={startTutorial}
        />
      )}

      <Sidebar onStartTutorial={startTutorial} demoMode={demoMode} onToggleDemoMode={toggleDemoMode} />

      <div className="flex-1 ml-60 flex flex-col min-h-screen">
        <Topbar />
        <main className="flex-1 p-6 overflow-x-hidden">
          {children}
        </main>
      </div>

      {tutorialActive && (
        <TutorialOverlay
          currentStep={currentStep}
          totalSteps={totalSteps}
          onNext={nextStep}
          onPrev={prevStep}
          onClose={closeTutorial}
        />
      )}
    </div>
  );
}

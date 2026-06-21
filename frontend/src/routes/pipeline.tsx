import { createFileRoute } from "@tanstack/react-router";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { pipelineSteps } from "@/lib/mock-data";
import { StatusDot, SectionTitle } from "@/components/ui-bits";
import { ArrowRight, Clock } from "lucide-react";

export const Route = createFileRoute("/pipeline")({
  head: () => ({ meta: [{ title: "Pipeline Multiagente — NVIDIA Toph" }] }),
  component: PipelinePage,
});

function statusLabel(s: string) {
  return { completed: "Concluído", running: "Em execução", "needs evidence": "Aguarda evidência", blocked: "Bloqueado", ready: "Pronto" }[s] ?? s;
}

function PipelinePage() {
  return (
    <div className="mx-auto w-full max-w-7xl space-y-5 p-4 md:p-6">
      <div>
        <h1 className="text-lg font-semibold text-foreground">Pipeline Multiagente</h1>
        <p className="text-xs text-muted-foreground">Consulta → Search Planner → Scraper → Extractor → Validator → Classifier → NVIDIA RAG → Recommendation → Briefing</p>
      </div>

      {/* Flow strip */}
      <Card className="overflow-x-auto p-4">
        <div className="flex min-w-max items-center gap-2">
          <Badge className="bg-foreground text-background">Consulta</Badge>
          {pipelineSteps.map((s, i) => (
            <div key={s.name} className="flex items-center gap-2">
              <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
              <div className="flex items-center gap-1.5 rounded-md border border-border bg-card px-2.5 py-1.5">
                <StatusDot status={s.status} />
                <span className="text-xs font-medium text-foreground">{i + 1}. {s.name.replace(" Agent", "")}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <div className="grid gap-3 md:grid-cols-2">
        {pipelineSteps.map((s, i) => (
          <Card key={s.name} className="p-4">
            <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="grid h-6 w-6 shrink-0 place-items-center rounded-md bg-muted text-[11px] font-semibold text-foreground">{i + 1}</span>
                  <h3 className="truncate text-sm font-semibold text-foreground">{s.name}</h3>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">{s.desc}</p>
              </div>
              <Badge variant="outline" className="gap-1 text-[10px]">
                <StatusDot status={s.status} /> {statusLabel(s.status)}
              </Badge>
            </div>
            <div className="mt-3 rounded-md bg-muted/50 p-2.5">
              <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">Output</p>
              <p className="mt-0.5 text-xs text-foreground">{s.output}</p>
            </div>
            <div className="mt-2 flex items-center gap-1 text-[11px] text-muted-foreground">
              <Clock className="h-3 w-3" /> {s.lastRun}
            </div>
          </Card>
        ))}
      </div>

      <Card className="p-4">
        <SectionTitle title="Regras do pipeline" desc="Garantias operacionais aplicadas em cada execução" />
        <ul className="grid gap-1.5 text-xs text-foreground sm:grid-cols-2">
          <li>• Coleta restrita a informações públicas, respeitando robots.txt.</li>
          <li>• URL e trecho original sempre preservados como evidência.</li>
          <li>• Classificação AI-Native / AI-Enabled / Non-AI com critérios explícitos.</li>
          <li>• Recomendação NVIDIA exige ao menos uma evidência validada.</li>
          <li>• Base NVIDIA consultada via RAG antes de toda recomendação.</li>
          <li>• Briefing executivo agrega justificativa técnica e de negócio.</li>
        </ul>
      </Card>
    </div>
  );
}

import { createFileRoute } from "@tanstack/react-router";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState } from "react";
import { startups } from "@/lib/mock-data";
import { MaturityBadge, ScoreBar, SectionTitle } from "@/components/ui-bits";
import { useHealth } from "@/lib/hooks/use-health";
import { ApiErrorDisplay } from "@/components/api-error-display";
import { Copy, Download, Save, Database, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/briefing")({
  head: () => ({ meta: [{ title: "Briefing Executivo — NVIDIA Toph" }] }),
  component: BriefingPage,
});

function BriefingPage() {
  const [id, setId] = useState(startups[0].id);
  const { data: health, error: healthError, refetch: retryHealth } = useHealth();
  const apiOk = health?.status === "ok";
  const s = startups.find((x) => x.id === id)!;

  const summary =
    `Briefing — ${s.name}\nSetor: ${s.sector} | Região: ${s.region} | Fundada em ${s.foundedYear}\nClassificação: ${s.maturity}\nRadar: ${s.radarScore} | NVIDIA fit: ${s.nvidiaFit} | Evidence: ${s.evidenceConfidence}\n\n${s.executiveSummary}\n\nRecomendações: ${s.recommendations.map((r) => r.tech).join(", ")}`;

  if (healthError) {
    return (
      <div className="mx-auto w-full max-w-5xl p-4 md:p-6">
        <ApiErrorDisplay error={healthError as any} onRetry={() => retryHealth()} />
      </div>
    );
  }

  if (!health) {
    return (
      <div className="mx-auto w-full max-w-5xl p-4 md:p-6">
        <Card className="p-6">
          <div className="space-y-3">
            <Skeleton className="h-6 w-64" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-40 w-full" />
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-5xl space-y-5 p-4 md:p-6">
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 sm:flex sm:flex-wrap sm:justify-between">
        <div className="min-w-0">
          <h1 className="truncate text-lg font-semibold text-foreground">Briefing Executivo</h1>
          <p className="text-xs text-muted-foreground">Documento de abordagem comercial e técnica para NVIDIA Startups & VCs.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline" className={`gap-1 text-[10px] ${apiOk ? "border-green-500/30 bg-green-500/5 text-green-600" : "border-primary/30 bg-primary/5 text-primary"}`}>
            {apiOk ? <><CheckCircle2 className="h-3 w-3" /> API ativa</> : <><Database className="h-3 w-3" /> Demo data</>}
          </Badge>
          <Select value={id} onValueChange={setId}>
            <SelectTrigger className="h-9 w-[220px]"><SelectValue /></SelectTrigger>
            <SelectContent>
              {startups.map((x) => <SelectItem key={x.id} value={x.id}>{x.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
      </div>

      <Card className="p-6">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-xl font-semibold text-foreground">{s.name}</h2>
          <MaturityBadge value={s.maturity} />
        </div>
        <p className="mt-1 text-sm text-muted-foreground">{s.sector} · {s.region} · {s.foundedYear} · {s.fundingRange}</p>

        <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-4">
          <div><p className="text-[10px] uppercase text-muted-foreground">Radar</p><ScoreBar value={s.radarScore} /></div>
          <div><p className="text-[10px] uppercase text-muted-foreground">Evidence</p><ScoreBar value={s.evidenceConfidence} /></div>
          <div><p className="text-[10px] uppercase text-muted-foreground">NVIDIA fit</p><ScoreBar value={s.nvidiaFit} /></div>
          <div><p className="text-[10px] uppercase text-muted-foreground">Contato</p><ScoreBar value={s.contactPriority} /></div>
        </div>

        <div className="my-6 h-px bg-border" />

        <SectionTitle title="1. Resumo" />
        <p className="text-sm leading-relaxed text-foreground">{s.executiveSummary}</p>

        <div className="mt-5">
          <SectionTitle title="2. Diagnóstico AI-native" />
          <p className="text-sm leading-relaxed text-foreground">{s.maturityJustification}</p>
        </div>

        <div className="mt-5">
          <SectionTitle title="3. Evidências principais" />
          <ul className="space-y-1.5">
            {s.evidences.slice(0, 4).map((e, i) => (
              <li key={i} className="text-xs text-foreground">
                <span className="font-medium">E{i + 1}</span> — <span className="text-muted-foreground">[{e.type}]</span> "{e.snippet}" — <code className="text-[11px] text-primary">{e.url}</code>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-5">
          <SectionTitle title="4. Gaps identificados" />
          <ul className="grid gap-1.5 sm:grid-cols-2">
            {s.gaps.map((g) => (
              <li key={g.name} className="text-xs text-foreground">
                <span className="font-medium">{g.name}</span> <span className="text-muted-foreground">— {g.description}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-5">
          <SectionTitle title="5. Recomendações NVIDIA" />
          <ul className="space-y-2">
            {s.recommendations.map((r, i) => (
              <li key={i} className="rounded-md border border-border p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-semibold text-foreground">{r.tech}</span>
                  <Badge variant="outline" className="text-[10px]">Prioridade {r.priority}</Badge>
                  <Badge variant="outline" className="text-[10px]">Complexidade {r.complexity}</Badge>
                </div>
                <p className="mt-1 text-xs text-foreground"><span className="font-medium">Por quê (técnico):</span> {r.technicalRationale}</p>
                <p className="text-xs text-foreground"><span className="font-medium">Por quê (negócio):</span> {r.businessRationale}</p>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-5">
          <SectionTitle title="6. Plano de abordagem" />
          <ol className="list-decimal space-y-1 pl-5 text-sm text-foreground">
            <li>Contato inicial via NVIDIA Inception com founder técnico.</li>
            <li>Discovery técnica de 60 min com squad de ML/Platform.</li>
            <li>POC focado em {s.recommendations[0]?.tech} validando {s.gaps[0]?.name.toLowerCase()}.</li>
            <li>Apresentação executiva com ROI estimado em 4 semanas.</li>
            <li>Onboarding em AI Enterprise / Inception conforme estágio.</li>
          </ol>
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          <Button className="gap-1.5" onClick={() => toast.success("PDF mockado pronto para download.")}>
            <Download className="h-4 w-4" /> Exportar PDF
          </Button>
          <Button variant="outline" className="gap-1.5" onClick={() => { navigator.clipboard?.writeText(summary); toast.success("Resumo copiado."); }}>
            <Copy className="h-4 w-4" /> Copiar resumo
          </Button>
          <Button variant="outline" className="gap-1.5" onClick={() => toast.success("Análise salva no workspace.")}>
            <Save className="h-4 w-4" /> Salvar análise
          </Button>
        </div>
      </Card>
    </div>
  );
}

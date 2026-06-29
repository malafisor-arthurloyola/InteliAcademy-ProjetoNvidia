import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Copy, Database, Download, Save } from "lucide-react";
import { toast } from "sonner";
import { ApiErrorDisplay } from "@/components/api-error-display";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MaturityBadge, ScoreBar, SectionTitle } from "@/components/ui-bits";
import type { ApiError } from "@/lib/api";
import {
  findLatestRunForStartup,
  formatDate,
  maturityLabel,
  parseListField,
  scoreFromConfidence,
  unavailable,
} from "@/lib/api-derived";
import { useHealth } from "@/lib/hooks/use-health";
import { useRun, useRuns } from "@/lib/hooks/use-runs";
import { useRunClaims, useRunSources } from "@/lib/hooks/use-sources";
import { useStartups } from "@/lib/hooks/use-startups";

export const Route = createFileRoute("/briefing")({
  head: () => ({ meta: [{ title: "Briefing Executivo - NVIDIA Toph" }] }),
  component: BriefingPage,
});

function BriefingPage() {
  const [selectedId, setSelectedId] = useState<string>("");
  const healthQuery = useHealth();
  const startupsQuery = useStartups();
  const runsQuery = useRuns();
  const startups = useMemo(
    () => startupsQuery.data ?? [],
    [startupsQuery.data],
  );

  useEffect(() => {
    if (!selectedId && startups[0]) setSelectedId(startups[0].id);
  }, [selectedId, startups]);

  const startup =
    startups.find((item) => item.id === selectedId) ?? startups[0];
  const latestRun = useMemo(
    () => findLatestRunForStartup(startup, runsQuery.data ?? []),
    [startup, runsQuery.data],
  );
  const runQuery = useRun(latestRun?.id ?? null);
  const sourcesQuery = useRunSources(latestRun?.id ?? null);
  const claimsQuery = useRunClaims(latestRun?.id ?? null);

  const error =
    healthQuery.error ??
    startupsQuery.error ??
    runsQuery.error ??
    runQuery.error ??
    sourcesQuery.error ??
    claimsQuery.error;
  if (error) {
    return (
      <div className="mx-auto w-full max-w-5xl p-4 md:p-6">
        <ApiErrorDisplay
          error={error as unknown as ApiError}
          onRetry={() => {
            void healthQuery.refetch();
            void startupsQuery.refetch();
            void runsQuery.refetch();
            void runQuery.refetch();
            void sourcesQuery.refetch();
            void claimsQuery.refetch();
          }}
        />
      </div>
    );
  }

  if (healthQuery.isLoading || startupsQuery.isLoading || runsQuery.isLoading) {
    return <BriefingSkeleton />;
  }

  if (startups.length === 0 || !startup) {
    return (
      <div className="mx-auto w-full max-w-5xl p-4 md:p-6">
        <Card className="flex min-h-64 flex-col items-center justify-center gap-2 p-6 text-center">
          <Database className="h-5 w-5 text-muted-foreground" />
          <p className="text-sm font-medium text-foreground">
            Nenhuma startup persistida ainda
          </p>
          <p className="max-w-md text-xs text-muted-foreground">
            Execute uma analise na tela Pipeline para gerar startups, fontes e
            recomendacoes reais.
          </p>
        </Card>
      </div>
    );
  }

  const recommendations = runQuery.data?.recommendations ?? [];
  const claims = claimsQuery.data ?? [];
  const sources = sourcesQuery.data ?? [];
  const maturity = maturityLabel(startup.classification_label);
  const confidenceScore = scoreFromConfidence(
    startup.classification_confidence,
  );
  const evidenceScore =
    claims.length > 0
      ? Math.round(
          (claims.reduce((sum, claim) => sum + claim.confidence, 0) /
            claims.length) *
            100,
        )
      : 0;
  const nvidiaFit = Math.min(100, recommendations.length * 25);
  const contactScore = latestRun ? 60 : 0;
  const technologies = parseListField(startup.cited_technologies);
  const summary = buildSummary({
    startupName: startup.name,
    sector: startup.sector,
    maturity: startup.classification_label,
    confidenceScore,
    recommendations: recommendations.map((rec) => rec.technology),
  });
  const apiOk = healthQuery.data?.status === "ok";

  return (
    <div className="mx-auto w-full max-w-5xl space-y-5 p-4 md:p-6">
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 sm:flex sm:flex-wrap sm:justify-between">
        <div className="min-w-0">
          <h1 className="truncate text-lg font-semibold text-foreground">
            Briefing Executivo
          </h1>
          <p className="text-xs text-muted-foreground">
            Documento montado com dados reais da FastAPI local.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge
            variant="outline"
            className={`gap-1 text-[10px] ${apiOk ? "border-green-500/30 bg-green-500/5 text-green-600" : "border-primary/30 bg-primary/5 text-primary"}`}
          >
            {apiOk ? (
              <>
                <CheckCircle2 className="h-3 w-3" /> API ativa
              </>
            ) : (
              <>
                <Database className="h-3 w-3" /> API indisponivel
              </>
            )}
          </Badge>
          <Select value={startup.id} onValueChange={setSelectedId}>
            <SelectTrigger className="h-9 w-[240px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {startups.map((item) => (
                <SelectItem key={item.id} value={item.id}>
                  {item.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <Card className="p-6">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-xl font-semibold text-foreground">
            {startup.name}
          </h2>
          {maturity ? (
            <MaturityBadge value={maturity} />
          ) : (
            <Badge variant="outline">Nao classificada</Badge>
          )}
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          {unavailable(startup.sector)} - {unavailable(startup.product)} -
          Funding: {unavailable(startup.funding)}
        </p>
        <p className="mt-1 text-[11px] text-muted-foreground">
          Run associado:{" "}
          {latestRun
            ? `#${latestRun.id} - ${formatDate(latestRun.created_at)}`
            : "Nenhum run associado por startup_id/nome/query"}
        </p>

        <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-4">
          <ScorePanel label="Radar" value={confidenceScore} />
          <ScorePanel label="Evidence" value={evidenceScore} />
          <ScorePanel label="NVIDIA fit" value={nvidiaFit} />
          <ScorePanel label="Contato" value={contactScore} />
        </div>

        <div className="my-6 h-px bg-border" />

        <SectionTitle title="1. Resumo" />
        <p className="text-sm leading-relaxed text-foreground">
          {startup.description ??
            startup.ai_usage_summary ??
            "Resumo ainda nao disponivel na API."}
        </p>

        <div className="mt-5">
          <SectionTitle title="2. Diagnostico AI-native" />
          <p className="text-sm leading-relaxed text-foreground">
            {startup.classification_rationale ??
              "Classificacao ainda nao disponivel."}
          </p>
        </div>

        <div className="mt-5">
          <SectionTitle title="3. Evidencias principais" />
          {claims.length === 0 ? (
            <EmptyText text="Nenhuma claim real associada ao ultimo run." />
          ) : (
            <ul className="space-y-1.5">
              {claims.slice(0, 5).map((claim, index) => (
                <li key={claim.id} className="text-xs text-foreground">
                  <span className="font-medium">E{index + 1}</span> -{" "}
                  <span className="text-muted-foreground">
                    [{claim.claim_type}]
                  </span>{" "}
                  {claim.text}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="mt-5">
          <SectionTitle title="4. Sinais tecnicos" />
          <div className="flex flex-wrap gap-1.5">
            {technologies.length === 0 ? (
              <Badge variant="outline">Nao disponivel</Badge>
            ) : (
              technologies.map((tech) => (
                <Badge key={tech} variant="outline" className="text-[10px]">
                  {tech}
                </Badge>
              ))
            )}
          </div>
        </div>

        <div className="mt-5">
          <SectionTitle title="5. Recomendacoes NVIDIA" />
          {recommendations.length === 0 ? (
            <EmptyText text="Nenhuma recomendacao real persistida para este run." />
          ) : (
            <ul className="space-y-2">
              {recommendations.map((rec) => (
                <li
                  key={rec.id}
                  className="rounded-md border border-border p-3"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-semibold text-foreground">
                      {rec.technology}
                    </span>
                    <Badge variant="outline" className="text-[10px]">
                      Prioridade {rec.priority}
                    </Badge>
                    <Badge variant="outline" className="text-[10px]">
                      Complexidade {rec.implementation_complexity}
                    </Badge>
                  </div>
                  <p className="mt-1 text-xs text-foreground">
                    <span className="font-medium">Tecnico:</span>{" "}
                    {rec.technical_justification}
                  </p>
                  <p className="text-xs text-foreground">
                    <span className="font-medium">Negocio:</span>{" "}
                    {rec.business_justification}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="mt-5">
          <SectionTitle title="6. Fontes disponiveis" />
          {sources.length === 0 ? (
            <EmptyText text="Nenhuma fonte associada ao ultimo run." />
          ) : (
            <p className="text-xs text-muted-foreground">
              {sources.length} fonte(s) reais associadas. Primeira fonte:{" "}
              {sources[0].domain}
            </p>
          )}
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          <Button
            className="gap-1.5"
            onClick={() => toast.success("Exportacao PDF ainda mockada.")}
          >
            <Download className="h-4 w-4" /> Exportar PDF
          </Button>
          <Button
            variant="outline"
            className="gap-1.5"
            onClick={() => {
              void navigator.clipboard?.writeText(summary);
              toast.success("Resumo copiado.");
            }}
          >
            <Copy className="h-4 w-4" /> Copiar resumo
          </Button>
          <Button
            variant="outline"
            className="gap-1.5"
            onClick={() => toast.success("Analise marcada localmente.")}
          >
            <Save className="h-4 w-4" /> Salvar analise
          </Button>
        </div>
      </Card>
    </div>
  );
}

function ScorePanel({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <p className="text-[10px] uppercase text-muted-foreground">{label}</p>
      <ScoreBar value={value} />
    </div>
  );
}

function BriefingSkeleton() {
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

function EmptyText({ text }: { text: string }) {
  return (
    <div className="rounded-md border border-dashed border-border p-4 text-xs text-muted-foreground">
      {text}
    </div>
  );
}

function buildSummary(input: {
  startupName: string;
  sector: string | null;
  maturity: string | null;
  confidenceScore: number;
  recommendations: string[];
}) {
  return `Briefing - ${input.startupName}\nSetor: ${input.sector ?? "Nao disponivel"}\nClassificacao: ${input.maturity ?? "Nao classificada"}\nConfianca: ${input.confidenceScore}\nRecomendacoes: ${input.recommendations.join(", ") || "Nenhuma recomendacao persistida"}`;
}

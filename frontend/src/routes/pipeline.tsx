import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { useSubmitRun, useRun } from "@/lib/hooks/use-runs";
import { PipelineStatus, type PipelineStepData, type StepStatus } from "@/components/pipeline-status";
import { ApiErrorDisplay } from "@/components/api-error-display";
import { Sparkles } from "lucide-react";

export const Route = createFileRoute("/pipeline")({
  head: () => ({ meta: [{ title: "Pipeline Multiagente - NVIDIA Toph" }] }),
  component: PipelinePage,
});

const STEP_KEYS = [
  "search_planner",
  "scraper",
  "extractor",
  "validator",
  "classifier",
  "nvidia_rag",
  "recommendation",
  "briefing",
];

function formatDuration(start: number | null, end: number | null): string {
  if (!start) return "0s";
  const s = Math.floor(((end ?? Date.now()) - start) / 1000);
  const m = Math.floor(s / 60);
  return m > 0 ? `${m}m ${s % 60}s` : `${s}s`;
}

function mapStepStatus(status: string | undefined): StepStatus {
  if (status === "running") return "running";
  if (status === "completed") return "done";
  if (status === "failed") return "error";
  return "idle";
}

function elapsedFromIso(startedAt: string | null, completedAt: string | null): number | undefined {
  if (!startedAt) return undefined;
  const start = Date.parse(startedAt);
  if (Number.isNaN(start)) return undefined;
  const end = completedAt ? Date.parse(completedAt) : Date.now();
  if (Number.isNaN(end)) return undefined;
  return Math.max(0, Math.floor((end - start) / 1000));
}

function emptySteps(activeFirstStep: boolean): PipelineStepData[] {
  return STEP_KEYS.map((key, index) => ({
    key,
    status: activeFirstStep && index === 0 ? "running" : "idle",
  }));
}

function buildStepData(runDetail: ReturnType<typeof useRun>["data"], isSubmitting: boolean): PipelineStepData[] {
  if (!runDetail?.steps?.length) {
    return emptySteps(isSubmitting);
  }

  const byKey = new Map(runDetail.steps.map((step) => [step.step_key, step]));
  return STEP_KEYS.map((key) => {
    const step = byKey.get(key);
    return {
      key,
      status: mapStepStatus(step?.status),
      elapsedSeconds: elapsedFromIso(step?.started_at ?? null, step?.completed_at ?? null),
      errorMessage: step?.error_message ?? undefined,
    };
  });
}

function PipelinePage() {
  const [query, setQuery] = useState("");
  const [runId, setRunId] = useState<number | null>(null);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval>>();

  const { mutate: execute, isPending: isSubmitting, error: submitError } = useSubmitRun();
  const { data: runDetail, isLoading: isPolling, error: pollError } = useRun(runId);

  const isRunning = isSubmitting || runDetail?.status === "pending" || runDetail?.status === "running";
  const hasResult = runDetail?.status === "completed";
  const hasError = runDetail?.status === "failed";

  useEffect(() => {
    if (isRunning) {
      timerRef.current = setInterval(() => {
        setElapsed(Math.floor((Date.now() - (startedAt ?? Date.now())) / 1000));
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }
    return () => clearInterval(timerRef.current);
  }, [isRunning, startedAt]);

  const steps = buildStepData(runDetail, isSubmitting || isPolling);
  const displayError = submitError ?? pollError ?? null;

  const handleSubmit = () => {
    if (!query.trim()) {
      toast.error("Digite uma consulta para executar o pipeline.");
      return;
    }
    setRunId(null);
    setStartedAt(Date.now());
    setElapsed(0);
    execute(query.trim(), {
      onSuccess: (res) => {
        setRunId(res.run_id);
        toast.success("Pipeline iniciado. Acompanhando progresso em tempo real.");
      },
      onError: (err: unknown) => {
        const msg = err && typeof err === "object" && "message" in err
          ? String((err as { message: string }).message)
          : "Erro ao iniciar pipeline";
        toast.error(msg);
      },
    });
  };

  return (
    <div className="mx-auto w-full max-w-7xl space-y-5 p-4 md:p-6">
      <div>
        <h1 className="text-lg font-semibold text-foreground">Pipeline Multiagente</h1>
        <p className="text-xs text-muted-foreground">
          Executa busca, coleta, extracao, validacao, classificacao, RAG NVIDIA, recomendacao e briefing.
        </p>
      </div>

      <Card className="p-4">
        <div className="flex flex-col gap-3 sm:flex-row">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            placeholder='Ex: "startups brasileiras de IA para saude", "agentes LLM em fintechs"...'
            className="h-10 flex-1"
            disabled={isRunning}
          />
          <Button
            size="default"
            className="h-10 gap-1.5"
            onClick={handleSubmit}
            disabled={isRunning || !query.trim()}
          >
            {isRunning ? (
              <>Processando...</>
            ) : (
              <><Sparkles className="h-4 w-4" /> Executar Pipeline</>
            )}
          </Button>
        </div>
      </Card>

      {(isRunning || hasResult || hasError) && (
        <Card className="p-4">
          <PipelineStatus
            steps={steps}
            elapsedSeconds={elapsed}
            overallStatus={hasResult ? "completed" : hasError ? "error" : "pending"}
          />
        </Card>
      )}

      {displayError && !isRunning && (
        <ApiErrorDisplay
          error={
            (displayError && typeof displayError === "object" && "endpoint" in displayError)
              ? displayError as { endpoint: string; status: number; message: string }
              : { endpoint: runId ? `GET /runs/${runId}` : "POST /runs", status: 0, message: String(displayError) }
          }
          onRetry={handleSubmit}
        />
      )}

      {hasError && !displayError && (
        <Card className="p-4">
          <p className="text-sm text-destructive">
            Pipeline falhou. Veja a etapa marcada em vermelho ou os logs do backend para o detalhe completo.
          </p>
        </Card>
      )}

      {hasResult && runDetail && (
        <div className="space-y-4">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold text-foreground">Pipeline concluido</h2>
                <p className="text-xs text-muted-foreground">
                  Consulta: "{runDetail.query}" - Duracao: {formatDuration(startedAt, Date.now())}
                </p>
              </div>
              <Badge variant="outline" className="gap-1.5 border-green-500/30 bg-green-500/10 text-green-600">
                Run #{runDetail.id}
              </Badge>
            </div>
          </Card>

          {runDetail.recommendations.length > 0 && (
            <Card className="p-4">
              <h3 className="mb-3 text-sm font-semibold text-foreground">
                Recomendacoes NVIDIA ({runDetail.recommendations.length})
              </h3>
              <div className="space-y-2">
                {runDetail.recommendations.map((r) => (
                  <div key={r.id} className="rounded-md border border-border p-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-medium text-foreground">{r.technology}</span>
                      <Badge variant="outline" className="text-[10px]">
                        Prioridade {r.priority}
                      </Badge>
                      <Badge variant="outline" className="text-[10px]">
                        Complexidade {r.implementation_complexity}
                      </Badge>
                    </div>
                    <p className="mt-1 text-xs text-foreground">
                      <span className="font-medium">Gap alvo:</span> {r.target_gap}
                    </p>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      <span className="font-medium">Tecnico:</span> {r.technical_justification}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      <span className="font-medium">Negocio:</span> {r.business_justification}
                    </p>
                    <p className="mt-1 text-[11px] text-primary">
                      Proxima acao: {r.suggested_next_action}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {runDetail.recommendations.length === 0 && (
            <Card className="p-4">
              <p className="text-sm text-muted-foreground">
                Pipeline executou mas nao gerou recomendacoes. Verifique evidencia minima, classificacao e logs do backend.
              </p>
            </Card>
          )}

          <div className="flex justify-end">
            <Button variant="outline" size="sm" className="gap-1.5" onClick={handleSubmit}>
              <Sparkles className="h-3.5 w-3.5" /> Executar novamente
            </Button>
          </div>
        </div>
      )}

      <Card className="p-4">
        <h3 className="mb-2 text-sm font-semibold text-foreground">Regras do pipeline</h3>
        <ul className="grid gap-1.5 text-xs text-foreground sm:grid-cols-2">
          <li>- Coleta restrita a informacoes publicas, respeitando robots.txt.</li>
          <li>- URL e trecho original sempre preservados como evidencia.</li>
          <li>- Classificacao AI-Native / AI-Enabled / Non-AI com criterios explicitos.</li>
          <li>- Recomendacao NVIDIA exige evidencia validada.</li>
          <li>- Base NVIDIA consultada via RAG antes de toda recomendacao.</li>
          <li>- Briefing executivo agrega justificativa tecnica e de negocio.</li>
        </ul>
      </Card>
    </div>
  );
}
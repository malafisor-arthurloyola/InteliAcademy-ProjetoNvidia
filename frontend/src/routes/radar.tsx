import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Radio, History, Clock, CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { Checkbox } from "@/components/ui/checkbox";
import { ApiErrorDisplay } from "@/components/api-error-display";
import { useDiscover, useBatch, useBatches } from "@/lib/hooks/use-batch";
import type { DiscoverResponse } from "@/lib/api";

export const Route = createFileRoute("/radar")({
  head: () => ({ meta: [{ title: "Radar — NVIDIA Toph" }] }),
  component: RadarPage,
});

function scoreLabel(score: number): { label: string; class: string } {
  if (score >= 5) return { label: "Alta", class: "bg-green-600" };
  if (score >= 3) return { label: "Média", class: "bg-yellow-600" };
  return { label: "Baixa", class: "bg-red-600" };
}

function RadarPage() {
  const [input, setInput] = useState("");
  const [batchId, setBatchId] = useState<number | null>(null);
  const [discoverResult, setDiscoverResult] = useState<DiscoverResponse | null>(null);
  const [selectedCandidates, setSelectedCandidates] = useState<Set<number>>(new Set());
  const [showOnlySelected, setShowOnlySelected] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [elapsed, setElapsed] = useState("");

  const discoverMutation = useDiscover();
  const batchQuery = useBatch(batchId);
  const batchesQuery = useBatches();

  const handleDiscover = () => {
    const query = input.trim();
    if (!query) return;
    setDiscoverResult(null);
    setBatchId(null);
    setSelectedCandidates(new Set());
    setStartTime(Date.now());
    setElapsed("");
    discoverMutation.mutate(
      { query, max_candidates: 10 },
      {
        onSuccess: (data) => {
          setDiscoverResult(data);
          setSelectedCandidates(new Set(data.candidates.map((_, i) => i)));
          if (data.batch_id) {
            setBatchId(data.batch_id);
            startElapsedTimer();
          }
        },
      },
    );
  };

  const startElapsedTimer = () => {
    const interval = setInterval(() => {
      if (startTime) {
        const secs = Math.floor((Date.now() - startTime) / 1000);
        const min = Math.floor(secs / 60);
        const s = secs % 60;
        setElapsed(`${min}:${s.toString().padStart(2, "0")}`);
      }
    }, 1000);
    return () => clearInterval(interval);
  };

  const toggleCandidate = (idx: number) => {
    setSelectedCandidates((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  const toggleAll = () => {
    if (!discoverResult) return;
    if (selectedCandidates.size === discoverResult.candidates.length) {
      setSelectedCandidates(new Set());
    } else {
      setSelectedCandidates(new Set(discoverResult.candidates.map((_, i) => i)));
    }
  };

  const visibleCandidates = showOnlySelected && discoverResult
    ? discoverResult.candidates.filter((_, i) => selectedCandidates.has(i))
    : discoverResult?.candidates ?? [];

  const batchProgress = batchQuery.data
    ? ((batchQuery.data.completed + batchQuery.data.failed) / batchQuery.data.total) * 100
    : 0;

  return (
    <div className="mx-auto w-full max-w-7xl space-y-5 p-4 md:p-6">
      <div className="flex items-center gap-3">
        <Radio className="h-6 w-6 text-[#76B900]" />
        <h1 className="text-lg font-semibold text-foreground">Radar de Startups</h1>
        <Button
          variant="ghost"
          size="sm"
          className="ml-auto gap-2 text-muted-foreground"
          onClick={() => setShowHistory(!showHistory)}
        >
          <History className="h-4 w-4" />
          Histórico
        </Button>
      </div>

      {/* ── Nova Varredura ── */}
      <Card>
        <CardHeader>
          <CardTitle>Nova varredura</CardTitle>
          <CardDescription>
            O sistema gera automaticamente 40+ queries em português e inglês, cruzando setores, rankings, funding e diretórios para encontrar startups brasileiras de IA.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Ex: startup IA brasileira saude | fintech IA Brasil | agentes IA Brasil autônomo"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={3}
          />
          <Button
            onClick={handleDiscover}
            disabled={!input.trim() || discoverMutation.isPending}
            className="bg-[#76B900] text-black hover:bg-[#76B900]/90"
          >
            {discoverMutation.isPending ? (
              <><Clock className="mr-2 h-4 w-4 animate-spin" />VARRENDO...</>
            ) : (
              <><Radio className="mr-2 h-4 w-4" />INICIAR RADAR</>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* ── Erro ── */}
      {discoverMutation.isError && (
        <ApiErrorDisplay error={discoverMutation.error as never} />
      )}

      {/* ── Etapas da descoberta ── */}
      {discoverMutation.isPending && (
        <Card>
          <CardHeader>
            <CardTitle>Buscando candidatos</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-4 w-2/3" />
          </CardContent>
        </Card>
      )}

      {/* ── Candidatos encontrados ── */}
      {discoverResult && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Candidatos encontrados</CardTitle>
              <CardDescription>
                {discoverResult.total} startups identificadas para &ldquo;{discoverResult.query}&rdquo;
                {elapsed && ` — ${elapsed}`}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <label className="flex items-center gap-1 text-xs text-muted-foreground">
                <Checkbox
                  checked={showOnlySelected}
                  onCheckedChange={(v) => setShowOnlySelected(!!v)}
                />
                Só selecionados
              </label>
              <Button variant="outline" size="sm" className="text-xs" onClick={toggleAll}>
                {selectedCandidates.size === discoverResult.candidates.length
                  ? "Desmarcar todos"
                  : "Selecionar todos"}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {visibleCandidates.map((c, i) => {
                const originalIdx = discoverResult.candidates.indexOf(c);
                const score = parseInt(c.score || "0", 10);
                const quality = scoreLabel(score);
                return (
                  <div
                    key={originalIdx}
                    className={`flex items-center justify-between rounded border p-3 text-sm transition-colors ${
                      selectedCandidates.has(originalIdx) ? "border-[#76B900]/50" : "opacity-60"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Checkbox
                        checked={selectedCandidates.has(originalIdx)}
                        onCheckedChange={() => toggleCandidate(originalIdx)}
                      />
                      <div>
                        <span className="font-medium">{c.startup_name}</span>
                        <span className="ml-2 text-xs text-muted-foreground truncate max-w-[300px] inline-block align-middle">
                          {c.source}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={quality.class}>{quality.label}</Badge>
                      {score > 0 && (
                        <span className="text-xs text-muted-foreground">score: {score}</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
            {showOnlySelected && visibleCandidates.length === 0 && (
              <p className="py-4 text-center text-sm text-muted-foreground">
                Nenhum candidato selecionado.
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* ── Progresso do batch ── */}
      {batchQuery.data && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Progresso da análise
              {batchQuery.data.status === "running" && (
                <Clock className="h-4 w-4 animate-spin text-yellow-500" />
              )}
              {batchQuery.data.status === "completed" && (
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              )}
            </CardTitle>
            <CardDescription>
              Batch #{batchQuery.data.id} — {batchQuery.data.completed + batchQuery.data.failed}/{batchQuery.data.total} startups
              {elapsed && ` · ${elapsed} de execução`}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Progress value={batchProgress} className="h-2" />
            <div className="space-y-2">
              {batchQuery.data.items.map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded border p-3 text-sm">
                  <div className="flex items-center gap-2">
                    {item.status === "completed" && <CheckCircle2 className="h-4 w-4 text-green-500" />}
                    {item.status === "failed" && <XCircle className="h-4 w-4 text-red-500" />}
                    {item.status === "running" && <Clock className="h-4 w-4 text-yellow-500" />}
                    {item.status === "pending" && <AlertCircle className="h-4 w-4 text-muted-foreground" />}
                    <span className="font-medium">{item.startup_name}</span>
                    <span className="ml-1 text-xs text-muted-foreground">{item.query}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      className={
                        item.status === "completed"
                          ? "bg-green-600"
                          : item.status === "failed"
                            ? "bg-red-600"
                            : item.status === "running"
                              ? "bg-yellow-600"
                              : ""
                      }
                    >
                      {item.status === "completed"
                        ? "Concluído"
                        : item.status === "failed"
                          ? "Falhou"
                          : item.status === "running"
                            ? "Analisando..."
                            : "Pendente"}
                    </Badge>
                    {item.run_id && (
                      <Link
                        to="/startup/$id"
                        params={{ id: String(item.run_id) }}
                        className="text-xs text-blue-400 hover:underline"
                      >
                        Detalhes
                      </Link>
                    )}
                    {item.error_message && (
                      <span className="max-w-[200px] truncate text-xs text-red-400" title={item.error_message}>
                        {item.error_message}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Skeleton durante carregamento ── */}
      {batchQuery.isLoading && discoverResult && !batchQuery.data && (
        <div className="space-y-3">
          <Skeleton className="h-2 w-full" />
          {Array.from({ length: discoverResult.candidates.length }).map((_, i) => (
            <Skeleton key={i} className="h-14 w-full" />
          ))}
        </div>
      )}

      {/* ── Histórico de varreduras ── */}
      {showHistory && (
        <Card>
          <CardHeader>
            <CardTitle>Varreduras anteriores</CardTitle>
          </CardHeader>
          <CardContent>
            {batchesQuery.isLoading ? (
              <Skeleton className="h-20 w-full" />
            ) : batchesQuery.data && batchesQuery.data.length > 0 ? (
              <div className="space-y-2">
                {batchesQuery.data.map((b) => (
                  <div
                    key={b.id}
                    className="flex cursor-pointer items-center justify-between rounded border p-3 text-sm hover:bg-muted/50"
                    onClick={() => setBatchId(b.id)}
                  >
                    <div>
                      <span className="font-medium">Batch #{b.id}</span>
                      <span className="ml-2 text-xs text-muted-foreground">
                        {b.completed + b.failed}/{b.total} · {new Date(b.created_at).toLocaleString("pt-BR")}
                      </span>
                    </div>
                    <Badge
                      className={
                        b.status === "completed"
                          ? "bg-green-600"
                          : b.status === "running"
                            ? "bg-yellow-600"
                            : ""
                      }
                    >
                      {b.status === "completed" ? "Concluído" : b.status === "running" ? "Em execução" : b.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="py-4 text-center text-sm text-muted-foreground">Nenhuma varredura anterior.</p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

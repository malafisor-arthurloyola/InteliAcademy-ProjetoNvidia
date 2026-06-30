import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Radio } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiErrorDisplay } from "@/components/api-error-display";
import { useDiscover, useBatch } from "@/lib/hooks/use-batch";
import type { DiscoverResponse } from "@/lib/api";

export const Route = createFileRoute("/radar")({
  head: () => ({ meta: [{ title: "Radar — NVIDIA Toph" }] }),
  component: RadarPage,
});

function RadarPage() {
  const [input, setInput] = useState("");
  const [batchId, setBatchId] = useState<number | null>(null);
  const [discoverResult, setDiscoverResult] = useState<DiscoverResponse | null>(null);

  const discoverMutation = useDiscover();
  const batchQuery = useBatch(batchId);

  const handleDiscover = () => {
    const query = input.trim();
    if (!query) return;
    setDiscoverResult(null);
    setBatchId(null);
    discoverMutation.mutate(
      { query, max_candidates: 10 },
      {
        onSuccess: (data) => {
          setDiscoverResult(data);
          if (data.batch_id) setBatchId(data.batch_id);
        },
      },
    );
  };

  return (
    <div className="mx-auto w-full max-w-7xl space-y-5 p-4 md:p-6">
      <div className="flex items-center gap-3">
        <Radio className="h-6 w-6 text-[#76B900]" />
        <h1 className="text-lg font-semibold text-foreground">Radar de Startups</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Nova varredura</CardTitle>
          <CardDescription>
            Digite um termo de busca para descobrir startups brasileiras de IA. Ex: "startup IA brasileira saude", "fintech IA Brasil"
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="startup IA brasileira saude"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={3}
          />
          <Button
            onClick={handleDiscover}
            disabled={!input.trim() || discoverMutation.isPending}
            className="bg-[#76B900] text-black hover:bg-[#76B900]/90"
          >
            {discoverMutation.isPending ? "VARRENDO..." : "INICIAR RADAR"}
          </Button>
        </CardContent>
      </Card>

      {discoverMutation.isError && (
        <ApiErrorDisplay error={discoverMutation.error as never} />
      )}

      {discoverResult && (
        <Card>
          <CardHeader>
            <CardTitle>Candidatos encontrados</CardTitle>
            <CardDescription>
              {discoverResult.total} startups identificadas para &ldquo;{discoverResult.query}&rdquo;
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {discoverResult.candidates.map((c, i) => (
                <div key={i} className="flex items-center justify-between rounded border p-3 text-sm">
                  <div>
                    <span className="font-medium">{c.startup_name}</span>
                    <span className="ml-2 text-xs text-muted-foreground">{c.source}</span>
                  </div>
                  <Badge variant="outline">Aguardando</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {batchQuery.data && (
        <Card>
          <CardHeader>
            <CardTitle>Progresso da análise</CardTitle>
            <CardDescription>
              Batch #{batchQuery.data.id} — {batchQuery.data.completed + batchQuery.data.failed}/{batchQuery.data.total} concluídos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {batchQuery.data.items.map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded border p-3 text-sm">
                  <div>
                    <span className="font-medium">{item.startup_name}</span>
                    <span className="ml-2 text-xs text-muted-foreground">{item.query}</span>
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
                        ? "✅ Concluído"
                        : item.status === "failed"
                          ? "❌ Falhou"
                          : item.status === "running"
                            ? "🔄 Analisando..."
                            : "⏳ Pendente"}
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

      {batchQuery.isLoading && discoverResult && (
        <div className="space-y-3">
          {Array.from({ length: discoverResult.total }).map((_, i) => (
            <Skeleton key={i} className="h-14 w-full" />
          ))}
        </div>
      )}
    </div>
  );
}

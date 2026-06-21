import { createFileRoute } from "@tanstack/react-router";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { sources } from "@/lib/mock-data";
import { ScoreBar, StatusDot } from "@/components/ui-bits";
import { useMemo, useState } from "react";
import { useHealth } from "@/lib/hooks/use-health";
import { ApiErrorDisplay } from "@/components/api-error-display";
import { Search } from "lucide-react";

export const Route = createFileRoute("/sources")({
  head: () => ({ meta: [{ title: "Fontes & Evidências — NVIDIA Toph" }] }),
  component: SourcesPage,
});

function SourcesPage() {
  const [q, setQ] = useState("");
  const { data: health, error: healthError, refetch: retryHealth } = useHealth();
  const filtered = useMemo(
    () => sources.filter((s) => s.name.toLowerCase().includes(q.toLowerCase()) || s.type.toLowerCase().includes(q.toLowerCase())),
    [q],
  );

  const summary = {
    total: sources.length,
    validated: sources.filter((s) => s.status === "validada").length,
    weak: sources.filter((s) => s.status === "fraca").length,
    contradictory: sources.filter((s) => s.status === "contraditória").length,
  };

  if (healthError) {
    return (
      <div className="mx-auto w-full max-w-7xl p-4 md:p-6">
        <ApiErrorDisplay error={healthError as any} onRetry={() => retryHealth()} />
      </div>
    );
  }

  if (!health) {
    return (
      <div className="mx-auto w-full max-w-7xl p-4 md:p-6">
        <Card className="p-4">
          <div className="space-y-3">
            <Skeleton className="h-5 w-48" />
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              {[1,2,3,4].map(i => <Skeleton key={i} className="h-20" />)}
            </div>
            <Skeleton className="h-64 w-full" />
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-7xl space-y-5 p-4 md:p-6">
      <div>
        <h1 className="text-lg font-semibold text-foreground">Fontes & Evidências</h1>
        <p className="text-xs text-muted-foreground">Auditoria das fontes públicas consultadas pelo Scraper e Validator Agents.</p>
      </div>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Card className="p-3"><p className="text-[10px] uppercase text-muted-foreground">Fontes</p><p className="text-xl font-semibold tabular-nums">{summary.total}</p></Card>
        <Card className="p-3"><p className="text-[10px] uppercase text-muted-foreground">Validadas</p><p className="text-xl font-semibold tabular-nums text-primary">{summary.validated}</p></Card>
        <Card className="p-3"><p className="text-[10px] uppercase text-muted-foreground">Fracas</p><p className="text-xl font-semibold tabular-nums text-warning">{summary.weak}</p></Card>
        <Card className="p-3"><p className="text-[10px] uppercase text-muted-foreground">Contraditórias</p><p className="text-xl font-semibold tabular-nums text-destructive">{summary.contradictory}</p></Card>
      </div>

      <Card className="p-3">
        <div className="relative max-w-md">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filtrar fontes por domínio ou tipo…" className="h-9 pl-8" />
        </div>
      </Card>

      <Card className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[800px] border-collapse text-sm">
            <thead className="bg-muted/50 text-left text-[11px] uppercase tracking-wider text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Fonte</th>
                <th className="px-3 py-2 font-medium">Tipo</th>
                <th className="px-3 py-2 font-medium">Evidências</th>
                <th className="px-3 py-2 font-medium">Qualidade média</th>
                <th className="px-3 py-2 font-medium">Última coleta</th>
                <th className="px-3 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s) => (
                <tr key={s.name} className="border-t border-border hover:bg-muted/30">
                  <td className="px-3 py-2.5"><code className="text-xs text-foreground">{s.name}</code></td>
                  <td className="px-3 py-2.5 text-xs text-foreground">{s.type}</td>
                  <td className="px-3 py-2.5 text-xs tabular-nums text-foreground">{s.evidences}</td>
                  <td className="px-3 py-2.5 w-48"><ScoreBar value={s.quality} /></td>
                  <td className="px-3 py-2.5 text-xs tabular-nums text-muted-foreground">{s.lastCollected}</td>
                  <td className="px-3 py-2.5">
                    <Badge variant="outline" className="gap-1.5 text-[10px] capitalize"><StatusDot status={s.status} /> {s.status}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

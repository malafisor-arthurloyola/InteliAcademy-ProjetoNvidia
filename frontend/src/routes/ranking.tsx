import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ScoreBar, MaturityBadge, CompanyLogo, ContactStatusBadge } from "@/components/ui-bits";
import { useContacts } from "@/lib/contacts-store";
import { useHealth } from "@/lib/hooks/use-health";
import { useStartups } from "@/lib/hooks/use-startups";
import { ApiErrorDisplay } from "@/components/api-error-display";
import type { ApiError, StartupRecord } from "@/lib/api";
import { ArrowRight, Filter } from "lucide-react";

export const Route = createFileRoute("/ranking")({
  head: () => ({ meta: [{ title: "Ranking — NVIDIA Toph" }] }),
  component: Ranking,
});

function FilterGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border-b border-border pb-3 last:border-0">
      <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">{title}</p>
      <div className="space-y-1.5">{children}</div>
    </div>
  );
}

function CheckRow<T extends string>({ value, label, set, current }: { value: T; label?: string; set: (v: T[]) => void; current: T[] }) {
  const checked = current.includes(value);
  return (
    <label className="flex cursor-pointer items-center gap-2 text-xs text-foreground">
      <Checkbox
        checked={checked}
        onCheckedChange={() => set(checked ? current.filter((v) => v !== value) : [...current, value])}
      />
      <span className="truncate">{label ?? value}</span>
    </label>
  );
}

function scoreFromCount(count: number, max: number): number {
  return Math.round(Math.min(count / max, 1) * 100);
}

function Ranking() {
  const contacts = useContacts();
  const { data: health, error: healthError, refetch: retryHealth } = useHealth();
  const { data: startupRecords = [], isLoading: startupsLoading, error: startupsError } = useStartups();
  const [search, setSearch] = useState("");
  const [maturity, setMaturity] = useState<string[]>([]);
  const [sectors, setSectors] = useState<string[]>([]);

  const records = startupRecords as StartupRecord[];

  const sectorsList = useMemo(() => Array.from(new Set(records.map((s) => s.sector).filter(Boolean))), [records]);
  const maturitiesList = ["AI-Native", "AI-Enabled", "Non-AI"];

  const filtered = useMemo(() => {
    return records.filter((s) => {
      if (search && !s.name.toLowerCase().includes(search.toLowerCase())) return false;
      if (maturity.length && !maturity.includes(s.classification_label ?? "")) return false;
      if (sectors.length && !sectors.includes(s.sector ?? "")) return false;
      return true;
    });
  }, [search, maturity, sectors, records]);

  const error = healthError ?? startupsError;
  if (error) {
    return (
      <div className="mx-auto w-full max-w-[1600px] p-4 md:p-6">
        <ApiErrorDisplay error={error as ApiError} onRetry={() => retryHealth()} />
      </div>
    );
  }

  if (!health || startupsLoading) {
    return (
      <div className="mx-auto w-full max-w-[1600px] p-4 md:p-6">
        <Card className="p-4">
          <div className="space-y-3">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-9 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto grid w-full max-w-[1600px] gap-4 p-4 md:p-6 lg:grid-cols-[220px_minmax(0,1fr)]">
      {/* Filters */}
      <Card className="h-fit p-4 lg:sticky lg:top-20">
        <div className="mb-3 flex items-center gap-2">
          <Filter className="h-4 w-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">Filtros</h2>
        </div>
        <ScrollArea className="h-[70vh] pr-3">
          <div className="space-y-4">
            <FilterGroup title="Maturidade de IA">
              {maturitiesList.map((m) => (
                <CheckRow key={m} value={m} set={setMaturity} current={maturity} />
              ))}
            </FilterGroup>
            <FilterGroup title="Setor">
              {sectorsList.map((s) => (
                <CheckRow key={s} value={s} set={setSectors} current={sectors} />
              ))}
              {sectorsList.length === 0 && (
                <p className="text-[11px] text-muted-foreground">Nenhum setor disponível</p>
              )}
            </FilterGroup>
          </div>
        </ScrollArea>
      </Card>

      {/* Table */}
      <div className="min-w-0 space-y-3">
        <Card className="p-3">
          <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 sm:flex sm:justify-between">
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Filtrar por nome…"
              className="h-9 sm:max-w-xs"
            />
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-[11px]">{filtered.length} de {records.length}</Badge>
            </div>
          </div>
        </Card>

        <Card className="overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] border-collapse text-sm">
              <thead className="bg-muted/50 text-left text-[11px] uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="px-3 py-2 font-medium">Startup</th>
                  <th className="px-3 py-2 font-medium">Setor</th>
                  <th className="px-3 py-2 font-medium">AI maturity</th>
                  <th className="px-3 py-2 font-medium">Contato</th>
                  <th className="px-3 py-2 font-medium">Radar</th>
                  <th className="px-3 py-2 font-medium">Evidências</th>
                  <th className="px-3 py-2 font-medium">Recomendações</th>
                  <th className="px-3 py-2"></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((s) => {
                  const status = contacts[s.id]?.status ?? "Não contactada";
                  const evidenceScore = scoreFromCount((s as any).evidence_count ?? 0, 5);
                  const recScore = scoreFromCount((s as any).recommendation_count ?? 0, 3);
                  return (
                  <tr key={s.id} className="border-t border-border hover:bg-muted/30">
                    <td className="px-3 py-2.5">
                      <div className="flex items-center gap-2.5">
                        <Link to="/startup/$id" params={{ id: s.id }} aria-label={`Abrir perfil de ${s.name}`} className="rounded-md outline-none ring-primary/40 transition hover:opacity-85 focus-visible:ring-2">
                          <CompanyLogo id={s.id} name={s.name} size="sm" />
                        </Link>
                        <div className="min-w-0">
                          <div className="truncate font-medium text-foreground">{s.name}</div>
                          <div className="truncate text-[11px] text-muted-foreground">{s.funding || "—"}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 py-2.5 text-xs text-foreground">{s.sector || "—"}</td>
                    <td className="px-3 py-2.5">{s.classification_label ? <MaturityBadge value={s.classification_label as any} /> : <span className="text-xs text-muted-foreground">—</span>}</td>
                    <td className="px-3 py-2.5"><ContactStatusBadge status={status} /></td>
                    <td className="px-3 py-2.5 w-36"><ScoreBar value={(s as any).radar_score ?? 0} /></td>
                    <td className="px-3 py-2.5 w-36"><ScoreBar value={evidenceScore} /></td>
                    <td className="px-3 py-2.5 w-36"><ScoreBar value={recScore} /></td>
                    <td className="px-3 py-2.5 text-right">
                      <Button asChild size="sm" variant="ghost" className="gap-1 text-xs">
                        <Link to="/startup/$id" params={{ id: s.id }}>Ver <ArrowRight className="h-3 w-3" /></Link>
                      </Button>
                    </td>
                  </tr>
                  );
                })}
                {filtered.length === 0 && (
                  <tr><td colSpan={8} className="px-3 py-10 text-center text-xs text-muted-foreground">Nenhuma startup com os filtros atuais.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}

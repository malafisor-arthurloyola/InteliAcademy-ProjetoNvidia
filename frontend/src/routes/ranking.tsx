import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  startups,
  NVIDIA_TECHS,
  SOURCE_TYPES,
  type AIMaturity,
  type NvidiaTech,
  type SourceType,
} from "@/lib/mock-data";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ScoreBar,
  MaturityBadge,
  CompanyLogo,
  ContactStatusBadge,
} from "@/components/ui-bits";
import { useContacts } from "@/lib/contacts-store";
import { useHealth } from "@/lib/hooks/use-health";
import { ApiErrorDisplay } from "@/components/api-error-display";
import type { ApiError } from "@/lib/api";
import { ArrowRight, Filter } from "lucide-react";

export const Route = createFileRoute("/ranking")({
  head: () => ({ meta: [{ title: "Ranking — NVIDIA Toph" }] }),
  component: Ranking,
});

const SECTORS = Array.from(new Set(startups.map((s) => s.sector)));
const REGIONS = Array.from(new Set(startups.map((s) => s.region)));
const MATURITIES: AIMaturity[] = ["AI-Native", "AI-Enabled", "Non-AI"];

function FilterGroup({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="border-b border-border pb-3 last:border-0">
      <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
        {title}
      </p>
      <div className="space-y-1.5">{children}</div>
    </div>
  );
}

function CheckRow<T extends string>({
  value,
  label,
  set,
  current,
}: {
  value: T;
  label?: string;
  set: (v: T[]) => void;
  current: T[];
}) {
  const checked = current.includes(value);
  return (
    <label className="flex cursor-pointer items-center gap-2 text-xs text-foreground">
      <Checkbox
        checked={checked}
        onCheckedChange={() =>
          set(
            checked ? current.filter((v) => v !== value) : [...current, value],
          )
        }
      />
      <span className="truncate">{label ?? value}</span>
    </label>
  );
}

function Ranking() {
  const contacts = useContacts();
  const {
    data: health,
    error: healthError,
    refetch: retryHealth,
  } = useHealth();
  const [search, setSearch] = useState("");
  const [maturity, setMaturity] = useState<AIMaturity[]>([]);
  const [sectors, setSectors] = useState<string[]>([]);
  const [regions, setRegions] = useState<string[]>([]);
  const [yearRange, setYearRange] = useState<[number, number]>([2019, 2026]);
  const [minGrowth, setMinGrowth] = useState(0);
  const [minContact, setMinContact] = useState(0);
  const [minEvidence, setMinEvidence] = useState(0);
  const [techs, setTechs] = useState<NvidiaTech[]>([]);
  const [sourceTypes, setSourceTypes] = useState<SourceType[]>([]);

  const filtered = useMemo(() => {
    return startups.filter((s) => {
      if (search && !s.name.toLowerCase().includes(search.toLowerCase()))
        return false;
      if (maturity.length && !maturity.includes(s.maturity)) return false;
      if (sectors.length && !sectors.includes(s.sector)) return false;
      if (regions.length && !regions.includes(s.region)) return false;
      if (s.foundedYear < yearRange[0] || s.foundedYear > yearRange[1])
        return false;
      if (s.growthPotential < minGrowth) return false;
      if (s.contactPriority < minContact) return false;
      if (s.evidenceConfidence < minEvidence) return false;
      if (
        techs.length &&
        !s.recommendations.some((r) => techs.includes(r.tech))
      )
        return false;
      if (
        sourceTypes.length &&
        !s.evidences.some((e) => sourceTypes.includes(e.type))
      )
        return false;
      return true;
    });
  }, [
    search,
    maturity,
    sectors,
    regions,
    yearRange,
    minGrowth,
    minContact,
    minEvidence,
    techs,
    sourceTypes,
  ]);

  if (healthError) {
    return (
      <div className="mx-auto w-full max-w-[1600px] p-4 md:p-6">
        <ApiErrorDisplay
          error={healthError as ApiError}
          onRetry={() => retryHealth()}
        />
      </div>
    );
  }

  if (!health) {
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
    <div className="mx-auto grid w-full max-w-[1600px] gap-4 p-4 md:p-6 lg:grid-cols-[280px_minmax(0,1fr)]">
      {/* Filters */}
      <Card className="h-fit p-4 lg:sticky lg:top-20">
        <div className="mb-3 flex items-center gap-2">
          <Filter className="h-4 w-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">Filtros</h2>
        </div>
        <ScrollArea className="h-[70vh] pr-3">
          <div className="space-y-4">
            <FilterGroup title="Maturidade de IA">
              {MATURITIES.map((m) => (
                <CheckRow
                  key={m}
                  value={m}
                  set={setMaturity}
                  current={maturity}
                />
              ))}
            </FilterGroup>
            <FilterGroup title="Setor">
              {SECTORS.map((s) => (
                <CheckRow
                  key={s}
                  value={s}
                  set={setSectors}
                  current={sectors}
                />
              ))}
            </FilterGroup>
            <FilterGroup title="Região">
              {REGIONS.map((r) => (
                <CheckRow
                  key={r}
                  value={r}
                  set={setRegions}
                  current={regions}
                />
              ))}
            </FilterGroup>
            <FilterGroup
              title={`Ano de fundação: ${yearRange[0]}–${yearRange[1]}`}
            >
              <Slider
                min={2015}
                max={2026}
                step={1}
                value={yearRange}
                onValueChange={(v) =>
                  setYearRange([v[0], v[1]] as [number, number])
                }
              />
            </FilterGroup>
            <FilterGroup title="Valuation / faixa">
              <p className="text-[11px] text-muted-foreground">
                US$ 10M – 100M (mock)
              </p>
              <Slider defaultValue={[10, 100]} min={0} max={200} step={5} />
            </FilterGroup>
            <FilterGroup title="Funding / faixa">
              <p className="text-[11px] text-muted-foreground">
                US$ 1M – 30M (mock)
              </p>
              <Slider defaultValue={[1, 30]} min={0} max={50} step={1} />
            </FilterGroup>
            <FilterGroup title={`Potencial de crescimento ≥ ${minGrowth}`}>
              <Slider
                value={[minGrowth]}
                onValueChange={(v) => setMinGrowth(v[0])}
                max={100}
                step={5}
              />
            </FilterGroup>
            <FilterGroup title={`Prob. de aceitar contato ≥ ${minContact}`}>
              <Slider
                value={[minContact]}
                onValueChange={(v) => setMinContact(v[0])}
                max={100}
                step={5}
              />
            </FilterGroup>
            <FilterGroup title={`Score de evidência ≥ ${minEvidence}`}>
              <Slider
                value={[minEvidence]}
                onValueChange={(v) => setMinEvidence(v[0])}
                max={100}
                step={5}
              />
            </FilterGroup>
            <FilterGroup title="Tipo de fonte">
              {SOURCE_TYPES.map((t) => (
                <CheckRow
                  key={t}
                  value={t}
                  set={setSourceTypes}
                  current={sourceTypes}
                />
              ))}
            </FilterGroup>
            <FilterGroup title="Tecnologia NVIDIA recomendada">
              {NVIDIA_TECHS.map((t) => (
                <CheckRow key={t} value={t} set={setTechs} current={techs} />
              ))}
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
              <Badge variant="outline" className="text-[11px]">
                {filtered.length} de {startups.length}
              </Badge>
            </div>
          </div>
        </Card>

        <Card className="overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[1100px] border-collapse text-sm">
              <thead className="bg-muted/50 text-left text-[11px] uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="px-3 py-2 font-medium">Startup</th>
                  <th className="px-3 py-2 font-medium">Setor</th>
                  <th className="px-3 py-2 font-medium">Região</th>
                  <th className="px-3 py-2 font-medium">Fund.</th>
                  <th className="px-3 py-2 font-medium">AI maturity</th>
                  <th className="px-3 py-2 font-medium">Contato</th>
                  <th className="px-3 py-2 font-medium">Radar</th>
                  <th className="px-3 py-2 font-medium">Evidence</th>
                  <th className="px-3 py-2 font-medium">Growth</th>
                  <th className="px-3 py-2 font-medium">NVIDIA fit</th>
                  <th className="px-3 py-2 font-medium">Prio.</th>
                  <th className="px-3 py-2"></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((s) => {
                  const status = contacts[s.id]?.status ?? "Não contactada";
                  return (
                    <tr
                      key={s.id}
                      className="border-t border-border hover:bg-muted/30"
                    >
                      <td className="px-3 py-2.5">
                        <div className="flex items-center gap-2.5">
                          <Link
                            to="/startup/$id"
                            params={{ id: s.id }}
                            aria-label={`Abrir perfil de ${s.name}`}
                            className="rounded-md outline-none ring-primary/40 transition hover:opacity-85 focus-visible:ring-2"
                          >
                            <CompanyLogo id={s.id} name={s.name} size="sm" />
                          </Link>
                          <div className="min-w-0">
                            <div className="truncate font-medium text-foreground">
                              {s.name}
                            </div>
                            <div className="truncate text-[11px] text-muted-foreground">
                              {s.fundingRange}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-3 py-2.5 text-xs text-foreground">
                        {s.sector}
                      </td>
                      <td className="px-3 py-2.5 text-xs text-foreground">
                        {s.region}
                      </td>
                      <td className="px-3 py-2.5 text-xs tabular-nums text-foreground">
                        {s.foundedYear}
                      </td>
                      <td className="px-3 py-2.5">
                        <MaturityBadge value={s.maturity} />
                      </td>
                      <td className="px-3 py-2.5">
                        <ContactStatusBadge status={status} />
                      </td>
                      <td className="px-3 py-2.5 w-40">
                        <ScoreBar value={s.radarScore} />
                      </td>
                      <td className="px-3 py-2.5 w-40">
                        <ScoreBar value={s.evidenceConfidence} />
                      </td>
                      <td className="px-3 py-2.5 w-40">
                        <ScoreBar value={s.growthPotential} />
                      </td>
                      <td className="px-3 py-2.5 w-40">
                        <ScoreBar value={s.nvidiaFit} />
                      </td>
                      <td className="px-3 py-2.5 w-40">
                        <ScoreBar value={s.contactPriority} />
                      </td>
                      <td className="px-3 py-2.5 text-right">
                        <Button
                          asChild
                          size="sm"
                          variant="ghost"
                          className="gap-1 text-xs"
                        >
                          <Link to="/startup/$id" params={{ id: s.id }}>
                            Ver <ArrowRight className="h-3 w-3" />
                          </Link>
                        </Button>
                      </td>
                    </tr>
                  );
                })}
                {filtered.length === 0 && (
                  <tr>
                    <td
                      colSpan={12}
                      className="px-3 py-10 text-center text-xs text-muted-foreground"
                    >
                      Nenhuma startup com os filtros atuais.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}

// silence unused vars
void Label;

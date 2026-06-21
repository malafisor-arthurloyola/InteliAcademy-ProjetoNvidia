import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Search, Sparkles, BarChart3, FileSearch, FileText, TrendingUp, ShieldCheck, Cpu, Database, ArrowRight, Handshake, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { startups, overviewMetrics, maturityDistribution } from "@/lib/mock-data";
import { sectorDistribution, regionDistribution, weeklyActivity, pipelineFunnel } from "@/lib/company-extras";
import { ScoreBar, MaturityBadge, SectionTitle, CompanyLogo, ContactStatusBadge } from "@/components/ui-bits";
import { useContacts } from "@/lib/contacts-store";
import { useHealth } from "@/lib/hooks/use-health";
import { ApiErrorDisplay } from "@/components/api-error-display";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  AreaChart, Area,
} from "recharts";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Overview — NVIDIA Toph" },
      { name: "description", content: "Visão geral do radar de startups brasileiras AI-native." },
    ],
  }),
  component: Overview,
});

function Metric({ label, value, hint, icon: Icon }: { label: string; value: string | number; hint?: string; icon: any }) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">{label}</p>
          <p className="mt-1 text-2xl font-semibold tabular-nums text-foreground">{value}</p>
          {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
        </div>
        <div className="grid h-8 w-8 shrink-0 place-items-center rounded-md bg-primary/10 text-primary">
          <Icon className="h-4 w-4" />
        </div>
      </div>
    </Card>
  );
}

const DONUT_COLORS = ["var(--color-primary)", "var(--color-info)", "#94a3b8"];

function Overview() {
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const contacts = useContacts();
  const top = [...startups].sort((a, b) => b.radarScore - a.radarScore).slice(0, 4);
  const { data: health, error: healthError, refetch: retryHealth } = useHealth();
  const apiOk = health?.status === "ok";

  const onAnalyze = () => {
    const match = startups.find((s) => s.name.toLowerCase().includes(q.toLowerCase())) ?? startups[0];
    navigate({ to: "/startup/$id", params: { id: match.id } });
  };

  const totalMaturity = maturityDistribution.reduce((acc, m) => acc + m.value, 0);

  if (healthError && !apiOk) {
    return (
      <div className="mx-auto w-full max-w-7xl space-y-5 p-4 md:p-6">
        <ApiErrorDisplay
          error={healthError as { endpoint: string; status: number; message: string }}
          onRetry={() => retryHealth()}
        />
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6 p-4 md:p-6">
      {/* Search hero — utility */}
      <Card className="border-border p-4 md:p-6">
        <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 sm:flex sm:flex-wrap sm:justify-between">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="truncate text-base font-semibold text-foreground md:text-lg">Radar de startups brasileiras AI-native</h1>
              <Badge variant="outline" className={`gap-1 text-[10px] ${apiOk ? "border-green-500/30 bg-green-500/5 text-green-600" : "border-primary/30 bg-primary/5 text-primary"}`}>
                {apiOk ? <><CheckCircle2 className="h-3 w-3" /> API ativa</> : <><Database className="h-3 w-3" /> Demo data</>}
              </Badge>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">Apenas dados públicos. Toda recomendação NVIDIA é justificada e rastreável até a fonte.</p>
          </div>
        </div>

        <div className="mt-4 flex flex-col gap-2 sm:flex-row">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onAnalyze()}
              placeholder="Pesquisar startup por nome"
              className="h-11 pl-9 text-sm"
            />
          </div>
          <Button size="lg" className="h-11 gap-1.5" onClick={onAnalyze}>
            <Sparkles className="h-4 w-4" /> Analisar empresa
          </Button>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => navigate({ to: "/ranking" })}>
            <BarChart3 className="h-3.5 w-3.5" /> Ver ranking geral
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => navigate({ to: "/contacts" })}>
            <Handshake className="h-3.5 w-3.5" /> Contatos comerciais
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => navigate({ to: "/sources" })}>
            <FileSearch className="h-3.5 w-3.5" /> Explorar fontes
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => navigate({ to: "/briefing" })}>
            <FileText className="h-3.5 w-3.5" /> Gerar briefing demo
          </Button>
        </div>
      </Card>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-5">
        <Metric label="Startups analisadas" value={overviewMetrics.analyzed} hint="últimos 30 dias" icon={Cpu} />
        <Metric label="AI-Native candidates" value={overviewMetrics.aiNative} hint="classificadas" icon={Sparkles} />
        <Metric label="Evidências validadas" value={overviewMetrics.validatedEvidences} hint="com URL preservada" icon={ShieldCheck} />
        <Metric label="Recomendações NVIDIA" value={overviewMetrics.recommendations} hint="com justificativa" icon={TrendingUp} />
        <Metric label="Briefings prontos" value={overviewMetrics.briefings} hint="para abordagem" icon={FileText} />
      </div>

      {/* Donut + sector bars + region bars */}
      <div className="grid gap-4 lg:grid-cols-6">
        <Card className="p-4 lg:col-span-2">
          <SectionTitle title="Maturidade de IA" desc={`${totalMaturity} startups classificadas`} />
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={maturityDistribution}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={2}
                  stroke="var(--color-background)"
                  strokeWidth={2}
                >
                  {maturityDistribution.map((_, i) => <Cell key={i} fill={DONUT_COLORS[i]} />)}
                </Pie>
                <Tooltip
                  contentStyle={{ background: "var(--color-popover)", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 12 }}
                />
                <Legend verticalAlign="bottom" iconType="circle" wrapperStyle={{ fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="p-4 lg:col-span-2">
          <SectionTitle title="Distribuição por setor" desc="Top setores em pipeline" />
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sectorDistribution} layout="vertical" margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
                <CartesianGrid horizontal={false} stroke="var(--color-border)" />
                <XAxis type="number" tickLine={false} axisLine={false} fontSize={10} stroke="var(--color-muted-foreground)" />
                <YAxis type="category" dataKey="name" tickLine={false} axisLine={false} fontSize={11} width={70} stroke="var(--color-muted-foreground)" />
                <Tooltip
                  contentStyle={{ background: "var(--color-popover)", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 12 }}
                  cursor={{ fill: "var(--color-muted)" }}
                />
                <Bar dataKey="value" fill="var(--color-primary)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="p-4 lg:col-span-2">
          <SectionTitle title="Distribuição por região" desc="UFs com mais startups na base" />
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={regionDistribution} margin={{ top: 8, right: 8, bottom: 8, left: -16 }}>
                <CartesianGrid vertical={false} stroke="var(--color-border)" />
                <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={11} stroke="var(--color-muted-foreground)" />
                <YAxis tickLine={false} axisLine={false} fontSize={11} stroke="var(--color-muted-foreground)" />
                <Tooltip
                  contentStyle={{ background: "var(--color-popover)", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 12 }}
                  cursor={{ fill: "var(--color-muted)" }}
                />
                <Bar dataKey="value" fill="var(--color-info)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Activity + funnel */}
      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="p-4 lg:col-span-3">
          <SectionTitle title="Atividade semanal" desc="Evidências coletadas e recomendações geradas (últimas 9 semanas)" />
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weeklyActivity} margin={{ top: 8, right: 8, bottom: 8, left: -16 }}>
                <defs>
                  <linearGradient id="ev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--color-primary)" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="var(--color-primary)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="rc" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--color-info)" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="var(--color-info)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} stroke="var(--color-border)" />
                <XAxis dataKey="week" tickLine={false} axisLine={false} fontSize={11} stroke="var(--color-muted-foreground)" />
                <YAxis tickLine={false} axisLine={false} fontSize={11} stroke="var(--color-muted-foreground)" />
                <Tooltip
                  contentStyle={{ background: "var(--color-popover)", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 12 }}
                />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Area type="monotone" dataKey="evidencias" name="Evidências" stroke="var(--color-primary)" strokeWidth={2} fill="url(#ev)" />
                <Area type="monotone" dataKey="recomend" name="Recomendações" stroke="var(--color-info)" strokeWidth={2} fill="url(#rc)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="p-4 lg:col-span-2">
          <SectionTitle title="Funil comercial" desc="Da descoberta ao fechamento" />
          <div className="space-y-2">
            {pipelineFunnel.map((step, i) => {
              const pct = (step.value / pipelineFunnel[0].value) * 100;
              return (
                <div key={step.stage}>
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-foreground">{step.stage}</span>
                    <span className="tabular-nums text-muted-foreground">{step.value}</span>
                  </div>
                  <div className="mt-1 h-2 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${pct}%`,
                        background: i >= pipelineFunnel.length - 2 ? "var(--color-primary)" : "var(--color-info)",
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      {/* Top opportunities */}
      <Card className="p-4">
        <SectionTitle
          title="Top opportunities"
          desc="Startups com maior Radar score validado"
          right={
            <Button variant="ghost" size="sm" className="gap-1 text-xs" onClick={() => navigate({ to: "/ranking" })}>
              Ver ranking <ArrowRight className="h-3 w-3" />
            </Button>
          }
        />
        <div className="divide-y divide-border">
          {top.map((s) => {
            const status = contacts[s.id]?.status;
            return (
              <Link
                key={s.id}
                to="/startup/$id"
                params={{ id: s.id }}
                className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 py-3 transition hover:bg-muted/40 sm:grid-cols-[auto_minmax(0,2fr)_minmax(0,1.5fr)_auto]"
              >
                <CompanyLogo id={s.id} name={s.name} size="md" />
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="truncate text-sm font-medium text-foreground">{s.name}</span>
                    <MaturityBadge value={s.maturity} />
                    {status && status !== "Não contactada" && <ContactStatusBadge status={status} />}
                  </div>
                  <p className="mt-0.5 truncate text-xs text-muted-foreground">{s.sector} · {s.region}</p>
                </div>
                <div className="hidden min-w-0 sm:block">
                  <ScoreBar value={s.radarScore} />
                  <p className="mt-1 text-[10px] uppercase tracking-wider text-muted-foreground">Radar score</p>
                </div>
                <Button variant="ghost" size="sm" className="gap-1 text-xs">
                  Ver <ArrowRight className="h-3 w-3" />
                </Button>
              </Link>
            );
          })}
        </div>
      </Card>
    </div>
  );
}

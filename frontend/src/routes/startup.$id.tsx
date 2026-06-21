import { createFileRoute, notFound, Link } from "@tanstack/react-router";
import { getStartup, type Startup } from "@/lib/mock-data";
import { getCompanyExtras } from "@/lib/company-extras";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  MaturityBadge,
  ScoreBar,
  SectionTitle,
  CompanyLogo,
  ContactStatusBadge,
} from "@/components/ui-bits";
import {
  ArrowLeft,
  ExternalLink,
  FileText,
  Sparkles,
  AlertTriangle,
  ShieldCheck,
  Cpu,
  Mail,
  Phone,
  Linkedin,
  Globe,
  User,
  TrendingUp,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  CONTACT_STATUSES,
  setContactStatus,
  useContact,
  type ContactStatus,
} from "@/lib/contacts-store";
import { useHealth } from "@/lib/hooks/use-health";
import { ApiErrorDisplay } from "@/components/api-error-display";
import { useState, useEffect } from "react";

export const Route = createFileRoute("/startup/$id")({
  head: ({ params }) => ({
    meta: [{ title: `${params.id} — NVIDIA Toph` }],
  }),
  loader: ({ params }) => {
    const s = getStartup(params.id);
    if (!s) throw notFound();
    return s;
  },
  component: StartupPage,
  notFoundComponent: () => (
    <div className="p-10 text-center text-sm text-muted-foreground">Startup não encontrada.</div>
  ),
});

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-border bg-card p-3">
      <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums text-foreground">{value}</p>
      <ScoreBar value={value} className="mt-2" />
    </div>
  );
}

function StartupPage() {
  const s = Route.useLoaderData() as Startup;
  const extras = getCompanyExtras(s.id);
  const contact = useContact(s.id);
  const { data: health, error: healthError, refetch: retryHealth } = useHealth();
  const [note, setNote] = useState(contact.note ?? "");
  useEffect(() => setNote(contact.note ?? ""), [s.id, contact.note]);

  const latest = extras.growth[extras.growth.length - 1];
  const first = extras.growth[0];
  const valuationDelta = Math.round(((latest.valuationM - first.valuationM) / first.valuationM) * 100);
  const arrDelta = Math.round(((latest.arrM - first.arrM) / first.arrM) * 100);

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
        <Card className="p-5">
          <div className="space-y-3">
            <div className="flex items-center gap-4">
              <Skeleton className="h-12 w-12 rounded-full" />
              <div className="space-y-1.5">
                <Skeleton className="h-6 w-48" />
                <Skeleton className="h-4 w-32" />
              </div>
            </div>
            <Skeleton className="h-40 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-7xl space-y-5 p-4 md:p-6">
      <div className="flex items-center justify-between gap-2">
        <Button asChild variant="ghost" size="sm" className="gap-1 text-xs">
          <Link to="/ranking"><ArrowLeft className="h-3.5 w-3.5" /> Ranking</Link>
        </Button>
        <Button asChild size="sm" className="gap-1.5">
          <Link to="/briefing"><FileText className="h-4 w-4" /> Gerar briefing</Link>
        </Button>
      </div>

      {/* Header */}
      <Card className="p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex min-w-0 items-start gap-4">
            <CompanyLogo id={s.id} name={s.name} size="lg" />
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="truncate text-xl font-semibold text-foreground md:text-2xl">{s.name}</h1>
                <MaturityBadge value={s.maturity} />
                <ContactStatusBadge status={contact.status} />
              </div>
              <p className="mt-1 text-sm text-muted-foreground">{s.sector} · {s.region} · fundada em {s.foundedYear}</p>
              <p className="mt-1 text-xs text-muted-foreground">{s.fundingRange} · valuation estimado {s.valuationRange}</p>
            </div>
          </div>
          <div className="rounded-md border border-primary/30 bg-primary/5 px-4 py-2 text-center">
            <p className="text-[10px] uppercase tracking-wider text-primary">Radar score</p>
            <p className="text-3xl font-bold tabular-nums text-primary">{s.radarScore}</p>
          </div>
        </div>
      </Card>

      {/* Contact + Status manager */}
      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="p-5 lg:col-span-2">
          <SectionTitle title="Contato da empresa" desc="Dados públicos coletados do site oficial e perfis institucionais" />
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-md border border-border p-3">
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Contato principal</p>
              <div className="mt-1.5 flex items-center gap-2">
                <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-muted text-muted-foreground">
                  <User className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-foreground">{extras.contact.primaryName}</p>
                  <p className="truncate text-[11px] text-muted-foreground">{extras.contact.primaryRole}</p>
                </div>
              </div>
            </div>
            <div className="rounded-md border border-border p-3">
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Canais</p>
              <ul className="mt-1.5 space-y-1 text-xs">
                <li className="flex items-center gap-2">
                  <Mail className="h-3.5 w-3.5 text-muted-foreground" />
                  <a className="truncate text-primary hover:underline" href={`mailto:${extras.contact.email}`}>{extras.contact.email}</a>
                </li>
                <li className="flex items-center gap-2">
                  <Phone className="h-3.5 w-3.5 text-muted-foreground" />
                  <a className="text-foreground hover:underline" href={`tel:${extras.contact.phone.replace(/\s/g, "")}`}>{extras.contact.phone}</a>
                </li>
                <li className="flex items-center gap-2">
                  <Globe className="h-3.5 w-3.5 text-muted-foreground" />
                  <a className="truncate text-primary hover:underline" href={extras.contact.website} target="_blank" rel="noreferrer">{extras.contact.website}</a>
                </li>
                <li className="flex items-center gap-2">
                  <Linkedin className="h-3.5 w-3.5 text-muted-foreground" />
                  <a className="truncate text-primary hover:underline" href={extras.contact.linkedin} target="_blank" rel="noreferrer">LinkedIn da empresa</a>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <Button size="sm" className="gap-1.5" asChild>
              <a href={`mailto:${extras.contact.email}`}><Mail className="h-3.5 w-3.5" /> Enviar e-mail</a>
            </Button>
            <Button size="sm" variant="outline" className="gap-1.5" asChild>
              <a href={`tel:${extras.contact.phone.replace(/\s/g, "")}`}><Phone className="h-3.5 w-3.5" /> Ligar</a>
            </Button>
            <Button size="sm" variant="outline" className="gap-1.5" asChild>
              <a href={extras.contact.linkedin} target="_blank" rel="noreferrer"><Linkedin className="h-3.5 w-3.5" /> Abrir LinkedIn</a>
            </Button>
          </div>
        </Card>

        <Card className="p-5">
          <SectionTitle title="Status do contato" desc="Atualizado em tempo real" />
          <Select value={contact.status} onValueChange={(v) => setContactStatus(s.id, v as ContactStatus, note)}>
            <SelectTrigger className="h-9 text-sm"><SelectValue /></SelectTrigger>
            <SelectContent>
              {CONTACT_STATUSES.map((cs) => (
                <SelectItem key={cs} value={cs} className="text-sm">{cs}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <div className="mt-3 space-y-1">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Notas internas</p>
            <Textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              onBlur={() => setContactStatus(s.id, contact.status, note)}
              placeholder="Última conversa, próximos passos, blockers…"
              className="min-h-[80px] text-xs"
            />
          </div>
          <p className="mt-2 text-[11px] text-muted-foreground">
            Última atualização: {contact.updatedAt ? new Date(contact.updatedAt).toLocaleString("pt-BR") : "—"}
          </p>
        </Card>
      </div>

      {/* Growth chart */}
      <Card className="p-5">
        <SectionTitle
          title="Crescimento (capital & ARR)"
          desc="Estimativas trimestrais a partir de dados públicos — valores em US$ milhões"
          right={
            <div className="flex items-center gap-3 text-xs">
              <Badge variant="outline" className="gap-1 border-primary/30 bg-primary/5 text-primary">
                <TrendingUp className="h-3 w-3" /> Valuation +{valuationDelta}%
              </Badge>
              <Badge variant="outline" className="gap-1 border-info/30 bg-info/5 text-info">
                <TrendingUp className="h-3 w-3" /> ARR +{arrDelta}%
              </Badge>
            </div>
          }
        />
        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-md border border-border p-3">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Valuation atual</p>
            <p className="mt-1 text-xl font-semibold tabular-nums text-foreground">US$ {latest.valuationM}M</p>
            <p className="text-[11px] text-muted-foreground">de US$ {first.valuationM}M em {first.month}</p>
          </div>
          <div className="rounded-md border border-border p-3">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground">ARR estimado</p>
            <p className="mt-1 text-xl font-semibold tabular-nums text-foreground">US$ {latest.arrM}M</p>
            <p className="text-[11px] text-muted-foreground">de US$ {first.arrM}M em {first.month}</p>
          </div>
          <div className="rounded-md border border-border p-3">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Headcount</p>
            <p className="mt-1 text-xl font-semibold tabular-nums text-foreground">{latest.headcount}</p>
            <p className="text-[11px] text-muted-foreground">de {first.headcount} em {first.month}</p>
          </div>
        </div>
        <div className="mt-4 h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={extras.growth} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
              <defs>
                <linearGradient id="val" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--color-primary)" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="var(--color-primary)" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="arr" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--color-info)" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="var(--color-info)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid vertical={false} stroke="var(--color-border)" />
              <XAxis dataKey="month" tickLine={false} axisLine={false} fontSize={11} stroke="var(--color-muted-foreground)" />
              <YAxis tickLine={false} axisLine={false} fontSize={11} stroke="var(--color-muted-foreground)" />
              <Tooltip
                contentStyle={{ background: "var(--color-popover)", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 12 }}
                formatter={(v: number, name: string) => [`US$ ${v}M`, name === "valuationM" ? "Valuation" : "ARR"]}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} formatter={(v) => v === "valuationM" ? "Valuation" : "ARR"} />
              <Area type="monotone" dataKey="valuationM" stroke="var(--color-primary)" strokeWidth={2} fill="url(#val)" />
              <Area type="monotone" dataKey="arrM" stroke="var(--color-info)" strokeWidth={2} fill="url(#arr)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Summary */}
      <Card className="p-5">
        <SectionTitle title="Resumo executivo" />
        <p className="text-sm leading-relaxed text-foreground">{s.executiveSummary}</p>
        <Separator className="my-4" />
        <SectionTitle title="Classificação AI-native" desc="Justificativa metodológica" />
        <p className="text-sm leading-relaxed text-foreground">{s.maturityJustification}</p>
      </Card>

      {/* Score cards */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-5">
        <StatCard label="Radar score" value={s.radarScore} />
        <StatCard label="Evidence confidence" value={s.evidenceConfidence} />
        <StatCard label="NVIDIA fit" value={s.nvidiaFit} />
        <StatCard label="Contact priority" value={s.contactPriority} />
        <StatCard label="Growth potential" value={s.growthPotential} />
      </div>

      {/* Evidences */}
      <Card className="p-5">
        <SectionTitle title="Evidências públicas" desc="Cada evidência preserva URL, trecho original e data de coleta" />
        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] border-collapse text-sm">
            <thead className="bg-muted/40 text-left text-[11px] uppercase tracking-wider text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">#</th>
                <th className="px-3 py-2 font-medium">URL</th>
                <th className="px-3 py-2 font-medium">Tipo de fonte</th>
                <th className="px-3 py-2 font-medium">Trecho</th>
                <th className="px-3 py-2 font-medium">Coletado em</th>
                <th className="px-3 py-2 font-medium">Confiança</th>
              </tr>
            </thead>
            <tbody>
              {s.evidences.map((e, i) => (
                <tr key={i} className="border-t border-border align-top">
                  <td className="px-3 py-2 text-xs text-muted-foreground tabular-nums">E{i + 1}</td>
                  <td className="px-3 py-2">
                    <a href={e.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-xs text-primary hover:underline">
                      <ExternalLink className="h-3 w-3" /> <code className="text-[11px]">{e.url}</code>
                    </a>
                  </td>
                  <td className="px-3 py-2 text-xs text-foreground">{e.type}</td>
                  <td className="px-3 py-2 text-xs text-foreground">"{e.snippet}"</td>
                  <td className="px-3 py-2 text-xs text-muted-foreground tabular-nums">{e.collectedAt}</td>
                  <td className="px-3 py-2 w-40"><ScoreBar value={e.confidence} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Gaps */}
      <Card className="p-5">
        <SectionTitle title="Gaps técnicos identificados" desc="Custo de inferência, latência, dependência de APIs, governança, escalabilidade e observabilidade" />
        <div className="grid gap-2 sm:grid-cols-2">
          {s.gaps.map((g) => (
            <div key={g.name} className="flex items-start gap-3 rounded-md border border-border p-3">
              <AlertTriangle className={`mt-0.5 h-4 w-4 shrink-0 ${g.severity === "Alta" ? "text-destructive" : g.severity === "Média" ? "text-warning" : "text-muted-foreground"}`} />
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-medium text-foreground">{g.name}</p>
                  <Badge variant="outline" className="text-[10px]">Severidade: {g.severity}</Badge>
                </div>
                <p className="mt-0.5 text-xs text-muted-foreground">{g.description}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Recommendations */}
      <Card className="p-5">
        <SectionTitle title="Recomendações NVIDIA" desc="Nenhuma recomendação sem justificativa técnica, de negócio e evidência associada" />
        <div className="space-y-3">
          {s.recommendations.map((r, i) => (
            <div key={i} className="rounded-md border border-border p-4">
              <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3 sm:flex sm:flex-wrap sm:justify-between">
                <div className="flex min-w-0 items-center gap-2">
                  <div className="grid h-8 w-8 shrink-0 place-items-center rounded-md bg-primary/10 text-primary"><Cpu className="h-4 w-4" /></div>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-foreground">{r.tech}</p>
                    <p className="text-[11px] text-muted-foreground">Próxima ação: {r.nextAction}</p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  <Badge variant="outline" className={`text-[10px] ${r.priority === "Alta" ? "border-primary/40 bg-primary/10 text-primary" : ""}`}>Prioridade {r.priority}</Badge>
                  <Badge variant="outline" className="text-[10px]">Complexidade {r.complexity}</Badge>
                </div>
              </div>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Justificativa técnica</p>
                  <p className="mt-1 text-xs text-foreground">{r.technicalRationale}</p>
                </div>
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Justificativa de negócio</p>
                  <p className="mt-1 text-xs text-foreground">{r.businessRationale}</p>
                </div>
              </div>
              <div className="mt-3 flex flex-wrap items-center gap-1.5">
                <ShieldCheck className="h-3 w-3 text-primary" />
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Evidências:</span>
                {r.evidenceRefs.map((ref) => (
                  <Badge key={ref} variant="outline" className="text-[10px]">E{ref + 1}</Badge>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex items-center gap-2 rounded-md border border-primary/30 bg-primary/5 p-3">
          <Sparkles className="h-4 w-4 text-primary" />
          <p className="text-xs text-foreground"><span className="font-medium">Próxima ação sugerida:</span> {s.nextAction}</p>
        </div>
      </Card>
    </div>
  );
}

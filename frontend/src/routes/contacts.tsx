import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { startups } from "@/lib/mock-data";
import {
  CONTACT_STATUSES,
  setContactStatus,
  useContacts,
  type ContactStatus,
} from "@/lib/contacts-store";
import { CompanyLogo, ContactStatusBadge, SectionTitle } from "@/components/ui-bits";
import { getCompanyExtras } from "@/lib/company-extras";
import { ArrowRight, Mail, Phone, Handshake } from "lucide-react";

export const Route = createFileRoute("/contacts")({
  head: () => ({ meta: [{ title: "Contatos — NVIDIA Toph" }] }),
  component: ContactsPage,
});

const FILTERS: (ContactStatus | "Todas")[] = ["Todas", ...CONTACT_STATUSES];

function ContactsPage() {
  const contacts = useContacts();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>("Todas");

  const rows = useMemo(() => {
    return startups
      .map((s) => ({ s, rec: contacts[s.id] ?? { status: "Não contactada" as ContactStatus, updatedAt: "" } }))
      .filter(({ s, rec }) => {
        if (filter !== "Todas" && rec.status !== filter) return false;
        if (search && !s.name.toLowerCase().includes(search.toLowerCase())) return false;
        return true;
      })
      .sort((a, b) => (b.rec.updatedAt || "").localeCompare(a.rec.updatedAt || ""));
  }, [contacts, search, filter]);

  const counts = useMemo(() => {
    const c: Record<ContactStatus, number> = {
      "Não contactada": 0,
      "Contactada": 0,
      "Aguardando resposta": 0,
      "Em negociação": 0,
      "Contrato fechado": 0,
      "Contrato recusado": 0,
    };
    for (const s of startups) {
      const status = contacts[s.id]?.status ?? "Não contactada";
      c[status]++;
    }
    return c;
  }, [contacts]);

  return (
    <div className="mx-auto w-full max-w-7xl space-y-5 p-4 md:p-6">
      <Card className="p-4 md:p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <Handshake className="h-4 w-4 text-primary" />
              <h1 className="text-base font-semibold text-foreground md:text-lg">Empresas em pipeline comercial</h1>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Controle qual startup já foi abordada e em que estágio está cada negociação.
            </p>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
          {CONTACT_STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`rounded-md border px-3 py-2 text-left transition ${
                filter === s ? "border-primary/40 bg-primary/5" : "border-border hover:bg-muted/40"
              }`}
            >
              <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">{s}</p>
              <p className="mt-0.5 text-lg font-semibold tabular-nums text-foreground">{counts[s]}</p>
            </button>
          ))}
        </div>
      </Card>

      <Card className="p-3">
        <div className="flex flex-wrap items-center gap-2">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar empresa…"
            className="h-9 sm:max-w-xs"
          />
          <Select value={filter} onValueChange={(v) => setFilter(v as ContactStatus | "Todas")}>
            <SelectTrigger className="h-9 w-[200px]"><SelectValue /></SelectTrigger>
            <SelectContent>
              {FILTERS.map((f) => <SelectItem key={f} value={f}>{f}</SelectItem>)}
            </SelectContent>
          </Select>
          <Badge variant="outline" className="ml-auto text-[11px]">{rows.length} resultados</Badge>
        </div>
      </Card>

      <Card className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse text-sm">
            <thead className="bg-muted/50 text-left text-[11px] uppercase tracking-wider text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Empresa</th>
                <th className="px-3 py-2 font-medium">Contato principal</th>
                <th className="px-3 py-2 font-medium">Canal</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium">Atualizado</th>
                <th className="px-3 py-2"></th>
              </tr>
            </thead>
            <tbody>
              {rows.map(({ s, rec }) => {
                const x = getCompanyExtras(s.id);
                return (
                  <tr key={s.id} className="border-t border-border hover:bg-muted/30">
                    <td className="px-3 py-2.5">
                      <div className="flex items-center gap-2.5">
                        <CompanyLogo id={s.id} name={s.name} size="sm" />
                        <div className="min-w-0">
                          <div className="truncate font-medium text-foreground">{s.name}</div>
                          <div className="truncate text-[11px] text-muted-foreground">{s.sector}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 py-2.5">
                      <div className="text-xs font-medium text-foreground">{x.contact.primaryName}</div>
                      <div className="text-[11px] text-muted-foreground">{x.contact.primaryRole}</div>
                    </td>
                    <td className="px-3 py-2.5">
                      <div className="flex flex-col gap-0.5 text-[11px]">
                        <a href={`mailto:${x.contact.email}`} className="inline-flex items-center gap-1 text-primary hover:underline">
                          <Mail className="h-3 w-3" /> {x.contact.email}
                        </a>
                        <span className="inline-flex items-center gap-1 text-muted-foreground">
                          <Phone className="h-3 w-3" /> {x.contact.phone}
                        </span>
                      </div>
                    </td>
                    <td className="px-3 py-2.5 w-[200px]">
                      <Select
                        value={rec.status}
                        onValueChange={(v) => setContactStatus(s.id, v as ContactStatus)}
                      >
                        <SelectTrigger className="h-8 text-xs">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {CONTACT_STATUSES.map((cs) => (
                            <SelectItem key={cs} value={cs} className="text-xs">{cs}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </td>
                    <td className="px-3 py-2.5 text-[11px] tabular-nums text-muted-foreground">
                      {rec.updatedAt ? new Date(rec.updatedAt).toLocaleDateString("pt-BR") : "—"}
                    </td>
                    <td className="px-3 py-2.5 text-right">
                      <Button asChild size="sm" variant="ghost" className="gap-1 text-xs">
                        <Link to="/startup/$id" params={{ id: s.id }}>Abrir <ArrowRight className="h-3 w-3" /></Link>
                      </Button>
                    </td>
                  </tr>
                );
              })}
              {rows.length === 0 && (
                <tr><td colSpan={6} className="px-3 py-10 text-center text-xs text-muted-foreground">Nenhuma empresa com esse filtro.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <Card className="p-4">
        <SectionTitle title="Legenda de status" />
        <div className="flex flex-wrap gap-2">
          {CONTACT_STATUSES.map((s) => <ContactStatusBadge key={s} status={s} />)}
        </div>
      </Card>
    </div>
  );
}

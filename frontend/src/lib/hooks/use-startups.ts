import { useQuery } from "@tanstack/react-query";
import { fetchStartups, fetchStartupById } from "@/lib/api";

export function useStartups() {
  return useQuery({
    queryKey: ["startups"],
    queryFn: fetchStartups,
    retry: 1,
    staleTime: 15_000,
  });
}

export function useStartup(id: string) {
  return useQuery({
    queryKey: ["startups", id],
    queryFn: () => fetchStartupById(id),
    enabled: !!id,
    retry: 1,
  });
}

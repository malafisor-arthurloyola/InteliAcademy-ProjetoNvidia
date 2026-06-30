import { useMutation, useQuery } from "@tanstack/react-query";
import { fetchBatch, fetchBatches, submitDiscover } from "@/lib/api";

export function useDiscover() {
  return useMutation({
    mutationFn: ({ query, max_candidates }: { query: string; max_candidates?: number }) =>
      submitDiscover(query, max_candidates),
  });
}

export function useBatch(batchId: number | null) {
  return useQuery({
    queryKey: ["batch", batchId],
    queryFn: () => fetchBatch(batchId!),
    enabled: !!batchId,
    refetchInterval: (data) =>
      data?.state?.data?.status === "running" ? 3000 : false,
  });
}

export function useBatches() {
  return useQuery({
    queryKey: ["batches"],
    queryFn: fetchBatches,
  });
}

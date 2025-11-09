/**
 * Custom API Query Hook
 *
 * Wrapper around React Query's useQuery for consistent API data fetching.
 * Provides standard error handling and loading states.
 *
 * Usage:
 * const { data, isLoading, error } = useApiQuery({
 *   queryKey: endpoints.user.register.getKeys(),
 *   queryFn: () => endpoints.user.register.query(data)
 * });
 */

import { useQuery } from "@tanstack/react-query";

export function useApiQuery(options) {
    return useQuery(options);
}

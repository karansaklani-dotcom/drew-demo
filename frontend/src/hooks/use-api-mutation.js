/**
 * Custom API Mutation Hook
 *
 * Wrapper around React Query's useMutation for consistent API mutations.
 * Provides standard error handling and success callbacks.
 *
 * Usage:
 * const mutation = useApiMutation({
 *   mutationFn: (data) => endpoints.user.register.query(data),
 *   onSuccess: () => { ... }
 * });
 */

import { useMutation } from "@tanstack/react-query";

export function useApiMutation(options) {
    return useMutation(options);
}

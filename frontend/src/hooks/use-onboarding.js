/**
 * Onboarding-related hooks using React Query
 */

import { useApiMutation } from "./use-api-mutation";
import { useQueryClient } from "@tanstack/react-query";
import { endpoints } from "../utils/endpoints";

/**
 * Hook to complete onboarding
 */
export function useOnboardingComplete() {
    const queryClient = useQueryClient();

    return useApiMutation({
        mutationFn: (data) => endpoints.onboarding.complete.query(data),
        onSuccess: () => {
            // Invalidate user/me to refetch with updated data
            queryClient.invalidateQueries({
                queryKey: endpoints.user.me.getKeys(),
            });
        },
    });
}

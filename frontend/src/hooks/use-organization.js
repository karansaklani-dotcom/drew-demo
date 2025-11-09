/**
 * Organization-related hooks using React Query
 */

import { useApiQuery } from "./use-api-query";
import { useApiMutation } from "./use-api-mutation";
import { endpoints } from "../utils/endpoints";
import { useQueryClient } from "@tanstack/react-query";

/**
 * Hook to create an organization
 */
export function useOrganizationCreate() {
    const queryClient = useQueryClient();

    return useApiMutation({
        mutationFn: (data) => endpoints.organization.create.query(data),
        onSuccess: (organization) => {
            // Invalidate user/me to refetch with new organizationId
            queryClient.invalidateQueries({
                queryKey: endpoints.user.me.getKeys(),
            });
            // Set the organization in cache
            queryClient.setQueryData(
                endpoints.organization.get.getKeys(organization.id),
                organization
            );
        },
    });
}

/**
 * Hook to update an organization
 */
export function useOrganizationUpdate() {
    const queryClient = useQueryClient();

    return useApiMutation({
        mutationFn: ({ id, data }) =>
            endpoints.organization.update.query(id, data),
        onSuccess: (updatedOrg, variables) => {
            // Update the organization cache
            queryClient.setQueryData(
                endpoints.organization.get.getKeys(variables.id),
                updatedOrg
            );
            // Invalidate user/me in case organizationId changed
            queryClient.invalidateQueries({
                queryKey: endpoints.user.me.getKeys(),
            });
        },
    });
}

/**
 * Hook to get an organization by ID
 */
export function useOrganization(id) {
    return useApiQuery({
        queryKey: endpoints.organization.get.getKeys(id),
        queryFn: () => endpoints.organization.get.query(id),
        enabled: !!id,
    });
}

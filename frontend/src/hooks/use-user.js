/**
 * User-related hooks using React Query
 */

import { useApiQuery } from "./use-api-query";
import { useApiMutation } from "./use-api-mutation";
import { endpoints } from "../utils/endpoints";
import { useQueryClient } from "@tanstack/react-query";

/**
 * Hook to get current user (me)
 */
export function useUserMe() {
    return useApiQuery({
        queryKey: endpoints.user.me.getKeys(),
        queryFn: () => endpoints.user.me.query(),
        retry: false,
        staleTime: 5 * 60 * 1000, // 5 minutes
    });
}

/**
 * Hook to register a new user
 */
export function useUserRegister() {
    const queryClient = useQueryClient();

    return useApiMutation({
        mutationFn: (data) => endpoints.user.register.query(data),
        onSuccess: (userData) => {
            // Update the user/me cache with the new user
            queryClient.setQueryData(endpoints.user.me.getKeys(), userData);
        },
    });
}

/**
 * Hook to verify/login a user
 */
export function useUserVerify() {
    const queryClient = useQueryClient();

    return useApiMutation({
        mutationFn: (data) => endpoints.user.verify.query(data),
        onSuccess: (userData) => {
            // Update the user/me cache with the logged in user
            queryClient.setQueryData(endpoints.user.me.getKeys(), userData);
        },
    });
}

/**
 * Hook to update user
 */
export function useUserUpdate() {
    const queryClient = useQueryClient();

    return useApiMutation({
        mutationFn: ({ id, data }) => endpoints.user.update.query(id, data),
        onSuccess: (updatedUser, variables) => {
            // Update the user/me cache
            queryClient.setQueryData(endpoints.user.me.getKeys(), updatedUser);
            // Also update the specific user cache if it exists
            queryClient.setQueryData(
                endpoints.user.update.getKeys(variables.id),
                updatedUser
            );
        },
    });
}

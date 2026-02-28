"use client";

import { useSession } from "next-auth/react";
import { useMemo } from "react";
import { apiClient } from "./client";

export function useAuthOptions() {
  const { data: session } = useSession();
  const options = useMemo(
    () => ({
      client: apiClient,
      auth: session?.accessToken,
    }),
    [session?.accessToken]
  );
  return { options, isAuthenticated: !!session?.accessToken };
}

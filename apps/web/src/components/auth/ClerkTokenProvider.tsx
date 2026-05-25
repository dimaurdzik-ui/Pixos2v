"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect } from "react";
import { setClerkTokenGetter } from "@/lib/api";

/**
 * Registers the Clerk getToken function into the global axios interceptor.
 * Must be rendered inside ClerkProvider (i.e. inside the dashboard layout).
 */
export function ClerkTokenProvider() {
  const { getToken } = useAuth();

  useEffect(() => {
    setClerkTokenGetter(getToken);
  }, [getToken]);

  return null;
}

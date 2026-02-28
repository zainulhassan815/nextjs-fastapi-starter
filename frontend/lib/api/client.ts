import { createClient, createConfig } from "./generated/client";

export const apiClient = createClient(
  createConfig({
    baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  })
);

import { createClient, createConfig } from "./generated/client";

export const serverClient = createClient(
  createConfig({
    baseUrl: process.env.BACKEND_URL || "http://localhost:8000",
  })
);

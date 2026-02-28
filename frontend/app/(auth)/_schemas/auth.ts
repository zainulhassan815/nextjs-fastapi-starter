import { z } from "zod";
import type { CreateUserRequest, LoginRequest } from "@/lib/api";

export const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
}) satisfies z.ZodType<LoginRequest>;

export const registerSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  full_name: z.string().min(1, "Name is required").nullable().optional(),
}) satisfies z.ZodType<CreateUserRequest>;

export type LoginFormValues = z.infer<typeof loginSchema>;
export type RegisterFormValues = z.infer<typeof registerSchema>;

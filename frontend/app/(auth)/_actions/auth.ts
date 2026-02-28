"use server";

import { signIn } from "@/auth";
import { register as registerUser, serverClient } from "@/lib/api";
import { loginSchema, registerSchema } from "../_schemas/auth";

export type AuthActionResult = {
  success: boolean;
  error?: string;
};

export async function loginAction(
  values: unknown
): Promise<AuthActionResult> {
  const parsed = loginSchema.safeParse(values);
  if (!parsed.success) {
    return { success: false, error: "Invalid form data" };
  }

  try {
    await signIn("credentials", {
      email: parsed.data.email,
      password: parsed.data.password,
      redirect: false,
    });
    return { success: true };
  } catch {
    return { success: false, error: "Invalid email or password" };
  }
}

export async function registerAction(
  values: unknown
): Promise<AuthActionResult> {
  const parsed = registerSchema.safeParse(values);
  if (!parsed.success) {
    return { success: false, error: "Invalid form data" };
  }

  const { error } = await registerUser({
    client: serverClient,
    body: {
      email: parsed.data.email,
      password: parsed.data.password,
      full_name: parsed.data.full_name ?? undefined,
    },
  });

  if (error) {
    const detail = (error as any)?.message || (error as any)?.detail;
    return {
      success: false,
      error: typeof detail === "string" ? detail : "Registration failed",
    };
  }

  // Auto-login after registration
  try {
    await signIn("credentials", {
      email: parsed.data.email,
      password: parsed.data.password,
      redirect: false,
    });
    return { success: true };
  } catch {
    return { success: false, error: "Account created but login failed" };
  }
}

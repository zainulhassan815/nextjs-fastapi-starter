import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";

import { getMe, login, serverClient } from "@/lib/api";

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Credentials({
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const { data: tokenData, error: loginError } = await login({
          client: serverClient,
          body: {
            email: credentials.email as string,
            password: credentials.password as string,
          },
        });

        if (loginError || !tokenData) return null;

        const { data: user, error: profileError } = await getMe({
          client: serverClient,
          headers: { Authorization: `Bearer ${tokenData.access_token}` },
        });

        if (profileError || !user) return null;

        return {
          id: String(user.id),
          email: user.email,
          name: user.full_name,
          accessToken: tokenData.access_token,
        };
      },
    }),
  ],
  session: { strategy: "jwt" },
  pages: {
    signIn: "/login",
  },
  callbacks: {
    jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.accessToken = (user as any).accessToken;
      }
      return token;
    },
    session({ session, token }) {
      session.user.id = token.id as string;
      (session as any).accessToken = token.accessToken;
      return session;
    },
  },
});

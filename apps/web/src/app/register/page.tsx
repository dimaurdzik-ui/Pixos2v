"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const router = useRouter();

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      localStorage.setItem("pixos_mock_user_email", email);
      localStorage.setItem("pixos_mock_workspace_id", "00000000-0000-0000-0000-000000000000");
      router.push("/office");
    }
  };

  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center bg-background">
      <Link href="/" className="absolute top-8 left-8 text-xl font-bold text-white tracking-tight">
        Pixos
      </Link>
      <div className="w-full max-w-md px-8">
        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Create an account</CardTitle>
            <CardDescription className="text-center">
              Enter your email below to create your account and workspace
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleRegister}>
            <CardContent className="grid gap-4">
              <div className="grid gap-2">
                <label htmlFor="company" className="text-sm font-medium leading-none">
                  Company Name
                </label>
                <Input id="company" type="text" placeholder="Acme Corp" required />
              </div>
              <div className="grid gap-2">
                <label htmlFor="email" className="text-sm font-medium leading-none">
                  Email
                </label>
                <Input 
                  id="email" 
                  type="email" 
                  placeholder="admin@pixos.ai" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required 
                />
              </div>
              <div className="grid gap-2">
                <label htmlFor="password" className="text-sm font-medium leading-none">
                  Password
                </label>
                <Input id="password" type="password" required />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-4">
              <Button className="w-full" type="submit">Create account</Button>
              <div className="text-center text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link href="/login" className="underline underline-offset-4 hover:text-primary">
                  Sign in
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}

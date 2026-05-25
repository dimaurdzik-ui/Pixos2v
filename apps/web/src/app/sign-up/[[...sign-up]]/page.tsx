import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <SignUp fallbackRedirectUrl="/office" signInUrl="/sign-in" />
    </div>
  );
}

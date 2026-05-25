import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Cpu, Shield, Globe } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Navbar */}
      <header className="px-6 lg:px-14 h-20 flex items-center justify-between border-b border-white/5 bg-background/50 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
            <Cpu className="text-primary-foreground h-5 w-5" />
          </div>
          <span className="text-xl font-bold tracking-tight">Pixos</span>
        </div>
        <nav className="hidden md:flex gap-8 text-sm font-medium text-muted-foreground">
          <Link href="#features" className="hover:text-foreground transition-colors">Features</Link>
          <Link href="#agents" className="hover:text-foreground transition-colors">Agents</Link>
          <Link href="#safety" className="hover:text-foreground transition-colors">Safety</Link>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/login">
            <Button variant="ghost">Sign In</Button>
          </Link>
          <Link href="/register">
            <Button>Get Started</Button>
          </Link>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative pt-32 pb-24 px-6 lg:px-14 overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background -z-10" />
          
          <div className="max-w-5xl mx-auto text-center space-y-8">
            <h1 className="text-5xl md:text-7xl font-bold tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60 leading-tight">
              Pixos is your autonomous <br className="hidden md:block" /> AI company.
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
              Build, manage, and deploy a workforce of AI agents that coordinate, execute complex workflows, and integrate securely with your existing tools.
            </p>
            <div className="flex items-center justify-center gap-4 pt-4">
              <Link href="/register">
                <Button size="lg" className="h-12 px-8 text-base">Start Building</Button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline" className="h-12 px-8 text-base bg-transparent border-white/10 hover:bg-white/5">
                  View Demo
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Feature Grid */}
        <section id="features" className="py-24 px-6 lg:px-14 border-t border-white/5 bg-black/20">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold tracking-tight mb-4">Enterprise-grade AI Workforce</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">Everything you need to orchestrate autonomous agents in a secure, compliant environment.</p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              <div className="glass p-8 rounded-2xl border border-white/5 space-y-4">
                <div className="h-12 w-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
                  <Cpu className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold">Autonomous Teams</h3>
                <p className="text-muted-foreground">Agents form teams, assign roles, and break down complex tasks into executable workflows.</p>
              </div>
              <div className="glass p-8 rounded-2xl border border-white/5 space-y-4">
                <div className="h-12 w-12 bg-amber-500/10 rounded-xl flex items-center justify-center text-amber-500">
                  <Shield className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold">Strict Approvals (HITL)</h3>
                <p className="text-muted-foreground">Granular tool policies ensure high-risk actions are paused for human-in-the-loop approval.</p>
              </div>
              <div className="glass p-8 rounded-2xl border border-white/5 space-y-4">
                <div className="h-12 w-12 bg-blue-500/10 rounded-xl flex items-center justify-center text-blue-500">
                  <Globe className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold">Native Integrations</h3>
                <p className="text-muted-foreground">Connect securely to GitHub, Gmail, Slack, and Notion via verified adapters.</p>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      {/* Footer */}
      <footer className="border-t border-white/5 py-12 px-6 lg:px-14 text-center text-sm text-muted-foreground">
        <p>© 2026 Pixos Inc. All rights reserved.</p>
      </footer>
    </div>
  );
}

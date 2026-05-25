import { AppLayout } from "@/components/Layout";

export default function Home() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Workspace Overview</h1>
          <p className="text-muted-foreground mt-2">Manage your AI Workforce and active tasks.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass p-6 rounded-2xl border-border/50 hover:border-indigo-500/50 transition-colors">
            <h3 className="text-lg font-medium text-white mb-2">Active Agents</h3>
            <p className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400">3</p>
          </div>
          <div className="glass p-6 rounded-2xl border-border/50 hover:border-purple-500/50 transition-colors">
            <h3 className="text-lg font-medium text-white mb-2">Tasks Completed</h3>
            <p className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-400">128</p>
          </div>
          <div className="glass p-6 rounded-2xl border-border/50 hover:border-amber-500/50 transition-colors">
            <h3 className="text-lg font-medium text-white mb-2">Pending Approvals</h3>
            <p className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-amber-400 to-orange-400">1</p>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

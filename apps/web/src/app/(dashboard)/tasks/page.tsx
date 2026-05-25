"use client";

import { AppLayout } from "@/components/Layout";
import { useState } from "react";
import { api } from "@/lib/api";
import { Send, Bot, Loader2 } from "lucide-react";

export default function TasksPage() {
  const [prompt, setPrompt] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [tasks, setTasks] = useState<{id: string, desc: string, status: string}[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    setIsSubmitting(true);
    try {
      const res = await api.createTask(prompt);
      setTasks([{ id: res.task_id, desc: prompt, status: "Running" }, ...tasks]);
      setPrompt("");
      // Trigger run
      await api.runWorkflow(res.task_id);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">AI Tasks</h1>
          <p className="text-muted-foreground mt-2">Assign new tasks to your AI workforce.</p>
        </div>

        {/* Create Task Form */}
        <div className="glass p-1 rounded-2xl border-border/50 focus-within:border-indigo-500/50 transition-colors">
          <form onSubmit={handleSubmit} className="flex relative">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. Write a weekly update email to the team..."
              className="w-full bg-transparent border-none text-white px-6 py-4 outline-none placeholder:text-muted-foreground/50"
            />
            <button
              type="submit"
              disabled={isSubmitting || !prompt.trim()}
              className="absolute right-2 top-2 bottom-2 bg-indigo-500 hover:bg-indigo-600 text-white px-4 rounded-xl font-medium flex items-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </form>
        </div>

        {/* Task List */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-white">Recent Tasks</h2>
          {tasks.length === 0 ? (
            <div className="text-center py-12 glass rounded-2xl border-dashed border-border/50">
              <Bot className="w-12 h-12 text-muted-foreground/30 mx-auto mb-4" />
              <p className="text-muted-foreground">No tasks assigned yet. Your agents are idle.</p>
            </div>
          ) : (
            tasks.map(task => (
              <div key={task.id} className="glass p-6 rounded-2xl border-border/50 flex justify-between items-center group hover:border-indigo-500/30 transition-all">
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                  <p className="text-white font-medium">{task.desc}</p>
                </div>
                <span className="text-xs px-3 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-full">
                  {task.status}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </AppLayout>
  );
}

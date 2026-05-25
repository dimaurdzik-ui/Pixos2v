"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Users, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { getTeams, createTeam } from "@/lib/api";

export default function TeamsPage() {
  const [teams, setTeams] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newTeam, setNewTeam] = useState({ name: "", description: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      const data = await getTeams();
      setTeams(data);
    } catch (error) {
      console.error("Failed to fetch teams", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await createTeam(newTeam);
      await fetchTeams();
      setShowModal(false);
      setNewTeam({ name: "", description: "" });
    } catch (error) {
      console.error("Failed to create team", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 relative">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Teams</h2>
          <p className="text-muted-foreground mt-1">Group agents into specialized squads.</p>
        </div>
        <Button onClick={() => setShowModal(true)}>
          <Plus className="mr-2 h-4 w-4" /> Create Team
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {teams.length === 0 ? (
          <div className="col-span-2 text-center p-8 text-muted-foreground border border-dashed rounded-lg">
            No teams found. Click "Create Team" to add one.
          </div>
        ) : (
          teams.map((team) => (
            <Card key={team.id}>
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="h-10 w-10 bg-primary/10 rounded-lg flex items-center justify-center">
                    <Users className="h-5 w-5 text-primary" />
                  </div>
                </div>
                <CardTitle>{team.name}</CardTitle>
                <CardDescription>{team.description || "No description provided."}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex -space-x-2">
                  <div className="h-8 w-8 rounded-full bg-muted border-2 border-background flex items-center justify-center text-xs">AI</div>
                  <div className="h-8 w-8 rounded-full bg-muted border-2 border-background flex items-center justify-center text-xs">AI</div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-md shadow-2xl border-primary/20">
            <CardHeader>
              <CardTitle>Create New Team</CardTitle>
              <CardDescription>Group agents for specific projects.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateTeam} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Name</label>
                  <Input required value={newTeam.name} onChange={e => setNewTeam({...newTeam, name: e.target.value})} placeholder="e.g. Content Team" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Description</label>
                  <Input value={newTeam.description} onChange={e => setNewTeam({...newTeam, description: e.target.value})} placeholder="What does this team do?" />
                </div>
                <div className="flex justify-end gap-2 pt-4">
                  <Button type="button" variant="outline" onClick={() => setShowModal(false)}>Cancel</Button>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Create Team
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

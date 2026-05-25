"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Check, X, ShieldAlert, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { getPendingApprovals, approveAction, rejectAction } from "@/lib/api";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    fetchApprovals();
  }, []);

  const fetchApprovals = async () => {
    try {
      const data = await getPendingApprovals();
      setApprovals(data);
    } catch (error) {
      console.error("Failed to fetch approvals:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: string) => {
    setProcessingId(id);
    try {
      await approveAction(id);
      setApprovals(approvals.filter(a => a.id !== id));
    } catch (error) {
      console.error("Approval failed:", error);
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (id: string) => {
    setProcessingId(id);
    try {
      await rejectAction(id);
      setApprovals(approvals.filter(a => a.id !== id));
    } catch (error) {
      console.error("Rejection failed:", error);
    } finally {
      setProcessingId(null);
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
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Pending Approvals</h2>
        <p className="text-muted-foreground mt-1">Review actions requested by your agents.</p>
      </div>

      <div className="grid gap-6">
        {approvals.length === 0 ? (
          <div className="text-center p-12 border rounded-xl bg-card text-muted-foreground">
            No pending approvals at this time.
          </div>
        ) : (
          approvals.map((approval) => (
            <Card key={approval.id} className="border-amber-500/30 bg-amber-500/5">
              <CardHeader className="pb-4">
                <div className="flex items-center gap-2 text-amber-500 mb-2">
                  <ShieldAlert className="h-5 w-5" />
                  <span className="font-semibold text-sm tracking-wider uppercase">Action Required</span>
                </div>
                <CardTitle>Execute Tool: {approval.action_type}</CardTitle>
                <CardDescription>Agent wants to perform an action that requires human review</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-black/40 p-4 rounded-lg border border-border/50 overflow-x-auto">
                  <pre className="text-sm text-muted-foreground font-mono">
                    {JSON.stringify(approval.payload_preview, null, 2)}
                  </pre>
                </div>
              </CardContent>
              <CardFooter className="flex gap-4">
                <Button 
                  className="bg-green-600 hover:bg-green-700 text-white"
                  onClick={() => handleApprove(approval.id)}
                  disabled={processingId !== null}
                >
                  {processingId === approval.id ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Check className="mr-2 h-4 w-4" />}
                  Approve
                </Button>
                <Button 
                  variant="destructive"
                  onClick={() => handleReject(approval.id)}
                  disabled={processingId !== null}
                >
                  {processingId === approval.id ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <X className="mr-2 h-4 w-4" />}
                  Reject
                </Button>
              </CardFooter>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

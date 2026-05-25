"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Check, X, ShieldAlert } from "lucide-react";

export default function ApprovalsPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Pending Approvals</h2>
        <p className="text-muted-foreground mt-1">Review actions requested by your agents.</p>
      </div>

      <div className="grid gap-6">
        <Card className="border-amber-500/30 bg-amber-500/5">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-2 text-amber-500 mb-2">
              <ShieldAlert className="h-5 w-5" />
              <span className="font-semibold text-sm tracking-wider uppercase">Action Required</span>
            </div>
            <CardTitle>Send Email via Gmail</CardTitle>
            <CardDescription>System Coordinator wants to use tool `gmail.send`</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-black/40 p-4 rounded-lg border border-border/50 overflow-x-auto">
              <pre className="text-sm text-muted-foreground font-mono">
                {JSON.stringify({
                  to: "investors@example.com",
                  subject: "Q2 Earnings Report Draft",
                  body: "Please find the attached..."
                }, null, 2)}
              </pre>
            </div>
          </CardContent>
          <CardFooter className="flex gap-4">
            <Button className="bg-green-600 hover:bg-green-700 text-white">
              <Check className="mr-2 h-4 w-4" />
              Approve
            </Button>
            <Button variant="destructive">
              <X className="mr-2 h-4 w-4" />
              Reject
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}

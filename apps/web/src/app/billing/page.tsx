"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function BillingPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Billing & Credits</h2>
        <p className="text-muted-foreground mt-1">Manage your subscriptions and agent credits.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Current Plan</CardTitle>
            <CardDescription>Pro Tier</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-3xl font-bold">$99<span className="text-sm text-muted-foreground font-normal">/mo</span></div>
            <Button className="w-full">Manage Subscription</Button>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Credit Balance</CardTitle>
            <CardDescription>Used for AI inference (GPT-4o, etc.)</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-3xl font-bold">12,450 <span className="text-sm text-muted-foreground font-normal">credits</span></div>
            <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-primary w-[30%]"></div>
            </div>
            <p className="text-xs text-muted-foreground">Approx. 3,000 credits used this month.</p>
            <Button variant="outline" className="w-full">Add Credits</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

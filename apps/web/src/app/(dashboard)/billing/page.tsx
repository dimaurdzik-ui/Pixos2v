"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { CreditCard, Zap, Download, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { getBillingBalance, getBillingHistory, createCheckoutSession } from "@/lib/api";
import { useSearchParams, useRouter } from "next/navigation";
import toast from "react-hot-toast";

export default function BillingPage() {
  const [balance, setBalance] = useState<number | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    // Check for Stripe redirect success/cancel
    const success = searchParams.get("success");
    const canceled = searchParams.get("canceled");
    
    if (success) {
      toast.success("Payment successful! Credits added to your account.");
      router.replace("/billing");
    }
    
    if (canceled) {
      toast.error("Payment was canceled.");
      router.replace("/billing");
    }
    const fetchData = async () => {
      try {
        const [balData, histData] = await Promise.all([
          getBillingBalance(),
          getBillingHistory()
        ]);
        setBalance(balData.balance);
        setHistory(histData);
      } catch (error) {
        console.error("Failed to fetch billing data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const handleBuyCredits = async (amountUsd: number) => {
    setCheckoutLoading(true);
    try {
      const res = await createCheckoutSession(amountUsd);
      if (res.url) {
        window.location.href = res.url;
      }
    } catch (error: any) {
      console.error("Checkout error:", error);
      toast.error(error.response?.data?.detail || "Failed to initiate checkout");
      setCheckoutLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Billing & Usage</h2>
          <p className="text-muted-foreground mt-1">Manage your credit balance and track API usage.</p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={() => handleBuyCredits(10)} 
            disabled={checkoutLoading}
          >
            <CreditCard className="mr-2 h-4 w-4" /> $10 (1k cr)
          </Button>
          <Button 
            onClick={() => handleBuyCredits(50)} 
            disabled={checkoutLoading}
          >
            <Zap className="mr-2 h-4 w-4" /> Buy 5k Credits ($50)
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="md:col-span-1 border-primary/50 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-6 opacity-10">
            <Zap className="h-24 w-24 text-primary" />
          </div>
          <CardHeader>
            <CardTitle>Current Balance</CardTitle>
            <CardDescription>Available AI compute credits</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-5xl font-bold font-mono tracking-tighter">{balance?.toLocaleString() || 0}</div>
            <p className="text-sm text-muted-foreground mt-4">Credits are deducted automatically per workflow run.</p>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Usage History</CardTitle>
              <CardDescription>Recent credit deductions</CardDescription>
            </div>
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" /> Export CSV
            </Button>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Workflow ID</TableHead>
                  <TableHead className="text-right">Cost</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {history.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center text-muted-foreground py-8">
                      No usage records found.
                    </TableCell>
                  </TableRow>
                ) : (
                  history.map((record) => (
                    <TableRow key={record.id}>
                      <TableCell>{new Date(record.created_at).toLocaleString()}</TableCell>
                      <TableCell className="font-mono text-xs">{record.workflow_run_id || "Unknown"}</TableCell>
                      <TableCell className="text-right text-red-400 font-medium">-{record.cost}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

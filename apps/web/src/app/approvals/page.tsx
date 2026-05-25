"use client";

import { AppLayout } from "@/components/Layout";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { AlertTriangle, Check, X } from "lucide-react";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<any[]>([]);

  useEffect(() => {
    api.getApprovals().then(setApprovals);
  }, []);

  const handleAction = (id: string, action: "approve" | "reject") => {
    // In real app, call API to approve/reject
    console.log(`${action} approval ${id}`);
    setApprovals(approvals.filter(a => a.id !== id));
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center">
            Pending Approvals 
            {approvals.length > 0 && (
              <span className="ml-3 bg-red-500/20 text-red-400 text-sm px-3 py-1 rounded-full border border-red-500/30">
                {approvals.length} Action Required
              </span>
            )}
          </h1>
          <p className="text-muted-foreground mt-2">Review and authorize high-risk actions requested by your agents.</p>
        </div>

        <div className="space-y-6">
          {approvals.length === 0 ? (
            <div className="text-center py-16 glass rounded-2xl border-border/50">
              <div className="w-16 h-16 rounded-full bg-green-500/10 flex items-center justify-center mx-auto mb-4">
                <Check className="w-8 h-8 text-green-400" />
              </div>
              <h3 className="text-lg font-medium text-white">All clear!</h3>
              <p className="text-muted-foreground mt-1">No pending approvals at the moment.</p>
            </div>
          ) : (
            approvals.map(approval => (
              <div key={approval.id} className="glass overflow-hidden rounded-2xl border-red-500/30 shadow-[0_0_20px_rgba(239,68,68,0.05)]">
                <div className="p-6 border-b border-border/50 flex justify-between items-start bg-red-500/5">
                  <div className="flex items-start space-x-4">
                    <div className="p-3 bg-red-500/20 rounded-xl mt-1">
                      <AlertTriangle className="w-6 h-6 text-red-400" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-white">{approval.tool}</h3>
                      <p className="text-red-300 mt-1 text-sm font-medium">Risk Level: {approval.risk}</p>
                    </div>
                  </div>
                </div>
                <div className="p-6 bg-black/20">
                  <h4 className="text-sm font-medium text-muted-foreground mb-3 uppercase tracking-wider">Payload Preview</h4>
                  <pre className="bg-black/40 p-4 rounded-xl text-sm text-indigo-200 overflow-x-auto border border-white/5">
                    {JSON.stringify(approval.payload, null, 2)}
                  </pre>
                  
                  <div className="mt-8 flex justify-end space-x-4">
                    <button 
                      onClick={() => handleAction(approval.id, "reject")}
                      className="px-6 py-2.5 rounded-xl font-medium text-red-400 hover:bg-red-500/10 border border-red-500/30 transition-colors flex items-center space-x-2"
                    >
                      <X className="w-4 h-4" />
                      <span>Reject</span>
                    </button>
                    <button 
                      onClick={() => handleAction(approval.id, "approve")}
                      className="px-6 py-2.5 rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-400 hover:to-green-400 text-white shadow-[0_0_15px_rgba(16,185,129,0.4)] transition-all flex items-center space-x-2"
                    >
                      <Check className="w-4 h-4" />
                      <span>Approve Action</span>
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </AppLayout>
  );
}

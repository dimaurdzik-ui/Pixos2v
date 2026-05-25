"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getArtifact } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, ArrowLeft, Download } from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

export default function ArtifactDetailPage() {
  const params = useParams();
  const [artifact, setArtifact] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchArtifact = async () => {
      try {
        const data = await getArtifact(params.id as string);
        setArtifact(data);
      } catch (error) {
        console.error("Failed to load artifact", error);
      } finally {
        setLoading(false);
      }
    };
    if (params.id) {
      fetchArtifact();
    }
  }, [params.id]);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!artifact) {
    return (
      <div className="p-8 max-w-4xl mx-auto space-y-4">
        <Link href="/artifacts">
          <Button variant="ghost"><ArrowLeft className="mr-2 h-4 w-4" /> Back to Artifacts</Button>
        </Link>
        <div className="p-12 text-center text-muted-foreground border rounded-lg bg-card">
          Artifact not found.
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/artifacts">
            <Button variant="outline" size="icon"><ArrowLeft className="h-4 w-4" /></Button>
          </Link>
          <div>
            <h2 className="text-2xl font-bold tracking-tight">{artifact.name}</h2>
            <p className="text-sm text-muted-foreground">Type: {artifact.artifact_type} • {new Date(artifact.created_at).toLocaleString()}</p>
          </div>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" /> Download
        </Button>
      </div>

      <Card>
        <CardContent className="p-8">
          <article className="prose prose-invert max-w-none prose-pre:bg-black/50 prose-pre:border prose-pre:border-border/50">
            <ReactMarkdown>{artifact.content}</ReactMarkdown>
          </article>
        </CardContent>
      </Card>
    </div>
  );
}

"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, User, Bot, Loader2, MessageSquarePlus, Activity, Briefcase } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { getConversations, getConversationMessages, sendAgentChat, getAgents, getWorkflows, getPendingApprovals } from "@/lib/api";
import { toast } from "sonner";
import { ScrollArea } from "@/components/ui/scroll-area";
import { formatDistanceToNow } from "date-fns";

type Conversation = {
  id: string;
  title: string;
  conversation_type: string;
  agent_id: string | null;
  team_id: string | null;
  created_at: string;
};

type Message = { 
  id: string; 
  sender_type: "user" | "agent" | "system"; 
  content: string;
  created_at: string;
};

export default function OfficePage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  
  const [taskInput, setTaskInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingChats, setIsLoadingChats] = useState(true);
  
  const [coordinatorId, setCoordinatorId] = useState<string | null>(null);
  const [metrics, setMetrics] = useState({ agents: 0, workflows: 0, approvals: 0 });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (activeConversationId) {
      fetchMessages(activeConversationId);
    } else {
      setMessages([]);
    }
  }, [activeConversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchInitialData = async () => {
    try {
      setIsLoadingChats(true);
      const [convosData, agentsData, workflowsData, approvalsData] = await Promise.all([
        getConversations(),
        getAgents(),
        getWorkflows(),
        getPendingApprovals()
      ]);
      
      setConversations(convosData);
      if (convosData.length > 0) {
        setActiveConversationId(convosData[0].id);
      }
      
      setMetrics({
        agents: agentsData.length,
        workflows: workflowsData.length,
        approvals: approvalsData.length
      });
      
      const coordinator = agentsData.find((a: any) => a.is_coordinator);
      if (coordinator) {
        setCoordinatorId(coordinator.id);
      }
    } catch (error) {
      toast.error("Failed to load office data");
    } finally {
      setIsLoadingChats(false);
    }
  };

  const fetchMessages = async (id: string) => {
    try {
      const data = await getConversationMessages(id);
      setMessages(data);
    } catch (error) {
      console.error("Failed to fetch messages", error);
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskInput.trim() || !coordinatorId) return;
    
    const userMessage: Message = { 
      id: Date.now().toString(), 
      sender_type: "user", 
      content: taskInput,
      created_at: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setTaskInput("");
    setIsSubmitting(true);
    
    try {
      const data = await sendAgentChat(coordinatorId, userMessage.content);
      const assistantMessage: Message = { 
        id: (Date.now() + 1).toString(), 
        sender_type: "agent", 
        content: data.message,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      // If this was a new chat, we should refresh the conversation list
      if (!activeConversationId) {
        const convos = await getConversations();
        setConversations(convos);
        if (convos.length > 0) {
          setActiveConversationId(convos[0].id);
        }
      }
    } catch (error) {
      toast.error("Failed to send message");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex h-full w-full bg-background border-t">
      {/* Sidebar: Conversation List */}
      <div className="w-80 border-r flex flex-col bg-muted/20">
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="font-semibold text-lg tracking-tight">Recent Chats</h2>
          <Button variant="ghost" size="icon" onClick={handleNewChat}>
            <MessageSquarePlus className="h-5 w-5" />
          </Button>
        </div>
        
        <ScrollArea className="flex-1">
          {isLoadingChats ? (
            <div className="p-8 flex justify-center">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-8 text-center text-sm text-muted-foreground">
              No conversations yet. Start a new chat!
            </div>
          ) : (
            <div className="p-2 space-y-1">
              {conversations.map(convo => (
                <button
                  key={convo.id}
                  onClick={() => setActiveConversationId(convo.id)}
                  className={`w-full text-left px-3 py-3 rounded-lg text-sm transition-colors ${
                    activeConversationId === convo.id 
                      ? 'bg-primary/10 hover:bg-primary/15 font-medium' 
                      : 'hover:bg-muted'
                  }`}
                >
                  <div className="truncate mb-1">{convo.title || "New Conversation"}</div>
                  <div className="text-xs text-muted-foreground">
                    {convo.created_at ? formatDistanceToNow(new Date(convo.created_at), { addSuffix: true }) : ""}
                  </div>
                </button>
              ))}
            </div>
          )}
        </ScrollArea>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative">
        {/* Top metrics bar */}
        <div className="h-14 border-b flex items-center justify-end px-6 gap-6 bg-background/95 backdrop-blur z-10">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <User className="h-4 w-4" /> <span>{metrics.agents} Agents</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Activity className="h-4 w-4" /> <span>{metrics.workflows} Workflows</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-amber-500 font-medium">
            <Briefcase className="h-4 w-4" /> <span>{metrics.approvals} Approvals</span>
          </div>
        </div>

        {/* Chat Messages */}
        <ScrollArea className="flex-1 p-6">
          <div className="max-w-3xl mx-auto space-y-6 pb-20">
            {messages.length === 0 && !isSubmitting && (
              <div className="text-center mt-20 space-y-4">
                <div className="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Bot className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-xl font-semibold">How can your team help today?</h3>
                <p className="text-muted-foreground max-w-sm mx-auto">
                  Ask the Coordinator to research a topic, manage your emails, or start a new workflow.
                </p>
              </div>
            )}
            
            {messages.map((msg) => (
              <div key={msg.id} className={`flex gap-4 ${msg.sender_type === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${
                  msg.sender_type === 'user' 
                    ? 'bg-primary/20' 
                    : 'bg-primary/10 border border-primary/30'
                }`}>
                  {msg.sender_type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4 text-primary" />}
                </div>
                <div className={`text-[15px] py-3 px-4 rounded-2xl max-w-[80%] whitespace-pre-wrap leading-relaxed shadow-sm ${
                  msg.sender_type === 'user' 
                    ? 'bg-primary text-primary-foreground rounded-tr-sm' 
                    : 'bg-card border border-border rounded-tl-sm'
                }`}>
                  {msg.content}
                </div>
              </div>
            ))}
            
            {isSubmitting && (
              <div className="flex gap-4">
                <div className="h-8 w-8 rounded-full bg-primary/10 border border-primary/30 flex items-center justify-center shrink-0 mt-1">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
                <div className="py-3 px-4 rounded-2xl bg-card border border-border rounded-tl-sm shadow-sm flex items-center gap-1.5 h-12">
                  <span className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce"></span>
                  <span className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="p-4 bg-background border-t">
          <div className="max-w-3xl mx-auto relative">
            <form onSubmit={handleSubmit}>
              <Input 
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
                placeholder="Message Coordinator..." 
                className="pr-12 py-6 text-base rounded-full shadow-sm bg-muted/50 border-muted-foreground/20 focus-visible:ring-primary/50"
                disabled={isSubmitting || !coordinatorId}
              />
              <Button 
                type="submit" 
                size="icon" 
                disabled={isSubmitting || !taskInput.trim() || !coordinatorId} 
                className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-full h-9 w-9"
              >
                {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4 ml-0.5" />}
              </Button>
            </form>
            {!coordinatorId && !isLoadingChats && (
              <p className="text-xs text-destructive text-center mt-2">
                System Coordinator is offline or missing. Please create an agent with coordinator flag.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

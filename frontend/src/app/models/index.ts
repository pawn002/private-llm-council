/**
 * Type definitions for The Sovereign Council frontend.
 * These mirror the backend dataclasses for type safety.
 */

export interface Perspective {
  member_id: string;
  model: string;
  character: string;
  content: string;
  timestamp: string;
}

export interface Critique {
  reviewer_id: string;
  rankings: string[];
  comments: Record<string, string>;
}

export interface Disagreement {
  topic: string;
  positions: Record<string, string>;
  description: string;
  severity?: 'minor' | 'moderate' | 'fundamental';
  implications?: string;
}

export interface MinorityReport {
  member_id: string;
  position: string;
  rationale: string;
}

export interface ConfidenceScore {
  overall: number;
  consensus_strength: number;
  dissent_strength: number;
  reasoning: string;
}

export interface Synthesis {
  content: string;
  consensus_points: string[];
  divisions: string[];
  unique_insights: string[];
  confidence?: ConfidenceScore;
}

export interface Deliberation {
  id: string;
  question: string;
  perspectives: Perspective[];
  critiques: Critique[];
  synthesis: Synthesis;
  disagreements: Disagreement[];
  minority_reports: MinorityReport[];
  timestamp: string;
  session_id: string;
}

export interface PrivacyMode {
  mode: 'SOVEREIGN' | 'SANCTUARY' | 'CITADEL';
  description: string;
}

export interface NetworkStatus {
  external_reachable: boolean;
  ollama_reachable: boolean;
  local_only: boolean;
}

export interface PrivacyStatus {
  mode: PrivacyMode;
  network_status: NetworkStatus;
  warnings: string[];
  verified: boolean;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  ollama_available: boolean;
  available_models: string[];
  council_size: number;
  privacy_mode: string;
}

export type DeliberationPhase =
  | 'idle'
  | 'gathering'
  | 'reviewing'
  | 'synthesizing'
  | 'analyzing'
  | 'complete'
  | 'error';

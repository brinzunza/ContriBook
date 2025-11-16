export enum UserRole {
  MEMBER = "member",
  INSTRUCTOR = "instructor",
  MANAGER = "manager"
}

export enum ContributionType {
  GIT = "git",
  DOCUMENT = "document",
  IMAGE = "image",
  MEETING = "meeting",
  MENTAL = "mental",
  OTHER = "other"
}

export enum ProjectStatus {
  ACTIVE = "active",
  FROZEN = "frozen",
  ARCHIVED = "archived"
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface UserInTeam {
  id: number;
  username: string;
  full_name?: string;
  role: UserRole;
}

export interface Team {
  id: number;
  name: string;
  description?: string;
  invite_code: string;
  status: ProjectStatus;
  created_by: number;
  created_at: string;
  frozen_at?: string;
  member_count?: number;
}

export interface Contribution {
  id: number;
  uuid: string;
  title: string;
  description?: string;
  contribution_type: ContributionType;
  file_path?: string;
  file_hash?: string;
  external_link?: string;
  self_assessed_impact: number;
  reputation_score: number;
  block_id?: number;
  block_hash?: string;
  team_id: number;
  contributor_id: number;
  contributor: UserInTeam;
  verification_count: number;
  flag_count: number;
  verified_by_current_user: boolean;
  flagged_by_current_user: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Verification {
  id: number;
  contribution_id: number;
  verifier_id: number;
  verifier: UserInTeam;
  verifier_role: UserRole;
  comment?: string;
  created_at: string;
}

export interface ReputationBreakdown {
  total_contributions: number;
  verified_contributions: number;
  instructor_verified: number;
  flagged_contributions: number;
  total_score: number;
}

export interface UserReputation {
  user: UserInTeam;
  reputation: ReputationBreakdown;
}

export interface TeamLeaderboard {
  team_id: number;
  team_name: string;
  rankings: UserReputation[];
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

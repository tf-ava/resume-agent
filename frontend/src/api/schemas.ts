export interface ResumeProfile {
  name?: string | null;
  phone?: string | null;
  email?: string | null;
  address?: string | null;

  job_intention?: string | null;
  expected_salary?: string | null;

  years_of_experience?: string | null;
  education_background?: string | null;
  project_experience: string[];
  skills: string[];
}

export interface MatchAnalysis {
  skill_match_score: number;
  experience_relevance_score: number;
  overall_relevance_score: number;
  summary: string;
}

export interface AnalyzeResumeResponse {
  resume_profile: ResumeProfile | null;
  match_analysis: MatchAnalysis | null;
}
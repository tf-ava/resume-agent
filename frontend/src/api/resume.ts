import axios from "axios";
import type { AnalyzeResumeResponse } from "./schemas";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function analyzeResume(
  file: File,
  jobDescription: string
): Promise<AnalyzeResumeResponse> {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("job_description", jobDescription);

  const response = await axios.post<AnalyzeResumeResponse>(
    `${API_BASE_URL}/api/analyze`,
    formData
  );

  return response.data;
}
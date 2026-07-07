import { useState } from "react";
import { Button, Card, Alert, message, Space, Typography } from "antd";

import { analyzeResume } from "../api/resume";
import { getApiErrorMessage } from "../api/error";
import type { AnalyzeResumeResponse } from "../api/schemas";
import ResumeUpload from "./ResumeUpload";
import JobDescriptionInput from "./JobDescriptionInput";
import AnalyzeResult from "./AnalyzeResult";

const { Title, Paragraph } = Typography;

export default function ResumeAnalyzer() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResumeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleAnalyze() {
    if (!file) {
      message.warning("请先上传 PDF 简历");
      return;
    }

    if (!jobDescription.trim()) {
      message.warning("请输入岗位描述");
      return;
    }

    setLoading(true);
    setResult(null);
    setErrorMessage(null);

    try {
      const data = await analyzeResume(file, jobDescription);
      setResult(data);
      message.success("分析完成");
    } catch (error: unknown) {
      const msg = getApiErrorMessage(error);
      setErrorMessage(msg);
      message.error(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <Card>
        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          <div>
            <Title level={2}>简历分析 Agent</Title>
            <Paragraph type="secondary">
              上传 PDF 简历并输入岗位描述，系统会分析简历与岗位的匹配度。
            </Paragraph>
          </div>

          {errorMessage && (
            <Alert
              type="error"
              message="分析失败"
              description={errorMessage}
              showIcon
            />
          )}

          <ResumeUpload onFileChange={setFile} />

          <JobDescriptionInput
            value={jobDescription}
            onChange={setJobDescription}
          />

          <Button
            type="primary"
            loading={loading}
            onClick={handleAnalyze}
            block
          >
            开始分析
          </Button>

          {result && <AnalyzeResult result={result} />}
        </Space>
      </Card>
    </div>
  );
}
import { useState } from "react";
import {
  Alert,
  Button,
  Card,
  Empty,
  message,
  Space,
  Spin,
  Typography,
} from "antd";

import { analyzeResume } from "../api/resume";
import { getApiErrorMessage } from "../api/error";
import type { AnalyzeResumeResponse } from "../api/schemas";
import ResumeUpload from "./ResumeUpload";
import JobDescriptionInput from "./JobDescriptionInput";
import AnalyzeResult from "./AnalyzeResult";

const { Title, Paragraph, Text } = Typography;

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
    <main className="page">
      <header className="page-header">
        <div>
          <Text className="page-kicker">Resume Analysis Agent</Text>
          <Title level={2} className="page-title">
            简历智能分析工作台
          </Title>
          <Paragraph className="page-description">
            上传 PDF 简历并输入岗位描述，系统会提取候选人关键信息，并分析简历与岗位的匹配度。
          </Paragraph>
        </div>
      </header>

      <section className="analyzer-layout">
        <Card className="input-panel" title="分析输入">
          <Space direction="vertical" size="large" style={{ width: "100%" }}>
            <div>
              <Text strong>简历文件</Text>
              <div className="field-help">仅支持 PDF 格式，建议文件大小不超过 10MB。</div>
              <ResumeUpload onFileChange={setFile} />
            </div>

            <div>
              <Text strong>岗位描述</Text>
              <div className="field-help">粘贴岗位职责、技术要求、经验要求等 JD 内容。</div>
              <JobDescriptionInput
                value={jobDescription}
                onChange={setJobDescription}
              />
            </div>

            <Button
              type="primary"
              size="large"
              loading={loading}
              onClick={handleAnalyze}
              block
            >
              开始分析
            </Button>
          </Space>
        </Card>

        <div className="result-panel">
          {errorMessage && (
            <Alert
              className="result-alert"
              type="error"
              message="分析失败"
              description={errorMessage}
              showIcon
            />
          )}

          {loading && (
            <Card className="result-card">
              <div className="loading-state">
                <Spin size="large" />
                <div>
                  <Title level={4}>正在分析简历</Title>
                  <Paragraph type="secondary">
                    正在解析 PDF、提取关键信息并计算岗位匹配度。
                  </Paragraph>
                </div>
              </div>
            </Card>
          )}

          {!loading && !result && !errorMessage && (
            <Card className="result-card">
              <Empty
                description="上传简历并填写岗位描述后，分析结果会显示在这里"
              />
            </Card>
          )}

          {!loading && result && <AnalyzeResult result={result} />}
        </div>
      </section>
    </main>
  );
}
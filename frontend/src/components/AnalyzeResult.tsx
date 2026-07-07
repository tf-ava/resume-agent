import { Card, Descriptions, List, Progress, Space, Typography } from "antd";
import type { AnalyzeResumeResponse } from "../api/schemas";

const { Title, Paragraph } = Typography;

interface AnalyzeResultProps {
  result: AnalyzeResumeResponse;
}

export default function AnalyzeResult({ result }: AnalyzeResultProps) {
  const profile = result.resume_profile;
  const match = result.match_analysis;

  if (!profile || !match) {
    return <Card>分析失败</Card>;
  }

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
            <Card title="岗位匹配分析">
        <Title level={5}>技能匹配率</Title>
        <Progress percent={match.skill_match_score} />

        <Title level={5}>工作经验相关性</Title>
        <Progress percent={match.experience_relevance_score} />

        <Title level={5}>总相关性评分</Title>
        <Progress percent={match.overall_relevance_score} />

        <Paragraph style={{ marginTop: 16 }}>{match.summary}</Paragraph>
      </Card>
      
      <Card title="简历信息">
        <Descriptions column={1} bordered>
          <Descriptions.Item label="姓名">{profile.name ?? "-"}</Descriptions.Item>
          <Descriptions.Item label="电话">{profile.phone ?? "-"}</Descriptions.Item>
          <Descriptions.Item label="邮箱">{profile.email ?? "-"}</Descriptions.Item>
          <Descriptions.Item label="地址">{profile.address ?? "-"}</Descriptions.Item>
          <Descriptions.Item label="求职意向">
            {profile.job_intention ?? "-"}
          </Descriptions.Item>
          <Descriptions.Item label="期望薪资">
            {profile.expected_salary ?? "-"}
          </Descriptions.Item>
          <Descriptions.Item label="工作年限">
            {profile.years_of_experience ?? "-"}
          </Descriptions.Item>
          <Descriptions.Item label="学历背景">
            {profile.education_background ?? "-"}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="技能列表">
        <List
          dataSource={profile.skills}
          renderItem={(item) => <List.Item>{item}</List.Item>}
        />
      </Card>

      <Card title="项目经历">
        <List
          dataSource={profile.project_experience}
          renderItem={(item) => <List.Item>{item}</List.Item>}
        />
      </Card>


    </Space>
  );
}
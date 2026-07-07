import { Input } from "antd";

const { TextArea } = Input;

interface JobDescriptionInputProps {
  value: string;
  onChange: (value: string) => void;
}

export default function JobDescriptionInput({
  value,
  onChange,
}: JobDescriptionInputProps) {
  return (
    <TextArea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="请输入岗位描述，例如岗位职责、技术要求、经验要求等"
      rows={8}
      showCount
      maxLength={5000}
    />
  );
}
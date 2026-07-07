import { Upload } from "antd";
import type { UploadProps } from "antd";

interface ResumeUploadProps {
  onFileChange: (file: File | null) => void;
}

export default function ResumeUpload({ onFileChange }: ResumeUploadProps) {
  const props: UploadProps = {
    accept: ".pdf",
    maxCount: 1,
    beforeUpload: (file) => {
      onFileChange(file);
      return false;
    },
    onRemove: () => {
      onFileChange(null);
    },
  };

  return (
    <Upload.Dragger {...props}>
      <p>点击或拖拽 PDF 简历到这里上传</p>
      <p style={{ color: "#888" }}>仅支持 PDF 文件</p>
    </Upload.Dragger>
  );
}
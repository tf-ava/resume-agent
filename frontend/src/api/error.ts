import axios from "axios";

export function getApiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return "发生未知错误";
  }

  const detail = error.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (detail && typeof detail === "object" && "message" in detail) {
    return String(detail.message);
  }

  return "请求失败，请稍后重试";
}
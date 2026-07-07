# Resume Agent

一个基于大模型的简历分析 Agent。用户在前端上传 PDF 简历并输入岗位描述后，后端会解析简历文本、提取结构化简历信息，并进一步分析简历与岗位描述的匹配度，最终返回结构化分析结果。

## 功能特性

- PDF 简历上传与岗位描述输入
- 使用 `pymupdf4llm` 将 PDF 简历解析为 Markdown 文本
- 对解析后的 Markdown 进行轻量清洗
- 使用 LiteLLM 统一调用大模型接口
- 使用 Pydantic 约束大模型结构化输出
- 两阶段 Agent 分析流程：
  - 简历信息提取 Agent：从简历文本中提取姓名、联系方式、求职意向、教育背景、项目经历、技能等信息
  - 岗位匹配分析 Agent：结合结构化简历信息和岗位描述，输出技能匹配度、经验相关性、整体相关性和总结
- 使用 Redis 缓存分析结果，减少重复 PDF 解析和重复大模型调用
- 前端使用 React + Vite + Ant Design 构建交互页面
- 支持后端部署到阿里云，前端部署到 GitHub Pages

## 项目架构

```text
resume-agent/
├── backend/
│   ├── src/
│   │   └── resume_agent/
│   │       ├── api/
│   │       │   └── resume_analyze.py        # 简历分析 API
│   │       ├── pdf_parser/
│   │       │   ├── parsed_by_pymupdf4llm.py # PDF 解析
│   │       │   └── clean.py                 # Markdown 清洗
│   │       ├── cache.py                     # Redis 缓存工具
│   │       ├── redis.py                     # Redis 客户端
│   │       ├── llm.py                       # LiteLLM 调用与结构化输出校验
│   │       ├── prompt.py                    # Agent Prompt
│   │       ├── schemas.py                   # Pydantic 数据模型
│   │       └── main.py                      # FastAPI 应用入口
│   ├── pyproject.toml
│   ├── uv.lock
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── resume.ts                    # Axios 请求封装
│   │   │   ├── schemas.ts                   # 前端类型定义
│   │   │   └── error.ts                     # 错误处理
│   │   ├── components/
│   │   │   ├── ResumeAnalyzer.tsx           # 主页面
│   │   │   ├── ResumeUpload.tsx             # 简历上传
│   │   │   ├── JobDescriptionInput.tsx      # 岗位描述输入
│   │   │   └── AnalyzeResult.tsx            # 分析结果展示
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

## 技术选型

### 后端

| 技术 | 说明 |
| --- | --- |
| FastAPI | 提供 REST API，接收 PDF 文件和岗位描述 |
| PyMuPDF / pymupdf4llm | 解析 PDF 简历并转换为 Markdown |
| LiteLLM | 统一大模型调用接口，便于切换模型服务商 |
| Pydantic | 定义结构化输出 Schema，并校验大模型返回结果 |
| Redis | 缓存重复分析结果，降低响应时间和模型调用成本 |
| uv | Python 依赖管理与运行环境管理 |

### 前端

| 技术 | 说明 |
| --- | --- |
| React | 构建前端交互页面 |
| Vite | 前端开发与构建工具 |
| Ant Design | UI 组件库 |
| Axios | 与后端 API 交互 |
| TypeScript | 类型约束，提高可维护性 |

## 核心流程

```text
用户上传 PDF 简历 + 输入岗位描述
        |
        v
FastAPI 接收 multipart/form-data
        |
        v
根据 PDF 内容和岗位描述生成缓存 Key
        |
        v
查询 Redis 是否存在完整分析结果
        |
        ├── 命中：直接返回 AnalyzeResumeResponse
        |
        └── 未命中：
              |
              v
        pymupdf4llm 解析 PDF
              |
              v
        清洗 Markdown 文本
              |
              v
        Agent 1：提取 ResumeProfile
              |
              v
        Agent 2：分析 MatchAnalysis
              |
              v
        写入 Redis 缓存
              |
              v
        返回结构化结果
```

## 结构化输出

后端使用 Pydantic 定义结构化结果，并要求大模型通过工具调用返回符合 Schema 的数据。

主要响应结构：

```json
{
  "resume_profile": {
    "name": "string",
    "phone": "string",
    "email": "string",
    "address": "string",
    "job_intention": "string",
    "expected_salary": "string",
    "years_of_experience": "string",
    "education_background": "string",
    "project_experience": ["string"],
    "skills": ["string"]
  },
  "match_analysis": {
    "skill_match_score": 85,
    "experience_relevance_score": 80,
    "overall_relevance_score": 82,
    "summary": "候选人与岗位整体匹配度较高..."
  }
}
```

## Redis 缓存设计

本项目中 Redis 作为缓存层，而不是主数据库。

缓存目标：

- 避免同一份简历和同一份岗位描述重复调用大模型
- 降低接口响应时间
- 降低大模型 API 调用成本

缓存 Key：

```
resume_analysis:{pdf_hash}:{jd_hash}
```

其中：

- `pdf_hash` 由 PDF 文件内容计算得到，不能使用文件名作为缓存 Key
- `jd_hash` 由岗位描述文本计算得到
- 缓存 Value 为 `AnalyzeResumeResponse` 的 JSON 字符串
- 缓存需要设置 TTL，避免长期保存简历敏感信息

默认TTL：

```
2分钟
可在backend的.env文件中配置
```



## 本地开发

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd resume-agent
```

### 2. 启动 Redis

如果本地安装了 Docker，可以直接运行：

```bash
docker run -d --name resume-agent-redis -p 6379:6379 redis:7-alpine
```

验证 Redis 是否正常：

```bash
docker exec -it resume-agent-redis redis-cli ping
```

返回 `PONG` 表示启动成功。

### 3. 配置后端环境变量

复制后端环境变量示例：

```bash
cd backend
cp .env.example .env
```

`.env` 示例：

```env
OPENROUTER_API_KEY=your_openrouter_api_key
BASE_URL=https://openrouter.ai/api/v1
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=60 * 2
```

说明：

- `OPENROUTER_API_KEY`：大模型服务 API Key
- `BASE_URL`：LiteLLM 调用的大模型服务地址
- `REDIS_URL`：Redis 连接地址
- `CACHE_TTL_SECONDS`:缓存保存时间

### 4. 启动后端

后端使用 `uv` 管理依赖：

```bash
cd backend
uv sync
uv run uvicorn src.resume_agent.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：

```text
http://localhost:8000/docs
```

### 5. 启动前端

安装依赖：

```bash
cd frontend
npm install
```

开发环境变量 `frontend/.env.development`：

```env
VITE_API_BASE_URL=http://localhost:8000
```

启动前端：

```bash
npm run dev
```

默认访问：

```text
http://localhost:5173
```

## API 使用说明

### 简历分析接口

```text
POST /api/analyze
```

请求类型：

```text
multipart/form-data
```

请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| file | PDF 文件 | 是 | 用户上传的简历 |
| job_description | string | 是 | 岗位描述 |

响应：

```json
{
  "resume_profile": {
    "name": "张三",
    "phone": "13800000000",
    "email": "zhangsan@example.com",
    "address": "上海",
    "job_intention": "后端开发工程师",
    "expected_salary": "面议",
    "years_of_experience": "3 年",
    "education_background": "本科",
    "project_experience": ["项目 A", "项目 B"],
    "skills": ["Python", "FastAPI", "Redis", "Docker"]
  },
  "match_analysis": {
    "skill_match_score": 88,
    "experience_relevance_score": 82,
    "overall_relevance_score": 85,
    "summary": "候选人的 Python、FastAPI 和 Redis 技能与岗位要求匹配度较高。"
  }
}
```


## 项目定位

本项目不是传统简历管理系统，而是一个面向岗位匹配场景的简历分析 Agent。它的核心价值是利用大模型完成非结构化简历文本到结构化候选人画像的转换，并进一步结合岗位描述给出可解释的匹配度分析。

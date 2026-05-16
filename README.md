# 简历解析与岗位匹配系统

PDF 简历上传 → 关键信息提取 → 岗位匹配评分，一站式简历处理服务。

## 项目结构

```
├── web 分支（前端页面）
│   └── web.html           单页应用，部署于 GitHub Pages
│
├── back 分支（后端服务）
│   ├── main.py            Flask 服务入口，端口 9000
│   ├── pdf_parser.py      PDF 文本提取与清洗
│   ├── info_extractor.py  关键字段正则提取
│   ├── matcher.py         TF-IDF + 余弦相似度匹配
│   └── requirements.txt   Python 依赖
│
└── main 分支（文档）
    └── README.md
```

## 功能模块

### 模块一：简历上传与解析
- 接口：`POST /api/upload-resume`
- 支持单文件 PDF 上传，兼容多页简历
- pdfplumber 提取文本，清洗冗余符号，保留中英文标点

### 模块二：关键信息提取
- 接口：`POST /api/extract-info`
- 必选字段：姓名、电话、邮箱、地址
- 加分项：学历、工作年限、求职意向、期望薪资、项目经历

### 模块三：简历评分与匹配
- 接口：`POST /api/match-jd`
- JD 关键词提取，TF-IDF 文本向量化
- 余弦相似度 + 技能匹配率综合评分（0-100）

### 模块四：结果返回与缓存
- 统一 JSON 结构返回：`{ code, msg, data }`
- Redis 缓存已解析结果，连接失败自动降级

### 模块五：前端页面
- 纯 HTML/CSS/JS 单页应用，无框架依赖
- 三段式交互：上传解析 → 信息展示 → 岗位匹配
- 支持拖拽上传、移动端适配
- 部署于 GitHub Pages

## 本地运行

```bash
# 克隆仓库
git clone https://github.com/hai-word/resume.git
cd resume
git checkout back

# 创建虚拟环境
python -m venv .venv
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # Mac/Linux

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
# 服务运行于 http://127.0.0.1:9000
```

## API 文档

### 上传简历
```
POST /api/upload-resume
Content-Type: multipart/form-data
参数: file (PDF)

响应: { "code": 200, "data": { "text": "...", "length": 1234 } }
```

### 提取信息
```
POST /api/extract-info
Content-Type: application/json
参数: { "text": "简历文本内容" }

响应: {
  "code": 200,
  "data": {
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@qq.com",
    "address": "北京市",
    "education": "本科",
    "work_years": 5,
    "job_intention": "后端开发",
    "expected_salary": "20K-30K",
    "projects": ["项目一描述", "项目二描述"]
  }
}
```

### 岗位匹配
```
POST /api/match-jd
Content-Type: application/json
参数: { "resume_text": "...", "jd": "岗位描述文本" }

响应: {
  "code": 200,
  "data": {
    "basic_info": { ... },
    "background": { ... },
    "match_result": {
      "match_score": 75,
      "skill_match_rate": 0.67,
      "similarity": 0.52,
      "matched_keywords": ["Python", "Django"],
      "jd_keywords": ["Python", "Django", "Java"]
    }
  }
}
```

## 前端部署

前端页面部署在 GitHub Pages，访问地址：

```
https://hai-word.github.io/resume/web.html
```

部署后需将 `web.html` 中 `API_BASE` 修改为后端公网地址。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端框架 | Flask 2.3 |
| PDF 解析 | pdfplumber 0.10 |
| 文本匹配 | scikit-learn (TF-IDF + Cosine) |
| 缓存 | Redis（可选，不可用时自动降级） |
| 前端 | 原生 HTML/CSS/JS，零依赖 |
| 部署 | GitHub Pages（前端）+ 云服务器（后端） |

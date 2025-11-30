# ☭ 智慧党建理论学习系统 (AI-Powered Smart Party Learning System)

> 基于大模型 (LLM) + 检索增强生成 (RAG) + 语音合成 (TTS) 的智能化政治理论学习平台。

## 📖 项目简介

本项目旨在解决传统政治理论学习中“内容枯燥、形式单一、缺乏互动”的痛点。通过上传 PPT 课件，系统能够：
1. **智能解析**：提取 PPT 图文内容。
2. **知识增强**：基于 RAG 技术，自动检索“人民网”、“学习强国”等权威政策库，生成深度解读。
3. **语音伴学**：生成高保真语音讲解。
4. **互动问答**：内置 AI 助教，支持针对内容的实时问答。

## 🛠️ 技术栈

- **后端框架**: FastAPI (Python 3.10+)
- **大模型基座**: 智谱 AI (ChatGLM-4 / Flash)
- **RAG 引擎**: LangChain + ChromaDB (向量数据库)
- **语音合成**: Edge-TTS
- **前端界面**: Vue 3 + Bootstrap 5
- **数据处理**: python-pptx, BeautifulSoup4

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/你的用户名/SmartPartyLearning.git
cd SmartPartyLearning

2. 安装依赖
code
Bash
pip install -r requirements.txt
3. 配置 API Key
打开 rag_engine.py，填入你的智谱 AI API Key：
code
Python
ZHIPU_API_KEY = "你的_key_填在这里"
4. 运行系统
code
Bash
python main.py
浏览器访问: http://127.0.0.1:8000
📂 目录结构
code
Text
├── knowledge_db/    # 权威政策知识库 (TXT文件)
├── static/          # 前端页面与音频资源
├── main.py          # 后端启动入口
├── rag_engine.py    # RAG 核心逻辑
├── ppt_processor.py # PPT 解析模块
├── tool_crawler.py  # 权威数据爬虫工具
└── requirements.txt # 项目依赖
✨ 核心亮点
垂直领域 RAG: 解决了大模型在政治理论领域的“幻觉”问题。
全流程自动化: 上传即生成，无需人工干预。
鲁棒性设计: 针对 Windows 环境优化了编码与反爬策略。
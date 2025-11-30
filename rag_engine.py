import os
from zhipuai import ZhipuAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

# ================= 配置区 =================
# 请填入你的 API KEY
# 请在此处填入你的智谱AI API Key
ZHIPU_API_KEY = "YOUR_API_KEY_HERE"
# 向量数据库保存路径
DB_PATH = "./chroma_db"
# 知识库源文件路径
DATA_PATH = "./knowledge_db"
# =========================================

client = ZhipuAI(api_key=ZHIPU_API_KEY)

class SimpleZhipuAIEmbeddings:
    def __init__(self, api_key):
        self.client = ZhipuAI(api_key=api_key)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            response = self.client.embeddings.create(
                model="embedding-2", 
                input=text
            )
            embeddings.append(response.data[0].embedding)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model="embedding-2",
            input=text
        )
        return response.data[0].embedding

embedding_model = SimpleZhipuAIEmbeddings(api_key=ZHIPU_API_KEY)

class KnowledgeBase:
    def __init__(self):
        self.vector_store = None
        self._init_vector_db()

    def _init_vector_db(self):
        if os.path.exists(DB_PATH) and os.listdir(DB_PATH):
            # 加载现有库，不打印日志
            self.vector_store = Chroma(
                persist_directory=DB_PATH, 
                embedding_function=embedding_model
            )
        else:
            # 构建新库
            self._build_index()

    def _build_index(self):
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)
            return

        documents = []
        for filename in os.listdir(DATA_PATH):
            if filename.endswith(".txt"):
                file_path = os.path.join(DATA_PATH, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    documents.append(Document(page_content=text, metadata={"source": filename}))
        
        if not documents:
            return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = text_splitter.split_documents(documents)
        
        self.vector_store = Chroma.from_documents(
            documents=split_docs,
            embedding=embedding_model,
            persist_directory=DB_PATH
        )

    def search(self, query, top_k=3):
        if not self.vector_store:
            return "（知识库为空，暂无参考资料）"
            
        docs = self.vector_store.similarity_search(query, k=top_k)
        
        context_str = ""
        for i, doc in enumerate(docs):
            context_str += f"\n【参考资料{i+1}】：{doc.page_content}\n"
        
        return context_str

def generate_lecture(ppt_text, knowledge_base: KnowledgeBase):
    # RAG 检索
    context = knowledge_base.search(ppt_text[:100])
    
    # 删除了这里的 print DEBUG 语句，这是罪魁祸首！

    prompt = f"""
    你是一名党建理论讲师。请根据[PPT原稿]和[权威参考资料]，生成一段大约200字的讲解词。
    
    【PPT原稿】：
    {ppt_text}
    
    【权威参考资料】：
    {context}
    
    要求：
    1. 必须基于[参考资料]中的理论对[PPT原稿]进行升华。
    2. 如果PPT内容与政治无关，请尝试寻找其与国家战略的结合点。
    3. 口语化，自然流畅。
    """
    
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
    )
    
    return response.choices[0].message.content
# --- 新增：智能问答功能 ---
def ask_smart_tutor(question, ppt_context, knowledge_base: KnowledgeBase):
    """
    智能助教：根据用户问题 + PPT当前页内容 + 知识库 RAG -> 生成回答
    """
    # 1. 拿着用户的问题去知识库搜一搜背景
    kb_context = knowledge_base.search(question)
    
    # 2. 构建 Prompt
    prompt = f"""
    你是一名智慧党建系统的智能辅导员。
    
    【当前学习的PPT片段】：
    {ppt_context}
    
    【知识库背景资料】：
    {kb_context}
    
    【学员提问】：{question}
    
    请结合PPT内容和背景资料，用简洁、专业、鼓励性的语气回答学员。
    如果问题与政治理论无关，请礼貌地引导回主题。
    """
    
    # 3. 调用模型 (继续用免费的 flash 模型)
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
    )
    
    return response.choices[0].message.content
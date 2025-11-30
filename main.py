import sys
import io
import os
import uuid
import traceback
import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- 强行设置控制台为 utf-8，专治 Windows 乱码报错 ---
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# --------------------------------------------------

# 导入我们的本地模块
# 确保 rag_engine.py 里已经添加了 ask_smart_tutor 函数
from ppt_processor import extract_content_from_ppt
from rag_engine import KnowledgeBase, generate_lecture, ask_smart_tutor 
from tts_service import text_to_speech

app = FastAPI(title="智慧党建学习系统")

# 1. 允许跨域（方便前端调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 挂载静态文件目录 (用于访问生成的音频和 index.html)
# 确保项目根目录下有 static 文件夹
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. 初始化知识库 (系统启动时加载)
print("正在初始化知识库，请稍候...")
kb = KnowledgeBase()
print("知识库初始化完成！")

# --- 定义请求数据模型 ---
class AskRequest(BaseModel):
    question: str
    ppt_context: str

# ================= 路由接口区 =================

@app.get("/")
async def read_index():
    """
    访问根路径时，直接返回前端网页
    """
    return FileResponse('static/index.html')

@app.post("/upload_ppt")
async def process_ppt(file: UploadFile = File(...)):
    """
    核心接口：上传PPT -> 解析 -> RAG生成讲解 -> TTS转语音
    """
    # 1. 生成纯英文的随机文件名，避免中文路径报错
    file_ext = os.path.splitext(file.filename)[1]
    if not file_ext:
        file_ext = ".pptx"
    
    random_filename = f"temp_{uuid.uuid4()}{file_ext}"

    try:
        # 2. 保存上传的文件
        async with aiofiles.open(random_filename, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # 3. 解析 PPT 内容
        print(f"正在解析文件: {random_filename} ...")
        slides = extract_content_from_ppt(random_filename)
        
        result_data = []
        
        # 4. 逐页处理 (为了演示速度，这里限制处理前 5 页，你可以去掉切片 [:5])
        # 如果 PPT 很大，生成时间会很长，建议保留这个限制用于答辩演示
        for slide in slides[:5]: 
            # RAG + LLM 生成讲解词
            script = generate_lecture(slide['text'], kb)
            
            # TTS 生成语音 (返回的是相对路径)
            # --- 容错处理：如果语音生成失败，不要崩，继续显示文字 ---
            try:
                audio_url = await text_to_speech(script)
            except Exception as e:
                print(f"⚠️ 语音合成失败 (可能是网络原因)，已跳过: {e}")
                audio_url = "" # 给个空值，前端就不会报错了
            # ---------------------------------------------------
            
            result_data.append({
                "page": slide['page'],
                "ppt_text": slide['text'],
                "ai_script": script,
                "audio_url": audio_url
            })
            
        return {"status": "success", "data": result_data}
        
    except Exception as e:
        # 捕获所有错误并打印详细堆栈，方便调试
        error_str = traceback.format_exc()
        print("\n\n################ ERROR DETAILS ################")
        print(error_str)
        print("###############################################\n\n")
        return {"status": "error", "message": str(e)}
        
    finally:
        # 5. 清理临时文件
        if os.path.exists(random_filename):
            os.remove(random_filename)

@app.post("/ask_ai")
async def api_ask_ai(req: AskRequest):
    """
    智能问答接口：用户提问 -> RAG检索 -> AI回答
    """
    try:
        # 调用 rag_engine 里的问答函数
        answer = ask_smart_tutor(req.question, req.ppt_context, kb)
        return {"status": "success", "answer": answer}
    except Exception as e:
        print(f"问答接口出错: {e}")
        return {"status": "error", "message": str(e)}

# ================= 启动入口 =================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
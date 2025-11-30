import requests
from bs4 import BeautifulSoup
import os
import time

# 数据保存路径
SAVE_DIR = "knowledge_db"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def fetch_article(url, source_name="权威媒体"):
    # 伪装成浏览器（很重要！）
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # 强制不走代理
    proxies = { "http": None, "https": None }
    
    try:
        print(f"🕸️ 正在尝试抓取: {url} ...")
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
        
        # --- 核心修复：自动检测编码，防止乱码 ---
        response.encoding = response.apparent_encoding 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- 核心修复：暴力提取法 ---
        # 1. 移除 script 和 style 标签（也就是移除代码和样式，只留文字）
        for script in soup(["script", "style"]):
            script.extract()    

        # 2. 获取页面所有文本
        text = soup.get_text()

        # 3. 按行分割，去除多余空白
        lines = (line.strip() for line in text.splitlines())
        # 4. 把每一行重新拼起来，只保留长度大于 50 的段落（过滤掉菜单、页脚）
        chunks = [phrase.strip() for phrase in lines if len(phrase.strip()) > 50]
        
        full_text = "\n\n".join(chunks)
        
        if len(full_text) < 100:
            print("⚠️ 内容过短，可能抓取失败。")
            return

        # 获取标题
        title = soup.title.string if soup.title else f"未知文章_{int(time.time())}"
        
        # 保存
        filename = f"{source_name}_{int(time.time())}.txt"
        file_path = os.path.join(SAVE_DIR, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"【来源】：{source_name}\n")
            f.write(f"【链接】：{url}\n")
            f.write(f"【标题】：{title}\n\n")
            f.write(full_text)
            
        print(f"✅ 成功保存！({len(full_text)}字)")
        
    except Exception as e:
        print(f"❌ 抓取出错: {e}")

if __name__ == "__main__":
    # 使用一些更容易抓取的页面
    urls = [
        ("人民网_数字经济", "http://politics.people.com.cn/n1/2024/0101/c1001-40150338.html"),
        ("新华网_高质量发展", "http://www.news.cn/politics/20240305/4e3415053426463994a0256860057068/c.html")
    ]
    
    print("=== 开始构建权威知识库 ===")
    for source, link in urls:
        fetch_article(link, source)
        time.sleep(2) 
    
    print("\n🎉 任务结束！请重启 main.py")
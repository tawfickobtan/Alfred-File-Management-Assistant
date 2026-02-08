import json
import os
import subprocess
import time
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from sentence_transformers import SentenceTransformer


forbidden = [
    "agent.py",
    "config.json",
    "llm.py",
    "README.md",
    "tools.json",
    "tools.py",
    ".gitignore",
    ".git",
    "system_prompt.txt",
    "requirements.txt"
]

# Load memory file
memory = {}
try:
    with open("memory.json", "r", encoding="utf-8") as f:
        memory = json.load(f)
except Exception as e:
    memory = {}

vector_embeddings = {}
try:
    with open("vector_embeddings.json", "r", encoding="utf-8") as f:
        vector_embeddings = json.load(f)
except Exception as e:
    vector_embeddings = {}
_embedding_model = None

vector_memory = {}
try:
    with open("vector_memory.json", "r", encoding="utf-8") as f:
        vector_memory = json.load(f)
except Exception as e:
    vector_memory = {}


def getItemsInPath(path: str) -> str:
    try:
        items = os.listdir(path)
        return "\n".join(items)
    except Exception as e:
        return "Error occured. " + str(e)

def createFile(file: str) -> str:
    if file in forbidden:
        return "You are not allowed to create these files."
    try:
        with open(file, "w", encoding="utf-8") as f:
            pass
        return "File created successfully."
    except Exception as e:
        return "Error occured: " + str(e)

def writeIntoFile(file: str, content: str) -> str:
    if file in forbidden:
        return "You are not allowed to modify these files."
    try:
        with open(file, "w", encoding="utf-8") as f:
            f.write(content)
        return "Wrote content into file successfully."
    except Exception as e:
        return "Error occured: " + str(e)
    
def readFile(file: str) -> str:
    try:
        with open(file, "r", encoding="utf-8") as f:
            output = f.read()
        return "content:\n" + output    
    except Exception as e:
        return "Error occured. " + str(e)

def delete(file: str) -> str:  
    if file in forbidden:
        return "You are not allowed to delete these files."
    try:
        os.remove(file)
        return "File deleted successfully."
    except Exception as e:
        return "Error occured: " + str(e)

def createDirectory(directory: str) -> str:
    try:
        os.makedirs(directory, exist_ok=True)
        return "Directory created successfully."
    except Exception as e:
        return "Error occured: " + str(e)

def deleteDirectory(directory: str) -> str:
    if directory in forbidden:
        return "You are not allowed to delete these directories."
    try:
        os.rmdir(directory)
        return "Directory deleted successfully."
    except Exception as e:
        return "Error occured: " + str(e)

def moveFile(source: str, destination: str) -> str:
    if source in forbidden or destination in forbidden:
        return "You are not allowed to move these files."
    try:
        os.rename(source, destination)
        return "File moved successfully."
    except Exception as e:
        return "Error occured: " + str(e)

def copyFile(source: str, destination: str) -> str:
    if source in forbidden or destination in forbidden:
        return "You are not allowed to copy these files."
    try:
        import shutil
        shutil.copy2(source, destination)
        return "File copied successfully."
    except Exception as e:
        return "Error occured: " + str(e)
    
def getCurrentDirectory() -> str:
    try:
        cwd = os.getcwd()
        return cwd
    except Exception as e:
        return "Error occured. " + str(e)

def runCommand(command: str) -> str:
    userInput = input("Are you sure you want to run this command? (y/n): ")
    if userInput.lower().strip() != "y":
        return "Command execution cancelled by user."
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        output = result.stdout
        return output
    except Exception as e:
        return "Error occured. " + str(e)

def fileExists(file: str) -> str:
    try:
        return ("Yes, " + file + " exists.") if os.path.exists(file) else ("No, " + file + " does not exist.")
    except Exception as e:
        return "Error occured: " + str(e)

def getFileSize(file: str) -> str:
    try:
        size = os.path.getsize(file)
        return f"Size of {file} is {size} bytes."
    except Exception as e:
        return "Error occured: " + str(e)

def readPDF(path: str) -> str:
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return "content:\n" + text
    except Exception as e:
        return "Error occured: " + str(e)
    
def renameFile(source: str, new_name: str) -> str:
    if source in forbidden or new_name in forbidden:
        return "You are not allowed to rename these files."
    try:
        os.rename(source, new_name)
        return "File renamed successfully."
    except Exception as e:
        return "Error occured: " + str(e)
    
# Tool functions for memory management 
    
def rememberFact(key: str, fact: str) -> str:
    memory[key] = fact
    try:
        with open("memory.json", "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=4)
        return "Fact remembered successfully."
    except Exception as e:
        return "Error occured: " + str(e)

def recallFact(key: str) -> str:
    try:
        fact = memory.get(key, "No fact found for the given key.")
        return fact
    except Exception as e:
        return "Error occured: " + str(e)

def forgetFact(key: str) -> str:
    try:
        if key in memory:
            del memory[key]
            with open("memory.json", "w", encoding="utf-8") as f:
                json.dump(memory, f, indent=4)
            return "Fact forgotten successfully."
        else:
            return "No fact found for the given key."
    except Exception as e:
        return "Error occured: " + str(e)
    
def listMemories() -> str:
    try:
        if memory:
            facts = "\n".join([f"{k}: {v}" for k, v in memory.items()])
            return facts
        else:
            return "No memories stored."
    except Exception as e:
        return "Error occured: " + str(e)
    
# Tool functions for web interaction
    
def searchWeb(query: str, k: int = 3) -> str:
    try:
        from urllib.parse import quote_plus
        import requests
        
        encoded = quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        with open("temp.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.find_all('div', class_='result'):
            title = result.find('a', class_='result__a')
            if title:
                results.append(title.get_text() + "\n(Link: " + title.get("href", "None") + ")")
            if len(results) >= k:
                break
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return "Error occured: " + str(e)
    
def extractTextFromUrl(url: str) -> str:
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from bs4 import BeautifulSoup
        import re
        
        # Setup headless Chrome
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        # Wait a bit for JS to load
        import time
        time.sleep(3)
        
        html = driver.page_source
        driver.quit()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Try to find main content using common patterns (in order of preference)
        content = (
            soup.find('article') or           # Most modern sites use <article>
            soup.find('main') or              # HTML5 semantic tag
            soup.find('div', id='content') or # Common pattern
            soup.find('div', class_='content') or
            soup.find('div', id='main') or
            soup.find('div', class_='main') or
            soup.body                         # Last resort: entire body
        )
        
        if not content:
            return "Could not find main content area."
        
        # Remove unwanted elements (noise)
        unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']
        for tag in unwanted_tags:
            for element in content.find_all(tag):
                element.decompose()
        
        # Get all paragraph text (usually the main content)
        paragraphs = content.find_all('p')
        text = '\n\n'.join([p.get_text(' ', strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # If no paragraphs found, get all text
        if not text:
            text = content.get_text(' ', strip=True)
        
        # Clean up excessive whitespace/newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Limit length to prevent overwhelming the LLM
        if len(text) > 8000:
            text = text[:8000] + "\n\n[Content truncated...]"
        
        return text if text else "No readable content found."
        
    except Exception as e:
        return f"Error extracting webpage: {str(e)}"

# Tool functions for embedding memory management
def _get_embedding_model():
    """Lazy loads the sentence transformer model only when needed"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model

def _compute_embedding(text: str) -> list:
    model = _get_embedding_model()
    embedding = model.encode(text).tolist()
    return embedding

def _cosine_similarity(vecA: list, vecB: list) -> float:
    import numpy as np
    a = np.array(vecA)
    b = np.array(vecB)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def addVectorMemory(text: str) -> str:
    embedding = _compute_embedding(text)
    id = int(time.time() * 1000)
    vector_embeddings[str(id)] = embedding
    vector_memory[str(id)] = text
    try:
        with open("vector_embeddings.json", "w", encoding="utf-8") as f:
            json.dump(vector_embeddings, f, indent=4)
        with open("vector_memory.json", "w", encoding="utf-8") as f:
            json.dump(vector_memory, f, indent=4)
        return "Vector memory added successfully."
    except Exception as e:
        return "Error occured: " + str(e)

def queryVectorMemory(query: str, k: int = 3) -> str:
    query_embedding = _compute_embedding(query)
    similarities = []
    for id, embedding in vector_embeddings.items():
        sim = _cosine_similarity(query_embedding, embedding)
        similarities.append((sim, id))
    similarities.sort(reverse=True, key=lambda x: x[0])
    top_k = similarities[:k]
    results = []
    for sim, id in top_k:
        results.append(f"Memory: {vector_memory[id]}\nSimilarity: {sim:.4f}")
    return "\n\n".join(results) if results else "No relevant memories found."
    




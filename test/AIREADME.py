import os
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

class CodeAnalyzer:
    """代码分析器"""

    def __init__(self, model="gpt-3.5-turbo"):
        api_key = os.environ.get("OPENAI_API_KEY", "sk-lwkQzJYwYdJwbQ4DaAlM3Ti6pgMCzEgztBjREyOlYFPLPDQP")
        if not api_key:
            raise RuntimeError("未检测到 OPENAI_API_KEY 环境变量，请先设置API密钥")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.chatanywhere.tech/v1"
        )
        self.model = model
        self.lock = threading.Lock()
    
    def analyze_code(self, file_path, code_content):
        """分析Python代码
        
        Args:
            file_path: 文件路径
            code_content: 代码内容
            
        Returns:
            dict: 包含分析结果的字典
        """
        prompt = f"""请分析以下Python代码，提供详细的分析报告。代码来自文件: {file_path}

请按照以下结构返回JSON格式的分析结果：
- function_summary: 主要函数/方法的简要说明
- key_features: 代码的核心功能特性（列表形式）
- complexity_analysis: 代码复杂度分析（简单/中等/复杂）
- improvement_suggestions: 改进建议（列表形式）
- potential_issues: 潜在问题或风险点（列表形式）

代码内容：
{code_content[:4000]}  # 限制内容长度
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的代码分析专家，擅长分析Python代码的结构、功能和优化点。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            result_text = (response.choices[0].message.content or "").strip()
            
            # 解析JSON响应
            analysis_data = self._parse_json_response(result_text)
            
            # 构建分析结果
            analysis_result = {
                "file_path": file_path,
                "function_summary": analysis_data.get("function_summary", "无总结"),
                "key_features": analysis_data.get("key_features", []),
                "complexity_analysis": analysis_data.get("complexity_analysis", "未知"),
                "improvement_suggestions": analysis_data.get("improvement_suggestions", []),
                "potential_issues": analysis_data.get("potential_issues", [])
            }
            
            with self.lock:
                print(f"✅ 已完成分析: {file_path}")
            
            return analysis_result
            
        except Exception as e:
            with self.lock:
                print(f"❌ 分析失败 {file_path}: {str(e)}")
            
            return {
                "file_path": file_path,
                "function_summary": f"分析失败: {str(e)}",
                "key_features": [],
                "complexity_analysis": "未知",
                "improvement_suggestions": [],
                "potential_issues": []
            }
    
    def _parse_json_response(self, response_text):
        """解析AI返回的JSON响应"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                return {
                    "function_summary": "JSON解析失败",
                    "key_features": ["无法解析AI响应"],
                    "complexity_analysis": "未知",
                    "improvement_suggestions": ["检查AI响应格式"],
                    "potential_issues": ["AI响应格式异常"]
                }

def merge_py_to_markdown(root_dir, max_workers=3):
    """合并Python文件并生成代码分析报告（多线程版本）"""
    
    # 初始化代码分析器
    analyzer = CodeAnalyzer()
    
    # 目标 Markdown 文件路径
    output_dir = os.path.join(root_dir, "")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "AI_code_analysis.md")

    # 收集所有Python文件
    python_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        if os.path.abspath(dirpath) == os.path.abspath(output_dir):
            continue
        for file in filenames:
            if file.endswith(".py"):
                filepath = os.path.join(dirpath, file)
                rel_path = os.path.relpath(filepath, root_dir)
                python_files.append((rel_path, filepath))

    print(f"🔍 找到 {len(python_files)} 个Python文件，开始分析...")

    # 多线程分析文件
    analysis_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_file = {}
        for rel_path, filepath in python_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    code_content = f.read()
                
                # 跳过空文件或过小的文件
                if len(code_content.strip()) < 10:
                    continue
                
                # 提交分析任务
                future = executor.submit(analyzer.analyze_code, rel_path, code_content)
                future_to_file[future] = (rel_path, filepath, code_content)
                
            except Exception as e:
                print(f"❌ 读取文件失败 {rel_path}: {e}")

        # 收集完成的任务
        for future in as_completed(future_to_file):
            rel_path, filepath, code_content = future_to_file[future]
            try:
                result = future.result()
                analysis_results.append((rel_path, filepath, code_content, result))
            except Exception as e:
                print(f"❌ 任务执行失败 {rel_path}: {e}")

    # 按文件路径排序结果
    analysis_results.sort(key=lambda x: x[0])

    # 生成Markdown报告
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# AI代码分析报告\n\n")
        out.write("> 本文档由AI自动分析项目中的Python代码并生成详细报告\n\n")
        out.write(f"## 项目概览\n\n")
        out.write(f"- **分析文件数**: {len(analysis_results)}\n")
        out.write(f"- **分析时间**: {os.path.basename(root_dir)}\n")
        out.write(f"- **使用模型**: GPT-3.5-turbo\n\n")
        out.write("---\n\n")

        for rel_path, filepath, code_content, analysis in analysis_results:
            out.write(f"## 📄 文件: {rel_path}\n\n")
            
            # 功能总结
            out.write(f"### 📋 功能总结\n\n")
            out.write(f"{analysis['function_summary']}\n\n")
            
            # 复杂度分析
            out.write(f"### 🎯 复杂度分析\n\n")
            complexity = analysis['complexity_analysis']
            complexity_emoji = "🟢" if "简单" in complexity else "🟡" if "中等" in complexity else "🔴"
            out.write(f"{complexity_emoji} **{complexity}**\n\n")
            
            # 核心特性
            out.write(f"### ✨ 核心特性\n\n")
            features = analysis['key_features']
            if features:
                for feature in features:
                    out.write(f"- {feature}\n")
            else:
                out.write("- 无明确特性标识\n")
            out.write("\n")
            
            # 改进建议
            out.write(f"### 💡 改进建议\n\n")
            suggestions = analysis['improvement_suggestions']
            if suggestions:
                for suggestion in suggestions:
                    out.write(f"- 📝 {suggestion}\n")
            else:
                out.write("- 暂无改进建议\n")
            out.write("\n")
            
            # 潜在问题
            out.write(f"### ⚠️ 潜在问题\n\n")
            issues = analysis['potential_issues']
            if issues:
                for issue in issues:
                    out.write(f"- 🔍 {issue}\n")
            else:
                out.write("- 未发现明显问题\n")
            out.write("\n")
            
            # 源代码（可折叠）
            out.write("<details>\n<summary>📝 查看源代码</summary>\n\n")
            out.write("```python\n")
            out.write(code_content)
            out.write("\n```\n")
            out.write("</details>\n\n")
            
            out.write("---\n\n")

    print(f"✅ AI代码分析报告已生成: {output_file}")
    print(f"📊 成功分析 {len(analysis_results)} 个文件")

def analyze_single_file(file_path):
    """单独分析一个Python文件"""
    analyzer = CodeAnalyzer()
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()
        
        print(f"正在分析: {file_path}")
        result = analyzer.analyze_code(file_path, code_content)
        
        print(f"\n📄 文件: {file_path}")
        print(f"📋 功能总结: {result['function_summary']}")
        print(f"🎯 复杂度: {result['complexity_analysis']}")
        print(f"✨ 核心特性: {', '.join(result['key_features'][:3])}")
        print(f"💡 改进建议: {', '.join(result['improvement_suggestions'][:2])}")
        print(f"⚠️ 潜在问题: {', '.join(result['potential_issues'][:2])}")
        print("-" * 50)
        
        return result
        
    except Exception as e:
        print(f"❌ 分析文件 {file_path} 时出错: {e}")
        return None

# 使用方法
if __name__ == "__main__":
    root = r"E:\onedrive\OneDrive - bupt.edu.cn\AIcard"  # ← 修改为你的主目录路径
    
    # 生成完整的AI代码分析报告（多线程，3个worker）
    merge_py_to_markdown(root, max_workers=3)
    
    # 如果需要单独分析某个文件，可以使用：
    # single_file = r"C:\Users\anyon\pythonProject\example.py"
    # analyze_single_file(single_file)
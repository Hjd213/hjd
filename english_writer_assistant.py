import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import openai
import json
from typing import Dict, List, Tuple

class EnglishWritingAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("英语写作学习助手")
        self.root.geometry("800x700")
        
        # 存储API配置
        self.api_key = ""
        self.deployment_name = ""
        self.endpoint = "https://hjd-aifdy-resource.cognitiveservices.azure.com/openai/v1/"
        self.model_type = "gpt-4.1"  # 更新为用户的具体模型
        
        # 学习级别映射
        self.level_mapping = {
            "中学7年级": "middle_school_7",
            "中学8年级": "middle_school_8", 
            "中学9年级": "middle_school_9",
            "中学10年级": "middle_school_10",
            "中学11年级": "middle_school_11",
            "中学12年级": "middle_school_12",
            "大学英语4级": "college_cet4",
            "大学英语6级": "college_cet6"
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # API配置区域
        api_frame = ttk.LabelFrame(main_frame, text="API配置", padding="10")
        api_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.api_key_entry = ttk.Entry(api_frame, width=50, show="*")
        self.api_key_entry.grid(row=0, column=1, padx=(10, 0), pady=2, sticky=(tk.W, tk.E))
        
        ttk.Label(api_frame, text="部署名称:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.deployment_entry = ttk.Entry(api_frame, width=50)
        self.deployment_entry.grid(row=1, column=1, padx=(10, 0), pady=2, sticky=(tk.W, tk.E))
        
        ttk.Label(api_frame, text="终结点:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.endpoint_entry = ttk.Entry(api_frame, width=50)
        self.endpoint_entry.insert(0, self.endpoint)  # 预填充默认终结点
        self.endpoint_entry.grid(row=2, column=1, padx=(10, 0), pady=2, sticky=(tk.W, tk.E))
        
        ttk.Label(api_frame, text="模型选择:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.model_var = tk.StringVar(value=self.model_type)
        model_combo = ttk.Combobox(api_frame, textvariable=self.model_var, 
                                  values=["gpt-4.1", "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"], 
                                  state="readonly", width=47)
        model_combo.grid(row=3, column=1, padx=(10, 0), pady=2, sticky=(tk.W, tk.E))
        
        # 学习级别选择
        level_frame = ttk.LabelFrame(main_frame, text="学习级别选择", padding="10")
        level_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.level_var = tk.StringVar(value="中学7年级")
        level_combo = ttk.Combobox(level_frame, textvariable=self.level_var,
                                  values=list(self.level_mapping.keys()),
                                  state="readonly", width=47)
        level_combo.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 文本输入区域
        input_frame = ttk.LabelFrame(main_frame, text="输入英文片段", padding="10")
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8, width=70)
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.analyze_btn = ttk.Button(button_frame, text="分析并修改", command=self.analyze_writing)
        self.analyze_btn.grid(row=0, column=0, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="清空", command=self.clear_all)
        self.clear_btn.grid(row=0, column=1, padx=5)
        
        # 结果显示区域
        result_notebook = ttk.Notebook(main_frame)
        result_notebook.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 修改后文本标签页
        self.modified_frame = ttk.Frame(result_notebook)
        result_notebook.add(self.modified_frame, text="修改后文本")
        self.modified_text = scrolledtext.ScrolledText(self.modified_frame, height=10, width=70)
        self.modified_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 修改建议标签页
        self.suggestions_frame = ttk.Frame(result_notebook)
        result_notebook.add(self.suggestions_frame, text="修改建议")
        self.suggestions_text = scrolledtext.ScrolledText(self.suggestions_frame, height=10, width=70)
        self.suggestions_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        api_frame.columnconfigure(1, weight=1)
        level_frame.columnconfigure(0, weight=1)
        self.modified_frame.columnconfigure(0, weight=1)
        self.modified_frame.rowconfigure(0, weight=1)
        self.suggestions_frame.columnconfigure(0, weight=1)
        self.suggestions_frame.rowconfigure(0, weight=1)
    
    def validate_api_config(self) -> bool:
        """验证API配置"""
        self.api_key = self.api_key_entry.get().strip()
        self.deployment_name = self.deployment_entry.get().strip()
        self.endpoint = self.endpoint_entry.get().strip()
        self.model_type = self.model_var.get()
        
        if not self.api_key:
            messagebox.showerror("错误", "请输入API Key")
            return False
            
        if not self.deployment_name:
            messagebox.showerror("错误", "请输入部署名称")
            return False
            
        if not self.endpoint:
            messagebox.showerror("错误", "请输入终结点")
            return False
            
        return True
    
    def get_level_description(self, level_key: str) -> str:
        """获取学习级别的详细描述"""
        descriptions = {
            "middle_school_7": "中学7年级水平：基础语法掌握，简单句式，基础词汇量",
            "middle_school_8": "中学8年级水平：较好语法基础，复合句开始使用，中等词汇量",
            "middle_school_9": "中学9年级水平：良好语法掌握，复杂句式，较丰富词汇量",
            "middle_school_10": "中学10年级水平：扎实语法基础，多样句式，丰富词汇量",
            "middle_school_11": "中学11年级水平：高级语法掌握，复杂句式结构，高级词汇量",
            "middle_school_12": "中学12年级水平：母语者水平语法，灵活句式运用，专业词汇量",
            "college_cet4": "大学英语4级水平：大学基础英语能力，学术写作入门",
            "college_cet6": "大学英语6级水平：较高英语水平，较强学术写作能力"
        }
        return descriptions.get(level_key, "未知水平")
    
    def create_analysis_prompt(self, text: str, level: str) -> str:
        """创建分析提示词"""
        level_desc = self.get_level_description(level)
        
        prompt = f"""你是一位专业的英语写作指导老师，请分析以下英文文本并提供修改建议。

学习者水平：{level_desc}

请严格按照以下要求进行分析和修改：

1. 识别并纠正语法错误、时态错误、用词不当、拼写错误
2. 检查句子结构问题，优化表达方式
3. 如果发现句式过于简单或用词过于基础，请提供升级建议
4. 必须保持原文的基本意思不变
5. 避免过度复杂化，确保修改后的文本适合该水平学习者的理解能力

请按以下格式返回结果：

【修改后文本】
[在这里放置修改后的完整文本]

【修改建议】
1. [具体问题1]：[修改原因和建议]
2. [具体问题2]：[修改原因和建议]
...

原文本：
{text}

请提供专业的分析和修改建议。"""

        return prompt
    
    def analyze_writing(self):
        """分析写作并给出修改建议"""
        if not self.validate_api_config():
            return
            
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "请输入要分析的英文文本")
            return
            
        selected_level = self.level_var.get()
        level_key = self.level_mapping[selected_level]
        
        try:
            # 显示处理中状态
            self.analyze_btn.config(state="disabled", text="处理中...")
            self.root.update()
            
            # 配置OpenAI客户端 - 适配用户的终结点格式
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.endpoint
            )
            
            # 创建分析提示
            prompt = self.create_analysis_prompt(text, level_key)
            
            # 调用API - 使用用户指定的模型
            response = client.chat.completions.create(
                model=self.model_type,  # 直接使用模型名称而不是部署名称
                messages=[
                    {"role": "system", "content": "你是一位专业的英语写作指导老师，擅长根据不同学习水平提供针对性的写作建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # 解析响应
            result = response.choices[0].message.content
            
            # 分离修改后文本和建议
            self.parse_and_display_result(result)
            
        except Exception as e:
            messagebox.showerror("错误", f"API调用失败：{str(e)}")
        finally:
            # 恢复按钮状态
            self.analyze_btn.config(state="normal", text="分析并修改")
    
    def parse_and_display_result(self, result: str):
        """解析并显示结果"""
        # 清空之前的结果
        self.modified_text.delete("1.0", tk.END)
        self.suggestions_text.delete("1.0", tk.END)
        
        # 分离修改后文本和建议
        if "【修改后文本】" in result and "【修改建议】" in result:
            parts = result.split("【修改建议】")
            modified_part = parts[0].replace("【修改后文本】", "").strip()
            suggestions_part = "【修改建议】" + parts[1].strip()
        else:
            # 如果格式不符合预期，直接显示全部内容
            modified_part = result
            suggestions_part = result
            
        # 显示结果
        self.modified_text.insert("1.0", modified_part)
        self.suggestions_text.insert("1.0", suggestions_part)
    
    def clear_all(self):
        """清空所有内容"""
        self.input_text.delete("1.0", tk.END)
        self.modified_text.delete("1.0", tk.END)
        self.suggestions_text.delete("1.0", tk.END)

def main():
    root = tk.Tk()
    app = EnglishWritingAssistant(root)
    root.mainloop()

if __name__ == "__main__":
    main()
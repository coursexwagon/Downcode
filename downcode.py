#!/usr/bin/env python3
"""
Downcode - Minimal AI Coding Agent
Works with any OpenAI-compatible API (NVIDIA, etc.)
"""

import os
import json
import re
import subprocess
from typing import List, Dict, Any
from openai import OpenAI

class Downcode:
    def __init__(self, api_key=None, base_url=None, model=None):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        self.model = model or os.getenv("NVIDIA_MODEL", "meta/llama-3.1-405b-instruct")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.context_files = []
        self.conversation_history = []
        
    def system_prompt(self) -> str:
        return """You are Downcode, an AI coding assistant. You have access to tools:

<tools>
- bash: Run shell commands. {"command": "cmd"}
- read: Read file contents. {"file_path": "/path/to/file"}
- write: Write file contents. {"file_path": "/path/to/file", "content": "..."}
- edit: Edit file (search/replace). {"file_path": "/path/to/file", "old_string": "...", "new_string": "..."}
- view: List directory contents. {"dir_path": "."}
</tools>

Rules:
1. ALWAYS respond with valid JSON in format: {"tool": "name", "args": {...}}
2. Use "view" to explore directory structure before reading files
3. Use "edit" for small changes, "write" for new files
4. Run "bash" to test your changes
5. After completing task, respond with {"tool": "done", "args": {"summary": "what you did"}}
"""

    def get_relevant_files(self, user_request: str) -> List[str]:
        """Auto-discover relevant files based on git status and request"""
        files = []
        
        # Get git modified files
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                files.extend(result.stdout.strip().split("\n"))
        except:
            pass
        
        # Get untracked files
        try:
            result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                files.extend(result.stdout.strip().split("\n"))
        except:
            pass
        
        # Filter for code files
        code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java', '.cpp', '.c', '.h']
        files = [f for f in files if any(f.endswith(ext) for ext in code_extensions) and os.path.exists(f)]
        
        return files[:20]  # Limit to 20 files

    def read_file(self, path: str) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content[:10000]  # Limit file reads
        except Exception as e:
            return f"Error reading {path}: {e}"

    def write_file(self, path: str, content: str) -> str:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Wrote {len(content)} chars to {path}"
        except Exception as e:
            return f"Error writing {path}: {e}"

    def edit_file(self, path: str, old: str, new: str) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if old not in content:
                return f"Old string not found in {path}"
            content = content.replace(old, new, 1)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Edited {path}"
        except Exception as e:
            return f"Error editing {path}: {e}"

    def bash(self, command: str) -> str:
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            output = result.stdout + result.stderr
            return output[:5000]  # Limit output
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception as e:
            return f"Error: {e}"

    def view_dir(self, path: str) -> str:
        try:
            items = os.listdir(path)
            result = []
            for item in sorted(items)[:50]:  # Limit items
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    result.append(f"📁 {item}/")
                else:
                    size = os.path.getsize(item_path)
                    result.append(f"📄 {item} ({size} bytes)")
            return "\n".join(result)
        except Exception as e:
            return f"Error: {e}"

    def execute_tool(self, tool_name: str, args: Dict) -> str:
        if tool_name == "bash":
            return self.bash(args.get("command", ""))
        elif tool_name == "read":
            return self.read_file(args.get("file_path", ""))
        elif tool_name == "write":
            return self.write_file(args.get("file_path", ""), args.get("content", ""))
        elif tool_name == "edit":
            return self.edit_file(args.get("file_path", ""), args.get("old_string", ""), args.get("new_string", ""))
        elif tool_name == "view":
            return self.view_dir(args.get("dir_path", "."))
        else:
            return f"Unknown tool: {tool_name}"

    def process_request(self, user_request: str, auto_context: bool = True):
        # Build initial context
        messages = [{"role": "system", "content": self.system_prompt()}]
        
        # Auto-add relevant files
        if auto_context:
            files = self.get_relevant_files(user_request)
            context = ""
            for f in files[:5]:  # Top 5 files
                content = self.read_file(f)
                context += f"\n=== {f} ===\n{content}\n\n"
            if context:
                user_request = f"<project_context>\n{context}</project_context>\n\n{user_request}"
        
        messages.append({"role": "user", "content": user_request})
        
        print(f"\n🤖 Downcode using {self.model}")
        print(f"📁 Found {len(self.get_relevant_files(user_request))} relevant files")
        print("=" * 50)
        
        iteration = 0
        max_iterations = 10
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call LLM
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=4096
                )
                content = response.choices[0].message.content
            except Exception as e:
                print(f"❌ API Error: {e}")
                break
            
            # Parse tool call
            try:
                # Try to extract JSON from markdown code blocks
                json_match = re.search(r'```json\s*\n?(.*?)\n?```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
                
                tool_call = json.loads(content.strip())
                tool_name = tool_call.get("tool")
                args = tool_call.get("args", {})
            except:
                print(f"⚠️  Failed to parse: {content[:200]}...")
                messages.append({"role": "user", "content": "ERROR: Respond ONLY with JSON like {\"tool\": \"bash\", \"args\": {\"command\": \"ls\"}}"})
                continue
            
            print(f"\n🔧 Tool: {tool_name}")
            if tool_name == "done":
                print(f"✅ Done: {args.get('summary', 'Task complete')}")
                break
            
            # Execute
            result = self.execute_tool(tool_name, args)
            print(f"📤 Result: {result[:500]}" if len(str(result)) > 500 else f"📤 Result: {result}")
            
            # Add to conversation
            messages.append({"role": "assistant", "content": json.dumps(tool_call)})
            messages.append({"role": "user", "content": f"Tool result: {result}"})
        
        if iteration >= max_iterations:
            print("⚠️  Max iterations reached")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Downcode - AI Coding Agent")
    parser.add_argument("prompt", help="What you want to do")
    parser.add_argument("--model", default=os.getenv("NVIDIA_MODEL", "meta/llama-3.1-405b-instruct"))
    parser.add_argument("--base-url", default=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"))
    args = parser.parse_args()
    
    agent = Downcode(model=args.model, base_url=args.base_url)
    agent.process_request(args.prompt)

if __name__ == "__main__":
    main()

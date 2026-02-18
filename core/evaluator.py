import os
import yaml
import time
import requests
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console()

class PromptBench:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables.")

    def call_model(self, model: str, prompt: str) -> Dict:
        """Calls the appropriate API (OpenRouter or OpenAI) for a specific model."""
        start_time = time.time()
        
        # Determine provider and endpoint
        if model.startswith("gpt-") or "openai" in model.lower() and "openrouter" not in model.lower():
            url = "https://api.openai.com/v1/chat/completions"
            api_key = os.getenv("OPENAI_API_KEY")
            headers = {"Authorization": f"Bearer {api_key}"}
        else:
            url = "https://openrouter.ai/api/v1/chat/completions"
            api_key = os.getenv("OPENROUTER_API_KEY")
            headers = {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/AIassistent2025/promptbench", # Optional for OpenRouter
                "X-Title": "PromptBench"
            }

        if not api_key:
            return {"model": model, "status": "error", "message": "API Key not found."}

        try:
            response = requests.post(
                url=url,
                headers=headers,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30
            )
            data = response.json()
            if response.status_code != 200:
                return {"model": model, "status": "error", "message": data.get('error', {}).get('message', 'Unknown error')}
            
            latency = time.time() - start_time
            return {
                "model": model,
                "content": data['choices'][0]['message']['content'],
                "latency": round(latency, 2),
                "tokens": data.get('usage', {}).get('total_tokens', 0),
                "status": "success"
            }
        except Exception as e:
            return {"model": model, "status": "error", "message": str(e)}

    def evaluate_response(self, response: str, criteria: Dict) -> Dict:
        """Scores a response based on simple heuristics."""
        scores = {}
        if "max_length" in criteria:
            scores["length_check"] = 1.0 if len(response.split()) <= criteria["max_length"] else 0.0
        
        if "contains_keywords" in criteria:
            matches = sum(1 for k in criteria["contains_keywords"] if k.lower() in response.lower())
            scores["keyword_score"] = matches / len(criteria["contains_keywords"])
            
        if "is_json" in criteria and criteria["is_json"]:
            import json
            try:
                json.loads(response)
                scores["format_score"] = 1.0
            except:
                scores["format_score"] = 0.0
                
        avg_score = sum(scores.values()) / len(scores) if scores else 1.0
        return {"scores": scores, "total": round(avg_score, 2)}

    def run_benchmark(self, prompt_file: str):
        with open(prompt_file, 'r') as f:
            prompt_data = yaml.safe_load(f)
        
        prompt_text = prompt_data['prompt']
        models = self.config['models']
        criteria = prompt_data.get('evaluation_criteria', {})
        
        results = []
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Running benchmark...", total=len(models))
            for model in models:
                res = self.call_model(model, prompt_text)
                if res['status'] == "success":
                    eval_res = self.evaluate_response(res['content'], criteria)
                    res['score'] = eval_res['total']
                    res['breakdown'] = eval_res['scores']
                results.append(res)
                progress.advance(task)
        
        self.display_results(prompt_data['name'], results)

    def display_results(self, name: str, results: List[Dict]):
        table = Table(title=f"Benchmark: {name}")
        table.add_column("Model", style="cyan")
        table.add_column("Score", justify="right", style="green")
        table.add_column("Latency (s)", justify="right")
        table.add_column("Tokens", justify="right")
        table.add_column("Status", justify="center")

        for r in results:
            if r['status'] == "success":
                table.add_row(
                    r['model'].split('/')[-1],
                    str(r['score']),
                    str(r['latency']),
                    str(r['tokens']),
                    "[green]PASS" if r['score'] >= 0.7 else "[yellow]FAIL"
                )
            else:
                table.add_row(r['model'], "0.0", "N/A", "N/A", f"[red]ERR")

        console.print(table)

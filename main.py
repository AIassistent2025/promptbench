import sys
from core.evaluator import PromptBench

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <prompt_file>")
        sys.exit(1)
        
    prompt_file = sys.argv[1]
    
    try:
        bench = PromptBench("config.yaml")
        bench.run_benchmark(prompt_file)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

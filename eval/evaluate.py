import json
import time
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.orchestrator import run_chat

def evaluate():
    with open("eval/test_cases.json", "r") as f:
        test_cases = json.load(f)
    
    results = []
    total_latency = 0
    success_count = 0
    
    print("Starting Evaluation...")
    
    for case in test_cases:
        print(f"Running Case {case['id']}: {case['query']}")
        start_time = time.time()
        try:
            response = run_chat(case['query'])
            latency = time.time() - start_time
            total_latency += latency
            
            # Simple keyword check
            passed = any(k.lower() in response.lower() for k in case['expected_keywords'])
            if passed:
                success_count += 1
            
            results.append({
                "id": case['id'],
                "query": case['query'],
                "response": response,
                "latency": latency,
                "passed": passed
            })
            print(f"  Result: {'PASS' if passed else 'FAIL'} ({latency:.2f}s)")
            
        except Exception as e:
            print(f"  Error: {e}")
            results.append({
                "id": case['id'],
                "error": str(e),
                "passed": False
            })

    metrics = {
        "total_cases": len(test_cases),
        "success_rate": success_count / len(test_cases) if test_cases else 0,
        "avg_latency": total_latency / len(test_cases) if test_cases else 0
    }
    
    print("\nEvaluation Metrics:")
    print(json.dumps(metrics, indent=2))
    
    with open("eval/results.json", "w") as f:
        json.dump({"metrics": metrics, "details": results}, f, indent=2)

if __name__ == "__main__":
    evaluate()

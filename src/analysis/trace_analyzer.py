"""Analyze LangSmith traces to find optimization opportunities"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langsmith import Client
from collections import defaultdict
import statistics

load_dotenv()

class TraceAnalyzer:
    """Analyze agent performance from LangSmith traces"""
    
    def __init__(self, project_name: str = None):
        self.client = Client()
        self.project_name = project_name or os.getenv("LANGCHAIN_PROJECT")
        
    def get_recent_runs(self, hours: int = 24, limit: int = 100):
        """Fetch recent runs from LangSmith"""
        print(f"\n📊 Fetching runs from last {hours} hours...")
        
        # Calculate time window
        start_time = datetime.now() - timedelta(hours=hours)
        
        # Fetch runs
        runs = list(self.client.list_runs(
            project_name=self.project_name,
            start_time=start_time,
            limit=limit
        ))
        
        print(f"✓ Found {len(runs)} runs\n")
        return runs
    
    def _get_latency(self, run):
        """Get latency from run object (handles different attribute names)"""
        # Try different possible attribute names
        if hasattr(run, 'latency') and run.latency:
            return run.latency
        elif hasattr(run, 'total_tokens') and run.end_time and run.start_time:
            return (run.end_time - run.start_time).total_seconds()
        elif run.end_time and run.start_time:
            return (run.end_time - run.start_time).total_seconds()
        return None
    
    def analyze_latency(self, runs):
        """Analyze latency by step"""
        print("="*70)
        print("⏱️  LATENCY ANALYSIS")
        print("="*70)
        
        step_latencies = defaultdict(list)
        
        for run in runs:
            if run.name:
                latency = self._get_latency(run)
                if latency:
                    step_latencies[run.name].append(latency)
        
        if not step_latencies:
            print("\n⚠️  No latency data available\n")
            return step_latencies
        
        print(f"\n{'Step':<25} {'Count':<8} {'P50':<10} {'P95':<10} {'Max':<10}")
        print("-"*70)
        
        for step_name in sorted(step_latencies.keys()):
            latencies = step_latencies[step_name]
            
            if len(latencies) > 0:
                # Convert to milliseconds
                latencies_ms = [l * 1000 for l in latencies]
                
                p50 = statistics.median(latencies_ms)
                p95 = statistics.quantiles(latencies_ms, n=20)[18] if len(latencies_ms) > 1 else latencies_ms[0]
                max_lat = max(latencies_ms)
                
                print(f"{step_name:<25} {len(latencies):<8} {p50:<10.0f} {p95:<10.0f} {max_lat:<10.0f}")
        
        print()
        return step_latencies
    
    def analyze_token_usage(self, runs):
        """Analyze token usage and costs"""
        print("="*70)
        print("💰 TOKEN USAGE & COST ANALYSIS")
        print("="*70)
        
        total_tokens = 0
        total_input = 0
        total_output = 0
        llm_calls = 0
        
        for run in runs:
            # Check for token usage in different places
            input_tokens = 0
            output_tokens = 0
            
            # Method 1: Check outputs
            if hasattr(run, 'outputs') and run.outputs and isinstance(run.outputs, dict):
                input_tokens = run.outputs.get('total_tokens', 0) or run.outputs.get('input_tokens', 0)
                output_tokens = run.outputs.get('output_tokens', 0)
            
            # Method 2: Check extra metadata
            if hasattr(run, 'extra') and run.extra and isinstance(run.extra, dict):
                usage = run.extra.get('usage', {})
                if usage:
                    input_tokens = usage.get('input_tokens', 0)
                    output_tokens = usage.get('output_tokens', 0)
            
            # Method 3: Check if run has prompt_tokens/completion_tokens
            if hasattr(run, 'prompt_tokens'):
                input_tokens = run.prompt_tokens or 0
            if hasattr(run, 'completion_tokens'):
                output_tokens = run.completion_tokens or 0
            
            if input_tokens > 0 or output_tokens > 0:
                total_input += input_tokens
                total_output += output_tokens
                llm_calls += 1
        
        total_tokens = total_input + total_output
        
        if llm_calls == 0:
            print("\n⚠️  No token usage data available")
            print("   This might be because:")
            print("   - Traces don't include usage metadata")
            print("   - LLM calls weren't captured properly\n")
            return {}
        
        # Approximate costs (Claude Sonnet 4 pricing)
        # Input: $3 per 1M tokens, Output: $15 per 1M tokens
        input_cost = (total_input / 1_000_000) * 3
        output_cost = (total_output / 1_000_000) * 15
        total_cost = input_cost + output_cost
        
        print(f"\nLLM Calls: {llm_calls}")
        print(f"Total Input Tokens: {total_input:,}")
        print(f"Total Output Tokens: {total_output:,}")
        print(f"Total Tokens: {total_tokens:,}")
        print(f"\nEstimated Cost:")
        print(f"  Input:  ${input_cost:.4f}")
        print(f"  Output: ${output_cost:.4f}")
        print(f"  Total:  ${total_cost:.4f}")
        
        if llm_calls > 0:
            print(f"\nAverage per call:")
            print(f"  Tokens: {total_tokens/llm_calls:.0f}")
            print(f"  Cost: ${total_cost/llm_calls:.4f}")
        
        print()
        return {
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "llm_calls": llm_calls
        }
    
    def analyze_errors(self, runs):
        """Analyze error patterns"""
        print("="*70)
        print("❌ ERROR ANALYSIS")
        print("="*70)
        
        errors = defaultdict(int)
        error_steps = defaultdict(int)
        
        for run in runs:
            error = None
            
            # Check different error attributes
            if hasattr(run, 'error') and run.error:
                error = run.error
            elif hasattr(run, 'status') and run.status == 'error':
                error = "Error (no message)"
            
            if error:
                # Count by error type
                error_msg = str(error)[:100]
                errors[error_msg] += 1
                
                # Count by step
                if run.name:
                    error_steps[run.name] += 1
        
        if not errors:
            print("\n✅ No errors found!\n")
            return
        
        print(f"\nTotal errors: {sum(errors.values())}")
        print(f"\nErrors by type:")
        for error, count in sorted(errors.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {count}x: {error}")
        
        print(f"\nErrors by step:")
        for step, count in sorted(error_steps.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {step}: {count}")
        
        print()
        return errors
    
    def analyze_intent_accuracy(self, runs):
        """
        Analyze classification accuracy.
        This requires ground truth labels in your test data.
        """
        print("="*70)
        print("🎯 INTENT CLASSIFICATION ACCURACY")
        print("="*70)
        
        # This is a simplified version - you'd need to correlate runs with ground truth
        print("\n⚠️  Accuracy analysis requires ground truth labels")
        print("   See test results in classification_results.json\n")
    
    def identify_bottlenecks(self, runs):
        """Identify performance bottlenecks"""
        print("="*70)
        print("🔍 BOTTLENECK IDENTIFICATION")
        print("="*70)
        
        step_latencies = defaultdict(list)
        
        for run in runs:
            if run.name:
                latency = self._get_latency(run)
                if latency:
                    step_latencies[run.name].append(latency)
        
        # Find slowest steps
        avg_latencies = {}
        for step, latencies in step_latencies.items():
            if latencies:
                avg_latencies[step] = statistics.mean(latencies)
        
        if not avg_latencies:
            print("\n⚠️  No latency data available\n")
            return
        
        print("\n🐌 Slowest steps (avg latency):")
        for step, latency in sorted(avg_latencies.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {step}: {latency*1000:.0f}ms")
        
        # Recommendations
        print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
        
        for step, latency in sorted(avg_latencies.items(), key=lambda x: x[1], reverse=True)[:3]:
            if "crm" in step.lower():
                print(f"\n  • {step} is slow ({latency*1000:.0f}ms)")
                print(f"    → Consider caching user data")
                print(f"    → Batch CRM requests if possible")
            elif "kb_search" in step.lower():
                print(f"\n  • {step} is slow ({latency*1000:.0f}ms)")
                print(f"    → Consider caching frequent queries")
                print(f"    → Optimize vector search parameters")
            elif "classify" in step.lower() or "extract" in step.lower() or "route" in step.lower():
                print(f"\n  • {step} is slow ({latency*1000:.0f}ms)")
                print(f"    → Consider using a faster model for this step")
                print(f"    → Optimize prompt length")
        
        print()
    
    def run_full_analysis(self, hours: int = 24):
        """Run complete analysis"""
        print("\n" + "="*70)
        print(f"🔬 FULL AGENT ANALYSIS - {self.project_name}")
        print("="*70)
        
        runs = self.get_recent_runs(hours=hours)
        
        if not runs:
            print("⚠️  No runs found in the specified time window")
            return
        
        self.analyze_latency(runs)
        self.analyze_token_usage(runs)
        self.analyze_errors(runs)
        self.analyze_intent_accuracy(runs)
        self.identify_bottlenecks(runs)
        
        print("="*70)
        print("✅ Analysis complete!")
        print(f"🔗 View detailed traces: https://smith.langchain.com/")
        print("="*70 + "\n")

if __name__ == "__main__":
    analyzer = TraceAnalyzer()
    analyzer.run_full_analysis(hours=24)
#!/usr/bin/env python3
"""Simple benchmark script to test download performance."""

import time
import subprocess
import sys
from pathlib import Path


def benchmark_download(url: str, test_name: str):
    """Benchmark a single download."""
    print(f"\n🚀 Running {test_name}...")
    print(f"URL: {url}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "cli.main", 
            "download", "gallery", url, "--force"
        ], capture_output=True, text=True, timeout=300)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ {test_name} completed in {duration:.2f} seconds")
            
            # Extract file count from output
            lines = result.stdout.split('\n')
            for line in lines:
                if "files downloaded" in line:
                    files_match = line.split()[0]
                    try:
                        files_count = int(files_match)
                        speed = files_count / duration
                        print(f"📊 Speed: {speed:.2f} files/second")
                        return duration, files_count
                    except:
                        pass
            
            return duration, 0
        else:
            print(f"❌ {test_name} failed: {result.stderr}")
            return None, 0
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_name} timed out after 5 minutes")
        return None, 0
    except Exception as e:
        print(f"💥 {test_name} error: {e}")
        return None, 0


def main():
    """Run performance benchmarks."""
    print("🎯 HFox Downloader Performance Benchmark")
    print("=" * 50)
    
    # Test URLs (smaller galleries for quick testing)
    test_urls = [
        "https://hentaifox.com/gallery/147838/",  # 49 pages
    ]
    
    results = []
    
    for i, url in enumerate(test_urls, 1):
        # Test with normal settings
        print(f"\n📊 Test {i}/2 - Normal Mode")
        subprocess.run([sys.executable, "-m", "cli.main", "perf", "normal"], 
                      capture_output=True)
        
        duration_normal, files_normal = benchmark_download(url, f"Normal Mode (Test {i})")
        
        # Test with turbo settings  
        print(f"\n🚀 Test {i}/2 - Turbo Mode")
        subprocess.run([sys.executable, "-m", "cli.main", "perf", "turbo"], 
                      capture_output=True)
        
        duration_turbo, files_turbo = benchmark_download(url, f"Turbo Mode (Test {i})")
        
        if duration_normal and duration_turbo:
            improvement = ((duration_normal - duration_turbo) / duration_normal) * 100
            results.append({
                'url': url,
                'normal_time': duration_normal,
                'turbo_time': duration_turbo,
                'improvement': improvement,
                'files': files_normal
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📈 BENCHMARK RESULTS")
    print("=" * 50)
    
    if results:
        total_normal = sum(r['normal_time'] for r in results)
        total_turbo = sum(r['turbo_time'] for r in results)
        overall_improvement = ((total_normal - total_turbo) / total_normal) * 100
        
        for i, result in enumerate(results, 1):
            print(f"\nTest {i}:")
            print(f"  Files: {result['files']}")
            print(f"  Normal: {result['normal_time']:.2f}s")
            print(f"  Turbo:  {result['turbo_time']:.2f}s")
            print(f"  Improvement: {result['improvement']:.1f}%")
        
        print(f"\n🎯 OVERALL IMPROVEMENT: {overall_improvement:.1f}%")
        print(f"Total time saved: {total_normal - total_turbo:.2f} seconds")
        
        if overall_improvement > 0:
            print("✅ Turbo mode is faster!")
        else:
            print("⚠️  Normal mode performed better (network conditions may vary)")
    else:
        print("❌ No successful benchmarks completed")


if __name__ == "__main__":
    main()
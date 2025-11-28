"""
MT5 API Concurrency Test
Test multi-worker performance and concurrent request handling
"""
import asyncio
import aiohttp
import time
import statistics
from typing import List, Tuple


async def test_endpoint(session: aiohttp.ClientSession, url: str, 
                       headers: dict = None) -> Tuple[int, float]:
    """Test a single endpoint and return status code and latency"""
    start = time.time()
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            await resp.read()
            latency = time.time() - start
            return resp.status, latency
    except Exception as e:
        latency = time.time() - start
        return 0, latency


async def concurrent_requests(url: str, num_requests: int, headers: dict = None):
    """Send multiple concurrent requests to an endpoint"""
    async with aiohttp.ClientSession() as session:
        tasks = [test_endpoint(session, url, headers) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
    
    return results


def analyze_results(results: List[Tuple[int, float]], endpoint: str):
    """Analyze and print results"""
    status_codes = [r[0] for r in results]
    latencies = [r[1] for r in results if r[0] == 200]
    
    successful = sum(1 for s in status_codes if s == 200)
    failed = len(status_codes) - successful
    
    print(f"\n{endpoint}")
    print("-" * 60)
    print(f"Total requests:  {len(results)}")
    print(f"Successful:      {successful} ({successful/len(results)*100:.1f}%)")
    print(f"Failed:          {failed}")
    
    if latencies:
        print(f"\nLatency Statistics (successful requests):")
        print(f"  Min:     {min(latencies)*1000:.2f}ms")
        print(f"  Max:     {max(latencies)*1000:.2f}ms")
        print(f"  Mean:    {statistics.mean(latencies)*1000:.2f}ms")
        print(f"  Median:  {statistics.median(latencies)*1000:.2f}ms")
        if len(latencies) > 1:
            print(f"  Std Dev: {statistics.stdev(latencies)*1000:.2f}ms")
        
        # Check for concerning latency
        p95 = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        p99 = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        print(f"  P95:     {p95*1000:.2f}ms")
        print(f"  P99:     {p99*1000:.2f}ms")
        
        if p95 > 1.0:  # More than 1 second
            print(f"  ⚠️  P95 latency is high (>{1000}ms)")
        elif p95 > 0.5:
            print(f"  ⚠️  P95 latency is elevated (>{500}ms)")
        else:
            print(f"  ✓  P95 latency is acceptable (<500ms)")


async def main():
    print("="*60)
    print("MT5 API Concurrency Test")
    print("="*60)
    print()
    print("Testing with various concurrency levels...")
    print("Make sure the API server is running with multiple workers:")
    print("  uvicorn src.mt5_api:app --host 0.0.0.0 --port 8000 --workers 4")
    print()
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health endpoint (no auth required)
    print("\n" + "="*60)
    print("Test 1: Health Endpoint (/healthz)")
    print("="*60)
    
    for concurrency in [10, 50, 100]:
        print(f"\nConcurrency: {concurrency} requests")
        results = await concurrent_requests(f"{base_url}/healthz", concurrency)
        analyze_results(results, f"/healthz - {concurrency} concurrent")
        await asyncio.sleep(1)  # Brief pause between tests
    
    # Test 2: Root endpoint
    print("\n" + "="*60)
    print("Test 2: Root Endpoint (/)")
    print("="*60)
    
    for concurrency in [10, 50, 100]:
        print(f"\nConcurrency: {concurrency} requests")
        results = await concurrent_requests(f"{base_url}/", concurrency)
        analyze_results(results, f"/ - {concurrency} concurrent")
        await asyncio.sleep(1)
    
    # Test 3: Protected endpoint (should get 401/403)
    print("\n" + "="*60)
    print("Test 3: Protected Endpoint (/api/v1/account - no auth)")
    print("="*60)
    
    for concurrency in [10, 50]:
        print(f"\nConcurrency: {concurrency} requests")
        results = await concurrent_requests(f"{base_url}/api/v1/account", concurrency)
        
        # For protected endpoints, we expect 403 responses
        status_codes = [r[0] for r in results]
        auth_errors = sum(1 for s in status_codes if s == 403)
        print(f"\nTotal requests:  {len(results)}")
        print(f"Auth errors (403): {auth_errors} ({auth_errors/len(results)*100:.1f}%)")
        
        if auth_errors == len(results):
            print("✓ All requests properly rejected (auth working)")
        else:
            print("⚠️  Some requests did not return 403")
        
        await asyncio.sleep(1)
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print()
    print("Concurrency test complete!")
    print()
    print("Key Metrics to Monitor:")
    print("  • P95 latency should be < 500ms for health checks")
    print("  • Success rate should be 100% for non-auth endpoints")
    print("  • No crashes or 500 errors under concurrent load")
    print("  • Memory usage should remain stable")
    print()
    print("For production:")
    print("  • Use gunicorn/uvicorn with multiple workers")
    print("  • Enable connection pooling")
    print("  • Configure proper rate limiting")
    print("  • Monitor with Prometheus/Grafana")
    print()


if __name__ == "__main__":
    asyncio.run(main())

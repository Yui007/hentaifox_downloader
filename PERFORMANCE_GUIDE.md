# 🚀 Performance Optimization Guide

## Quick Performance Boost

### Enable Turbo Mode
```bash
python -m cli.main perf turbo
```

This instantly optimizes your download settings for maximum speed:
- ✅ 16 connections per server (vs 4 default)
- ✅ 32 concurrent downloads (vs 4 default) 
- ✅ 4 parallel galleries (vs 2 default)
- ✅ Optimized aria2c configuration
- ✅ Minimal delays between requests

### Check Current Performance
```bash
python -m cli.main perf status
```

### Restore Normal Mode
```bash
python -m cli.main perf normal
```

## Performance Factors

### 1. Network Connection
- **Fiber/High-speed**: Turbo mode will show significant improvements
- **Slower connections**: May not see much difference, normal mode is fine
- **Mobile/Limited**: Use normal mode to avoid overwhelming your connection

### 2. System Resources
- **High-end PC**: Can handle turbo mode easily
- **Older systems**: May struggle with too many concurrent connections
- **Limited RAM**: Reduce `max_concurrent_downloads` in config

### 3. Server Response
- **HentaiFox server load**: Affects download speed regardless of settings
- **Geographic location**: Closer to servers = faster downloads
- **Time of day**: Peak hours may be slower

## Advanced Optimization

### Custom Aria2c Settings
Edit `config/performance.py` to customize aria2c parameters:

```python
ARIA2_HIGH_PERFORMANCE = {
    "cmdline-args": [
        "--max-connections-per-server=16",  # Increase for faster downloads
        "--split=16",                       # More segments per file
        "--min-split-size=256K",           # Smaller segments
        "--max-concurrent-downloads=32",    # More parallel downloads
        "--disk-cache=64M",                # More RAM cache
        # Add more optimizations...
    ]
}
```

### Gallery-dl Optimization
Reduce delays in `config/performance.py`:

```python
GALLERY_DL_PERFORMANCE = {
    "sleep": 0.05,          # Minimal delay (be respectful!)
    "sleep-request": 0.05,  # Between HTTP requests
    "retries": 2,           # Fewer retries for speed
    "timeout": 10,          # Faster timeouts
}
```

## Troubleshooting Slow Downloads

### 1. Check Dependencies
```bash
python -m cli.main test
```

Ensure both gallery-dl and aria2c are properly installed.

### 2. Network Issues
- Try different times of day
- Check your internet speed
- Disable VPN if using one
- Try normal mode if turbo is unstable

### 3. System Resources
- Close other download programs
- Check available RAM and CPU
- Monitor disk space and speed

### 4. Server-side Limits
- HentaiFox may have rate limiting
- Too many connections might trigger blocks
- Use normal mode if getting errors

## Benchmark Your Setup

Run the included benchmark:
```bash
python benchmark.py
```

This will test both normal and turbo modes to show actual performance gains on your system.

## Expected Performance

### Typical Results
- **Normal Mode**: 2-4 files/second
- **Turbo Mode**: 6-12 files/second  
- **Improvement**: 50-200% faster downloads

### Factors Affecting Speed
- File sizes (larger images = slower)
- Network latency and bandwidth
- Server response times
- System performance
- Concurrent downloads

## Best Practices

1. **Start with turbo mode** - works well for most users
2. **Monitor system resources** - don't overwhelm your PC
3. **Be respectful** - don't abuse the servers
4. **Test your setup** - use the benchmark script
5. **Adjust as needed** - customize settings for your environment

## Configuration Files

- `config/defaults.py` - Default settings
- `config/performance.py` - Performance optimizations  
- `config/settings.py` - Runtime configuration management

## Need Help?

If downloads are still slow:
1. Run `python -m cli.main test` to check setup
2. Try `python -m cli.main perf status` to see current settings
3. Test with `python benchmark.py` to measure performance
4. Check network connection and system resources
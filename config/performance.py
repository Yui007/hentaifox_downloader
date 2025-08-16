"""Performance optimization configurations."""

# High-performance aria2c configuration
ARIA2_HIGH_PERFORMANCE = {
    "cmdline-args": [
        "--max-connections-per-server=16",
        "--split=16", 
        "--min-split-size=256K",
        "--max-concurrent-downloads=32",
        "--continue=true",
        "--auto-file-renaming=false",
        "--disk-cache=64M",
        "--file-allocation=none",
        "--check-certificate=false",
        "--max-download-limit=0",  # No speed limit
        "--max-overall-download-limit=0",
        "--piece-length=1M",
        "--allow-overwrite=true",
        "--always-resume=false",
        "--async-dns=true",
        "--enable-http-keep-alive=true",
        "--enable-http-pipelining=true",
        "--max-tries=3",
        "--retry-wait=1",
        "--timeout=10",
        "--connect-timeout=10"
    ]
}

# Gallery-dl performance settings
GALLERY_DL_PERFORMANCE = {
    "sleep": 0.05,  # Minimal delay between requests
    "sleep-request": 0.05,
    "sleep-extractor": 0.05,
    "retries": 2,  # Fewer retries for speed
    "timeout": 10,
    "verify": False,  # Skip SSL verification for speed
}

# Network optimization
NETWORK_OPTIMIZATION = {
    "max_parallel_galleries": 4,
    "max_connections_per_server": 16,
    "connection_pool_size": 32,
    "request_timeout": 5,
    "max_retries": 2,
}
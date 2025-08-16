# 🎯 HFox Downloader - Complete Usage Guide

## 🚀 Quick Start

### Setup (first time)
```bash
python -m cli.main setup
python -m cli.main test  # Test all components
```
### Interactive Mode (Recommended)
```bash
python -m cli.main interactive
```

### Enable Turbo Mode (Recommended)
```bash
python -m cli.main perf turbo  # 4x faster downloads
```

### Set Auto-Conversion (Optional)
```bash
python -m cli.main convert auto pdf --delete-source  # Auto-convert to PDF and delete images
```

## 📥 Download Commands

### Download single gallery
```bash
python -m cli.main download gallery https://hentaifox.com/gallery/147838/
```

### Download with conversion
```bash
# Download and convert to PDF
python -m cli.main download gallery https://hentaifox.com/gallery/147838/ --convert pdf

# Download, convert to CBZ, and delete original images
python -m cli.main download gallery https://hentaifox.com/gallery/147838/ --convert cbz --delete-images

# Download with custom quality
python -m cli.main download gallery https://hentaifox.com/gallery/147838/ --convert pdf --quality 95
```

### Download multiple galleries
```bash
python -m cli.main download batch url1 url2 url3
```

### Get gallery info (without downloading)
```bash
python -m cli.main info https://hentaifox.com/gallery/147838/
```

## Search Commands

### Search by query (single page)
```bash
python -m cli.main search query "Welcome to the Youth Club"
```

### Search by query (page range)
```bash
python -m cli.main search query "manga" --page 1 --page-end 3 --limit 20
```

### Search by tag (single page)
```bash
python -m cli.main search tag "schoolgirl"
```

### Search by tag (page range)
```bash
python -m cli.main search tag "schoolgirl" --page 1 --page-end 2
```

### Search and download in one command
```bash
python -m cli.main search download "search term" --limit 5
```

### Show current config
```bash
python -m cli.main config
```

### Download history & stats
```bash
python -m cli.main history              # Recent downloads
python -m cli.main history --limit 50   # Show more entries
python -m cli.main history --search "term"  # Search history
python -m cli.main stats                # Download statistics
```

### Test system components
```bash
python -m cli.main test  # Test gallery-dl, aria2c, and HentaiFox parsing
```

## 🎯 Complete Workflow Examples

### Basic Workflow
```bash
# 1. Setup and test
python -m cli.main setup
python -m cli.main test

# 2. Enable turbo mode
python -m cli.main perf turbo

# 3. Download gallery
python -m cli.main download gallery https://hentaifox.com/gallery/147838/
```

### Advanced Workflow with Conversion
```bash
# 1. Enable turbo mode and auto-conversion
python -m cli.main perf turbo
python -m cli.main convert auto pdf --delete-source

# 2. Download (will auto-convert to PDF and delete images)
python -m cli.main download gallery https://hentaifox.com/gallery/147838/

# 3. Check results
python -m cli.main history
python -m cli.main stats
```

### Batch Processing Workflow
```bash
# 1. Search and download multiple galleries
python -m cli.main search download "schoolgirl" --limit 5

# 2. Convert existing downloads to CBZ
python -m cli.main convert batch "C:\Downloads\HFox" --format cbz

# 3. View statistics
python -m cli.main stats
```

## 🔧 Advanced Options

### Download Options
- `--output` / `-o` - Custom output directory
- `--force` / `-f` - Force download even if exists
- `--convert` / `-c` - Convert to format (pdf, cbz)
- `--delete-images` - Delete images after conversion
- `--quality` / `-q` - Image quality (1-100)

### Search Options
- `--page` / `-p` - Starting page number
- `--page-end` - Ending page number (for ranges)
- `--limit` / `-l` - Max results per page

### Conversion Options
- `--format` / `-f` - Output format (pdf, cbz)
- `--delete-source` / `-d` - Delete source images
- `--quality` / `-q` - Image quality (1-100)
- `--output` / `-o` - Custom output path

## 📋 File Formats

### Supported Input Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- GIF (.gif)
- BMP (.bmp)

### Output Formats
- **PDF**: Universal format, great for tablets/e-readers
- **CBZ**: Comic Book ZIP, works with comic readers

## 🔍 Search Selection Options
When searching, you can select galleries to download:
- Single number: `3`
- Range: `1-5`
- Multiple: `1,3,5`
- All galleries: `all`
- Cancel: `none`, `q`, or empty input

## 📖 Additional Resources

- **[Performance Guide](PERFORMANCE_GUIDE.md)** - Detailed performance optimization
- **[Conversion Guide](CONVERSION_GUIDE.md)** - Complete conversion documentation
- **[README.md](README.md)** - Project overview and setup

## 📚 Conversion Commands

### Convert existing galleries
```bash
# Convert single gallery to PDF
python -m cli.main convert gallery "C:\Downloads\HFox\Gallery Name" --format pdf

# Convert to CBZ and delete source images
python -m cli.main convert gallery "path/to/gallery" --format cbz --delete-source

# Convert with custom quality
python -m cli.main convert gallery "path/to/gallery" --format pdf --quality 95
```

### Batch conversion
```bash
# Convert all galleries in a directory to PDF
python -m cli.main convert batch "C:\Downloads\HFox" --format pdf

# Convert matching pattern to CBZ
python -m cli.main convert batch "Downloads" --pattern "*2024*" --format cbz --delete-source
```

### Auto-conversion setup
```bash
# Enable auto-conversion to PDF for all future downloads
python -m cli.main convert auto pdf

# Enable auto-conversion to CBZ and delete images after
python -m cli.main convert auto cbz --delete-source

# Disable auto-conversion
python -m cli.main convert auto none

# Check current conversion settings
python -m cli.main convert status
```

## 🚀 Performance Commands

### Performance modes
```bash
python -m cli.main perf turbo    # Enable turbo mode (4x faster)
python -m cli.main perf normal   # Restore normal settings
python -m cli.main perf status   # Check current performance mode
```

### Benchmark your setup
```bash
python benchmark.py  # Test normal vs turbo mode performance
```

## 📊 Monitoring & History

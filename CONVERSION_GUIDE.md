# 📚 Conversion Guide - PDF & CBZ Support

## Quick Start

### Download with Conversion
```bash
# Download and convert to PDF
python -m cli.main download gallery <url> --convert pdf

# Download and convert to CBZ, delete images after
python -m cli.main download gallery <url> --convert cbz --delete-images

# Download with custom quality
python -m cli.main download gallery <url> --convert pdf --quality 95
```

### Convert Existing Galleries
```bash
# Convert single gallery to PDF
python -m cli.main convert gallery "path/to/gallery" --format pdf

# Convert to CBZ and delete source images
python -m cli.main convert gallery "path/to/gallery" --format cbz --delete-source

# Batch convert all galleries in a directory
python -m cli.main convert batch "path/to/downloads" --format pdf
```

### Auto-Conversion Setup
```bash
# Enable auto-conversion to PDF for all future downloads
python -m cli.main convert auto pdf

# Enable auto-conversion to CBZ and delete images
python -m cli.main convert auto cbz --delete-source

# Disable auto-conversion
python -m cli.main convert auto none

# Check current settings
python -m cli.main convert status
```

## Supported Formats

### PDF Format
- **Best for**: Reading on tablets, e-readers, sharing
- **Features**: 
  - High-quality image compression
  - Optimized for reading devices
  - Smaller file sizes
  - Universal compatibility

### CBZ Format (Comic Book ZIP)
- **Best for**: Comic book readers, archival
- **Features**:
  - Native comic reader support
  - Preserves original image quality
  - Easy to extract individual images
  - Standard comic book format

## Configuration Options

### PDF Settings
```bash
# Set PDF quality (1-100, default: 85)
python -m cli.main convert gallery "path" --format pdf --quality 95

# Max image width for PDFs (default: 2048px)
# Edit config: conversion.max_image_width
```

### CBZ Settings
```bash
# CBZ compression level (0-9, default: 6)
# Edit config: conversion.cbz_compression

# CBZ image quality (1-100, default: 90)
# Edit config: conversion.cbz_quality

# Max image width for CBZ (default: 1920px)
# Edit config: conversion.max_cbz_width
```

## Advanced Usage

### Batch Operations
```bash
# Convert all galleries matching pattern
python -m cli.main convert batch "/downloads" --pattern "*hentai*" --format pdf

# Convert with specific settings
python -m cli.main convert batch "/downloads" --format cbz --delete-source
```

### Custom Output Paths
```bash
# Specify output file
python -m cli.main convert gallery "gallery_dir" --output "custom_name.pdf"

# Output to different directory
python -m cli.main convert gallery "gallery_dir" --output "/path/to/output.cbz"
```

### Quality Optimization
```bash
# High quality PDF (larger file)
python -m cli.main convert gallery "dir" --format pdf --quality 95

# Compressed CBZ (smaller file)
# Edit config: conversion.cbz_compression = 9
```

## File Management

### Source Image Handling
- **Keep images**: Default behavior, images remain after conversion
- **Delete images**: Use `--delete-source` or `--delete-images` flags
- **Auto-delete**: Configure with `convert auto <format> --delete-source`

### Directory Structure
```
Downloads/
├── Gallery 1/
│   ├── 001.jpg
│   ├── 002.jpg
│   └── Gallery 1.pdf     # Converted file
├── Gallery 2/
│   └── Gallery 2.cbz     # Images deleted after conversion
```

## Configuration File

Edit `~/.hfox/config.yaml` for persistent settings:

```yaml
conversion:
  auto_convert: true
  default_format: "pdf"
  delete_source_after_conversion: false
  pdf_quality: 85
  max_image_width: 2048
  cbz_compression: 6
  cbz_quality: 90
  max_cbz_width: 1920
  optimize_cbz_images: false
```

## Performance Tips

### For Speed
- Use CBZ format (faster than PDF)
- Lower compression levels
- Disable image optimization
- Keep source images (no deletion overhead)

### For Quality
- Use PDF format with high quality (90-95)
- Enable CBZ image optimization
- Higher compression for smaller files

### For Storage
- Enable auto-delete of source images
- Use higher compression levels
- Lower quality settings (70-80)

## Troubleshooting

### Common Issues

**"No image files found"**
- Check directory contains .jpg, .png, .webp, etc.
- Verify directory path is correct

**"Conversion failed"**
- Install Pillow: `pip install Pillow`
- Check disk space
- Verify write permissions

**Large file sizes**
- Reduce quality setting
- Increase compression level
- Enable image optimization

### Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- GIF (.gif)
- BMP (.bmp)

## Examples

### Complete Workflow
```bash
# 1. Enable turbo mode for fast downloads
python -m cli.main perf turbo

# 2. Set auto-conversion to PDF with source deletion
python -m cli.main convert auto pdf --delete-source

# 3. Download gallery (will auto-convert and delete images)
python -m cli.main download gallery https://hentaifox.com/gallery/12345/

# 4. Check conversion status
python -m cli.main convert status
```

### Batch Processing Existing Downloads
```bash
# Convert all existing galleries to CBZ
python -m cli.main convert batch "C:\Users\user\Downloads\HFox" --format cbz

# Convert only specific galleries
python -m cli.main convert batch "C:\Downloads" --pattern "*2024*" --format pdf
```

### Custom Quality Settings
```bash
# High quality for archival
python -m cli.main convert gallery "gallery" --format pdf --quality 100

# Balanced quality/size
python -m cli.main convert gallery "gallery" --format cbz --quality 85

# Small file size
python -m cli.main convert gallery "gallery" --format pdf --quality 70
```

## Integration with Downloads

The conversion system integrates seamlessly with the download process:

1. **Manual conversion**: Use `--convert` flag during download
2. **Auto-conversion**: Enable with `convert auto` command
3. **Post-download**: Convert existing galleries anytime

This gives you complete flexibility in how you manage your manga collection!
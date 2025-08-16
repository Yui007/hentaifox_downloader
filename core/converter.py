"""Image to PDF/CBZ converter for downloaded galleries."""

import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass
from PIL import Image
import tempfile

from config.settings import config
from cli.utils.display import display


@dataclass
class ConversionResult:
    """Result of a conversion operation."""
    success: bool
    output_path: Optional[Path]
    input_files_count: int
    error_message: Optional[str] = None


class GalleryConverter:
    """Converts downloaded image galleries to PDF or CBZ format."""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}
    
    def get_image_files(self, directory: Path) -> List[Path]:
        """Get all image files from directory, sorted naturally."""
        if not directory.exists():
            return []
        
        image_files = []
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                image_files.append(file_path)
        
        # Sort naturally (1, 2, 10 instead of 1, 10, 2)
        return sorted(image_files, key=lambda x: self._natural_sort_key(x.name))
    
    def _natural_sort_key(self, text: str) -> List:
        """Generate natural sorting key for filenames."""
        import re
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]
    
    def convert_to_pdf(self, source_dir: Path, output_path: Optional[Path] = None, 
                      delete_source: bool = False, quality: Optional[int] = None) -> ConversionResult:
        """Convert image gallery to PDF format."""
        try:
            image_files = self.get_image_files(source_dir)
            if not image_files:
                return ConversionResult(
                    success=False,
                    output_path=None,
                    input_files_count=0,
                    error_message="No image files found in directory"
                )
            
            # Determine output path
            if output_path is None:
                output_path = source_dir / f"{source_dir.name}.pdf"
            
            # Convert images to PDF
            pdf_images = []
            temp_files = []
            
            for img_path in image_files:
                try:
                    # Open and convert image
                    img = Image.open(img_path)
                    
                    # Convert to RGB if necessary (PDF requires RGB)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Optimize image size if too large
                    max_width = config.get("conversion.max_image_width", 2048)
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    
                    pdf_images.append(img)
                    
                except Exception as e:
                    display.print_warning(f"Skipping {img_path.name}: {e}")
                    continue
            
            if not pdf_images:
                return ConversionResult(
                    success=False,
                    output_path=None,
                    input_files_count=len(image_files),
                    error_message="No images could be processed"
                )
            
            # Save as PDF
            pdf_quality = quality if quality is not None else config.get("conversion.pdf_quality", 85)
            pdf_images[0].save(
                output_path,
                format='PDF',
                save_all=True,
                append_images=pdf_images[1:],
                optimize=True,
                quality=pdf_quality
            )
            
            # Clean up PIL images
            for img in pdf_images:
                img.close()
            
            # Delete source files if requested
            if delete_source:
                self._delete_source_files(image_files, source_dir)
            
            return ConversionResult(
                success=True,
                output_path=output_path,
                input_files_count=len(image_files)
            )
            
        except Exception as e:
            return ConversionResult(
                success=False,
                output_path=None,
                input_files_count=len(image_files) if 'image_files' in locals() else 0,
                error_message=str(e)
            )
    
    def convert_to_cbz(self, source_dir: Path, output_path: Optional[Path] = None,
                      delete_source: bool = False, quality: Optional[int] = None) -> ConversionResult:
        """Convert image gallery to CBZ (Comic Book ZIP) format."""
        try:
            image_files = self.get_image_files(source_dir)
            if not image_files:
                return ConversionResult(
                    success=False,
                    output_path=None,
                    input_files_count=0,
                    error_message="No image files found in directory"
                )
            
            # Determine output path
            if output_path is None:
                output_path = source_dir / f"{source_dir.name}.cbz"
            
            # Create CBZ (ZIP) file
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, 
                               compresslevel=config.get("conversion.cbz_compression", 6)) as cbz:
                
                for i, img_path in enumerate(image_files):
                    try:
                        # Use zero-padded numbering for proper sorting in comic readers
                        extension = img_path.suffix.lower()
                        archive_name = f"{i+1:03d}{extension}"
                        
                        # Optionally optimize images before adding to CBZ
                        if config.get("conversion.optimize_cbz_images", False):
                            cbz_quality = quality if quality is not None else config.get("conversion.cbz_quality", 90)
                            optimized_path = self._optimize_image_for_cbz(img_path, cbz_quality)
                            cbz.write(optimized_path, archive_name)
                            if optimized_path != img_path:
                                os.unlink(optimized_path)  # Clean up temp file
                        else:
                            cbz.write(img_path, archive_name)
                            
                    except Exception as e:
                        display.print_warning(f"Skipping {img_path.name}: {e}")
                        continue
            
            # Delete source files if requested
            if delete_source:
                self._delete_source_files(image_files, source_dir)
            
            return ConversionResult(
                success=True,
                output_path=output_path,
                input_files_count=len(image_files)
            )
            
        except Exception as e:
            return ConversionResult(
                success=False,
                output_path=None,
                input_files_count=len(image_files) if 'image_files' in locals() else 0,
                error_message=str(e)
            )
    
    def _optimize_image_for_cbz(self, img_path: Path, quality: int = 90) -> Path:
        """Optimize image for CBZ format."""
        try:
            with Image.open(img_path) as img:
                # Check if optimization is needed
                max_width = config.get("conversion.max_cbz_width", 1920)
                
                if img.width <= max_width and img_path.suffix.lower() in ['.jpg', '.jpeg']:
                    return img_path  # No optimization needed
                
                # Create optimized version
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB if necessary
                if img.mode not in ['RGB', 'L']:
                    img = img.convert('RGB')
                
                # Save optimized version
                temp_path = Path(tempfile.mktemp(suffix='.jpg'))
                img.save(temp_path, format='JPEG', quality=quality, optimize=True)
                return temp_path
                
        except Exception:
            return img_path  # Return original if optimization fails
    
    def _delete_source_files(self, image_files: List[Path], source_dir: Path):
        """Delete source image files and directory if empty."""
        try:
            # Delete image files
            for img_path in image_files:
                if img_path.exists():
                    img_path.unlink()
            
            # Delete directory if empty (or only contains non-image files)
            remaining_files = list(source_dir.iterdir())
            if not remaining_files:
                source_dir.rmdir()
                display.print_info(f"Deleted empty directory: {source_dir.name}")
            else:
                # Check if only non-image files remain
                non_image_files = [f for f in remaining_files 
                                 if f.suffix.lower() not in self.supported_formats]
                if len(non_image_files) == len(remaining_files):
                    display.print_info(f"Kept directory with {len(non_image_files)} non-image files")
                
        except Exception as e:
            display.print_warning(f"Could not delete source files: {e}")
    
    def convert_gallery(self, source_dir: Path, format_type: str, 
                       output_path: Optional[Path] = None,
                       delete_source: bool = False, quality: Optional[int] = None) -> ConversionResult:
        """Convert gallery to specified format."""
        format_type = format_type.lower()
        
        if format_type == 'pdf':
            return self.convert_to_pdf(source_dir, output_path, delete_source, quality)
        elif format_type == 'cbz':
            return self.convert_to_cbz(source_dir, output_path, delete_source, quality)
        else:
            return ConversionResult(
                success=False,
                output_path=None,
                input_files_count=0,
                error_message=f"Unsupported format: {format_type}"
            )


# Global converter instance
converter = GalleryConverter()
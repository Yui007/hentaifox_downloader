from setuptools import setup, find_packages

setup(
    name="hentaifox-downloader",
    version="1.0.0",
    description="A beautiful, modern manga downloader with Aria2c integration",
    packages=find_packages(),
    install_requires=[
        "gallery-dl>=1.26.0",
        "rich>=13.0.0",
        "typer>=0.9.0",
        "PyQt6>=6.5.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "hentaifox-downloader=cli.main:app",
            "hfox=cli.main:app",  # Keep backward compatibility
        ],
    },
    python_requires=">=3.8",
)
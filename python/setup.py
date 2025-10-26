"""Setup configuration for kicad-pcb-api."""

from setuptools import setup, find_packages

setup(
    name="kicad-pcb-api",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "sexpdata>=0.0.3",
        "loguru>=0.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "mypy>=0.950",
        ],
    },
    author="Circuit-Synth Team",
    description="Professional KiCAD PCB manipulation library",
    long_description=open("../README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/circuit-synth/kicad-pcb-api",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

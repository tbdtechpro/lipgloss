"""Setup file for Lip Gloss Python port."""

import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="lipgloss",
    version="0.1.0",
    description="CSS-like terminal styling for Python (port of Go Lip Gloss)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tbdtechpro/lipgloss",
    author="Charm",
    author_email="vt100@charm.sh",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    python_requires=">=3.10",
    install_requires=[
        "wcwidth>=0.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
            "mypy",
            "black",
            "isort",
            "flake8",
        ],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Terminals",
        "Typing :: Typed",
    ],
    keywords=[
        "tui",
        "terminal",
        "cli",
        "console",
        "styling",
        "ansi",
        "lipgloss",
        "charm",
    ],
    package_data={
        "lipgloss": ["py.typed"],
    },
    project_urls={
        "Bug Reports": "https://github.com/tbdtechpro/lipgloss/issues",
        "Source": "https://github.com/tbdtechpro/lipgloss",
        "Original Go Library": "https://github.com/charmbracelet/lipgloss",
    },
)

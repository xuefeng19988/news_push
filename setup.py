#!/usr/bin/env python3
"""
智能新闻推送系统 - 安装配置
版本: 0.0.1
"""

from setuptools import setup, find_packages
import os

# 读取版本号
with open('VERSION', 'r') as f:
    VERSION = f.read().strip()

# 读取README
with open('README.md', 'r', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="news-push-system",
    version=VERSION,
    description="智能新闻+股票推送系统",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="OpenClaw User",
    author_email="user@example.com",
    url="https://github.com/xuefeng19988/news_push",
    packages=find_packages(where=".", include=["src*"]),
    package_dir={"": "."},
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.toml", "VERSION"]
    },
    include_package_data=True,
    install_requires=[
        "requests>=2.28.0",
        "feedparser>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "news-push=src.common.auto_push_system_optimized_final:main",
            "push-status=src.common.auto_push_system_optimized_final:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    license="MIT",
    keywords="news, stock, push, notification, whatsapp",
    project_urls={
        "Homepage": "https://github.com/xuefeng19988/news_push",
        "Repository": "https://github.com/xuefeng19988/news_push.git",
    },
)
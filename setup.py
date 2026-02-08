from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="subctl",
    version="0.1.0",
    author="vim",
    author_email="your-email@example.com",
    description="Sub-Agent Management CLI for distributed AI systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AmosTheBuilder/subctl",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.7.0",
        "redis>=5.0.0",
        "psutil>=5.9.0",
        "cryptography>=41.0.0",
        "pyjwt>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "subctl=subctl.cli:main",
        ],
    },
)

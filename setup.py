from setuptools import setup, find_packages

setup(
    name="omni-shell",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "prompt_toolkit",
        "pygments",
        "rich",
        "google-genai",
        "duckduckgo-search",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "omni=omni.shell:main",
        ],
    },
)

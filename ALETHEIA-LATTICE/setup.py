from setuptools import setup, find_packages
from pathlib import Path

desc = (Path(__file__).parent / "README.md").read_text() if (Path(__file__).parent / "README.md").exists() else ""
setup(
    name="aletheia-lattice",
    version="1.0.0",
    description="Evidence-Bounded Sovereign AI Architecture for National Systems",
    long_description=desc,
    url="https://github.com/deontewatts/ALETHEIA-LATTICE",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["fastapi>=0.111.0","uvicorn[standard]>=0.29.0","pydantic>=2.7.0"],
    extras_require={"dev": ["pytest>=8.0","ruff>=0.4","pytest-cov>=5.0"]},
)

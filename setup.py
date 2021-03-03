"""Installing with setuptools."""
import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycape",
    version="0.0.0",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[],
    license="",
    url="",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="",
    author_email="",
    classifiers=[],
)

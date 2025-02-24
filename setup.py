import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lpitabformer",
    version="1.0.2",
    author="linqin",
    url='https://github.com/Ci-TJ/LPItabformer',
    author_email="1911449@tongji.edu.cn",
    description="Lpitabformer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)

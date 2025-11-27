import setuptools

main_ns = {}
with open('src/cliasi/__about__.py') as ver_file:
    exec(ver_file.read(), main_ns)

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setuptools.setup(
    name="cliasi",
    version=main_ns["__version__"],
    author="Qrashi",
    author_email="fritz@vibe.ac",
    description="Have a nice looking, simple cli in seconds",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Qrashi/cliasi",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
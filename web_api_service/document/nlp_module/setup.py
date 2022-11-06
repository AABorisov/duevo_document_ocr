import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Document Understanding",
    version="0.1.0",
    author="Ushakov Alexey",
    author_email="kafka.pochta@gmail.com",
    description="Parsing and analyzing documents",
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dearkafka/doc",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ),
    zip_safe=False,
    platforms='any'
)

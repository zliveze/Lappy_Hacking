from setuptools import setup, find_packages

# Đọc README.md với encoding UTF-8
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lappy-hacking",
    version="2.1",
    packages=find_packages(),
    install_requires=[
        "Pillow>=9.0.0",
    ],
    author="Nguyen Ky",
    author_email="zliveze@gmail.com",
    description="A tool for managing and fixing ID-related issues in development applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Letandat071/Lappy_Hacking",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "lappy-hacking=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["public/image/*"],
    },
) 
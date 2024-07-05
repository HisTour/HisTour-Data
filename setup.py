from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="histour-ai",
    version="0.1",
    description="AI Server For Histour Service",
    packages=find_packages(),
    author="suwonpabby",
    author_email="leeuj9663@naver.com",
    install_requires=requirements
)

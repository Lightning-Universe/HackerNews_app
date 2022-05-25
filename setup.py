import setuptools

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="hackernews_app",
    version="0.0.1",
    description="Personalized HackerNews stories for you!",
    author="Grid.ai",
    packages=setuptools.find_packages(where="hackernews_app*"),
    install_requires=[requirements],
    include_package_data=False,
    python_requires=">=3.8",
)

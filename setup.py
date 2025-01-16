from setuptools import setup, find_packages

setup(
    name="odia_learning",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "azure-cognitiveservices-speech>=1.31.0",
        "python-dotenv>=1.0.0",
        "sounddevice>=0.4.6",
    ],
) 
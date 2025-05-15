from setuptools import setup, find_packages

setup(
    name='agri-picking-robot',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A control program for an agricultural picking robot utilizing a Gemini335 depth camera.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'opencv-python',  # For video capture and processing
        'numpy',          # For numerical operations
        'scikit-learn',   # For machine learning model interactions
        'tensorflow',     # If using TensorFlow for the model
        'robotics-toolbox',  # Hypothetical library for robotics control
    ],
    entry_points={
        'console_scripts': [
            'agri-picking-robot=main:main',  # Adjust according to the main function in main.py
        ],
    },
)
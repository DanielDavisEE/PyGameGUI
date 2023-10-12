from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='pygame-gui',
    version='1.0',
    author='Daniel Davis',
    description='',
    long_description=long_description,
    url='https://github.com/DanielDavisEE/PyGameGUI',
    python_requires='>=3.10, <4',
    package_dir={'': 'src'},
    packages=['pygame_gui'],
    install_requires=[
        'pyperclip',
        'pygame'
    ],
    package_data={
    },
    entry_points={
    }
)

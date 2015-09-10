
# Thanks: http://pythonhosted.org/an_example_pypi_project/setuptools.html

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "jp_svg_canvas",
    version = "0.0.1",
    author = "Aaron Watters",
    author_email = "awatters@simonsfoundation.org",
    description = ("A very simple SVG canvas proxy widget for Jupyter visualizations."),
    license = "BSD",
    keywords = "svg jupyter widget",
    url = "http://packages.python.org/jp_svg_canvas",
    packages=['jp_svg_canvas'],
    package_data={'jp_svg_canvas': ['*.js']},
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
    ],
)

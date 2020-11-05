# Copyright 2020 Álvaro Justen <https://github.com/turicas/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import setuptools

with open("README.md", mode="r") as fobj:
    long_description = fobj.read()

with open("requirements.txt", mode="r") as fobj:
    requirements = [line.strip() for line in fobj if line.strip() and not line.strip().startswith("#")]

setuptools.setup(
    name="contributor-network",
    version="0.1.0dev0",
    author="Álvaro Justen",
    author_email="alvarojusten@gmail.com",
    description="Create an interactive contributor network graph from git/hg repository",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pythoniccafe/contributor-network/",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    keywords="free-software open-source contributor graph network",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
)

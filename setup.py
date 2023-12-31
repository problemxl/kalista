# -*- coding: utf-8 -*-
from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

packages = \
['kalista', 'kalista.models']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp==3.9.0',
 'decorators',
 'loguru',
 'pandas>=2.0.2,<3.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'pydantic',
 'requests>=2.31.0,<3.0.0']

setup_kwargs = {
    'name': 'kalista',
    'version': '0.1.4',
    'description': '',
    "long_description"=long_description,
    "long_description_content_type"='text/markdown',
    'author': 'Mark Franciscus',
    'author_email': 'mark.franciscus@hotmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)


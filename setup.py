from setuptools import setup

setup(name='ledger_api_client',
      version='1.27',
      description='Ledger API Client',
      url='https://github.com/dbca-wa/ledger_api_client',
      author='Department of Parks and Wildlife',
      author_email='asi@dbca.wa.gov.au',
      license='BSD',
      packages=['ledger_api_client','ledger_api_client.migrations','ledger_api_client.management','ledger_api_client.management.commands',
                ],
      install_requires=[],
      include_package_data=True,
      zip_safe=False)


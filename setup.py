import setuptools

setuptools.setup(
    name='Payment',
    version='0.0.6',
    author='Pochang Lee',
    author_email='stupidgod08@yahoo.com.tw',
    description='A django package made for handling third party payment',
    long_description='A django package made for handling third party payment',
    long_description_content_type='text/markdown',
    url='https://github.com/pochangl/django-payment',
    install_requires=[
        'django',
        'mysqlclient',
        'requests',
        'djangorestframework',
    ],
    packages=setuptools.find_packages(
        exclude = [
            'test-server'
        ]
    ),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 1 - Planning',
    ],
)

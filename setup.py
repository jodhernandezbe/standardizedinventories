from setuptools import setup

setup(
    name="StEWI",
    version="0.9.2",
    author="Wesley Ingwersen, Matthew Bergman, Jose Hernandez-Betancur, Tapajyoti Ghosh, Mo Li",
    author_email="ingwersen.wesley@epa.gov",
    description="Standardized Emission And Waste Inventories (StEWI)"
                "provides processed EPA release and emissions inventories "
                "in standard tabular format",
    license="CC0",
    keywords="USEPA data",
    url="http://www.github.com/usepa/standardizedinventories",
    packages=['chemicalmatcher', 'facilitymatcher', 'stewi', 'stewicombo'],
    #Must include package data, specifying all subdirectories to be included
    #https://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files
    package_data={'stewi': ["data/*.*",
                            "output/*.*",
                            "output/facility/*.*",
                            "output/flow/*.*",
                            "output/flowbyfacility/*.*",
                            "output/validation/*.*"],
                  'chemicalmatcher': ["data/*.*", "output/*.*"],
                  'facilitymatcher': ["data/*.*", "output/*.*"]},
    include_package_data=True,
    install_requires=['numpy>=1.16', 'pandas>=0.22', 'requests>=2.20',
                      'bs4', 'argparse', 'regex', 'selenium','PyYAML>=5.1',
                      'webdriver-manager'],
    classifiers=[
        "Development Status :: Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: CC0",
        "Programming Language :: Python :: 3.x",
        "Topic :: Utilities",
    ]
)

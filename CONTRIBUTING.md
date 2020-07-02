# Contributing

Before suggesting a new change please see the [project boards](https://github.com/mcfadd/Job_Shop_Schedule_Problem/projects) for currently planned changes as well as the [development branch](https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/development).

When contributing to this repository, discuss the change you wish to make via issue,
email, or pull request conversation.

If you would like to become a collaborator so you have direct write access, contact the repository owner at mrfadd8@gmail.com

### Code of Conduct
We have a code of conduct for this project [here](https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/CODE_OF_CONDUCT.md).

### Pull Request Process

1. Create a fork of the repository
2. Make your changes to the fork
3. Create a pull request from the fork by following [this guide][fork pull request]

[fork pull request]:https://help.github.com/en/articles/creating-a-pull-request-from-a-fork

### Versioning

JSSP is versioned using [Semantic Versioning 2.0.0](https://semver.org/).

Given a version number MAJOR.MINOR.PATCH, increment the:   

- MAJOR version when you make incompatible API changes,  
- MINOR version when you add functionality in a backwards compatible manner, and  
- PATCH version when you make backwards compatible bug fixes.   

Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.  
    
### Releasing

When releasing a new version make sure to increment the versions in the following files:
- README.md
- setup.py
- docs/conf.py
- sonar-project.properties

Releases happen automatically in the Continuous Delivery (CD) stage of the CircleCI pipeline. 
To trigger a release create an annotated git tag with the name of the version (i.e. MAJOR.MINOR.PATCH).

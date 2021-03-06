.. :changelog:

Release History
------------------

0.2.3 (2015-05-07)
^^^^^^^^^^^^^^^^^^

* Add the possibility to specify the remote to use (default is origin)
* Internal changes:
    - Refactor code to use separated commands
    - Add console class to better handle console output
    - Add config class to handle config options

0.2.2 (2015-04-19)
^^^^^^^^^^^^^^^^^^

* Switch to argparse module for command line interface

0.2.1 (2015-04-14)
^^^^^^^^^^^^^^^^^^

**Bugfixes**

* Fix rsync exclude command build error

0.2.0 (2015-04-14)
^^^^^^^^^^^^^^^^^^

* Use common git files such as .gitignore, .gitmodules, .gitkeep and the .git 
  directory as default exclude patterns when building the rsync command

0.1.0 (2015-04-14)
^^^^^^^^^^^^^^^^^^

* Initial public release

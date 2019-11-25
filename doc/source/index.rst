.. _dl-index:

dL: Documentation Library
=================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   glossary

.. contents::

*dL* (documentation Library) is a tool that enables managing all documentation
from a common environment. In this environment, you can efficiently work with
selected projects and share their resources: code samples, graphics, fragments
of text, variables (such as reStructuredText replace directives) and so on.


Setting up
================================================================================

To be able to experiment with *dL*, you need to prepare your environment
manually. The setup includes the following steps:

#. Install python3 and related libraries which are not included into the
   standard library.
#. Set up Jira to enable looking up ticket IDs from the site.
#. Create the library directory with *lib* and *meta* sub directories.
#. Create a workspace directory.


Installing python3 and related libraries
--------------------------------------------------------------------------------

Python3 is usually already installed on all major Linux
distributions. If not, use your package management software. To
provide integration with *Git* and *JIRA*, dL uses the *gitpython* and
*jira* libraries. To install the correct versions of these libraries,
run *pip* (or *pip3*) using the *requirements.txt* file in the *src* directory.

.. code-block:: bash

   $ cd root-dir/src
   # sudo pip3 install -r requirements.txt

Setting up JIRA
--------------------------------------------------------------------------------

To connect to the JIRA site, the *jira* library must be provided with the
following information: the site URL, user name, and user password. In this early
implementation, it is expected that you specify these settings in the *.netrc*
file in your home directory. Add the following lines to
*/home/your-user-name/.netrc*:

.. code-block:: text

   machine https://jira.percona.com
   login user.jira.name
   password Y0uRp@$$w8Rd

Creating the library directory
--------------------------------------------------------------------------------

The library is the permanent storage of the documentation project assets. The
library consists of two directories: *lib* for storing all files that make up
projects, and *meta* for storing meta data that help determine which files
belong to specific projects.

To make it usable, *cd* into the directory where you plan to deploy the library
and complete the following steps:

.. code-block:: bash

   $ mkdir -p documentation-library/lib
   $ mkdir -p documentation-library/meta
   $ cd documentation-library
   $ touch dL
   $ git init
   $ git add .
   $ git commit -m "Install documentation library"

Note that you may replace *documentation-library* with any other name. You can
also use your own names for *lib* and *meta*. Your commit message can also be
different. It is important, though, that you create a git repository and have a
commit in it.

Now, change to the directory that contains the sources (*src*) and open
*src/options.yaml* using any text editor. You need to set the following options in it:

.. code-block:: yaml

   ...
   path:
     data_dir: /home/your-user-name/documentation-library
     ...
   dir_name:
     meta: meta
     lib: lib
   ...

If your setup differs and you decide to use another data directory (see
*documentation-library*), or different names for sub directories (such as *meta*
and *lib*), edit this file accodingly.

Creating the workspace directory
--------------------------------------------------------------------------------

The workspace is a directory that contains files related to documentation
projects. When you need to update documentation of a specific project you
receive relevant files from the library. Then you load the modified files back
to the library.

The workspace is not a permanent storage. Its sub directories can be deleted
after you finish updating your documentation project.

As the workspace, you can use any empty directory:

.. code-block:: bash

   $ mkdir /home/your-user-name/workspace

In this example, you use the *workspace* directory in your */home* directory.

To use this workspace, update your options file. First, *cd* to the directory
that contains the sources (*src*). Open *src/options.yaml* in any text editor and
set the *workspace* option under *path*:

.. code-block:: yaml

   path:
     workspace: /home/your-user-name/workspace


Operations
================================================================================

All tasks are performed via the sub commands of the :abbrev:`dli* (documentation
library interface)`. Each sub command may have its own set of required and
optional parameters. The program may modify the library or the workspace. Other
locations are only reached for reading.

Adding an existing documentation project
================================================================================




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

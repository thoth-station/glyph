Glyph
-----

Glyph uses Machine Learning and Natural Language Processing to understand
commit messages. This knowledge can be used for classifying commits into
categories such as Bug-fixes, Feature additions, Improvements etc.

* Using Glyph with `Kebechet <https://github.com/thoth-station/kebechet>`_,
  smart CHANGELOG entries out of commit messages can be generated.

* Glyph can also be used as a standlone library for analyzing commits from a
  locally stored repository (see usage below)

Running this project from Git
=============================

.. code-block:: console

  git clone git@github.com:thoth-station/glyph.git  # or use https
  cd glyph
  pipenv install --dev
  PYTHONPATH=. pipenv run ./thoth-glyph --help


Installing this project from PyPI
=================================

This project is available on PyPI, to install it:

.. code-block:: console

  pip install thoth-glyph

Features
========

* **Commit Classification:** Singular commits can be classified using the
  following command:

  .. code-block:: console

    thoth-glyph classify -m "COMMIT MESSAGE TO BE ANALYZED"

* **Classifying Multiple Commits:** Mulitple commit can be classified together
  using the classify-repo command. By default, this action classifies all the
  commits in the repository. Optionally, a date-range (YYYY-MM-DD) can be
  provided:

  .. code-block:: console

    thoth-glyph classify-repo --path /path/to/git/repo --start 2020-05-01 --end 2020-05-10

* **Classifying Using Tags:** Commits can also be picked using git tags. The
  following command will pick commits between the tags v3.7.1 and v3.7.2

  .. code-block:: console

    thoth-glyph classify-repo-by-tag --path /path/to/git/repo --start_tag v3.7.1 --end_tag v3.7.2

Sample Usage
============

.. code-block:: console

  $ thoth-glyph classify -m "Fixed server bug that impacted performance"
  2020-08-12 19:45:47,798 4594 WARNING  thoth.common:346: Logging to a Sentry instance is turned off
  2020-08-12 19:45:47,799 4594 INFO     thoth.common:368: Logging to rsyslog endpoint is turned off
  2020-08-12 19:45:47,799 4594 INFO     glyph:68: Version: 0.0.0
  2020-08-12 19:45:47,800 4594 INFO     glyph:83: Classifying commit
  2020-08-12 19:45:47,800 4594 INFO     thoth.glyph.models:33: Model Path : /home/tussharm/.local/lib/python3.6/site-     packages/thoth/glyph/data/model_commits_v2_quant.bin
  Label : corrective

.. code-block:: console

  $ thoth-glyph classify-repo --path /home/tussharm/fork/glyph/ --start 2020-08-08 --end 2020-08-12
  2020-08-12 19:51:26,743 4873 WARNING  thoth.common:346: Logging to a Sentry instance is turned off
  2020-08-12 19:51:26,743 4873 INFO     thoth.common:368: Logging to rsyslog endpoint is turned off
  2020-08-12 19:51:26,744 4873 INFO     glyph:68: Version: 0.0.0
  2020-08-12 19:51:26,744 4873 INFO     glyph:100: Classifying commits in the given date-range
  2020-08-12 19:51:26,749 4873 INFO     thoth.glyph.models:44: Model Path : /home/tussharm/.local/lib/python3.6/site-p    packages/thoth/glyph/data/model_commits_v2_quant.bin
  2020-08-12 19:51:26,768 4873 INFO     thoth.glyph.models:52: 6 commits classified
                                             message labels_predicted
  0                                 readme updated #27       perfective
  1  merge pull request #1 from tushar7sharma/commi...    nonfunctional
  2  merge remote-tracking branch 'upstream/master'...         features
  3  grouping user-defined commit phrases (#28)* co...         features
  4  commits can be collected inside user-defined g...         features
  5  merge remote-tracking branch 'upstream/master'...         features

Integration with Kebechet
=========================

Kebechet can use Glyph by reading the project's configuration from .thoth.yaml
file. Glyph's supported formatters and ML classifers can be specified in this
configuration file.

* See sample manager configuration `here
  <https://github.com/thoth-station/kebechet/tree/master/kebechet/managers/version>`__

* See sample changelog generated using Glyph `here
  <https://github.com/tushar7sharma/release-log-test/blob/master/SAMPLE_CHANGELOG.md>`__

Model and Dataset
=================

Currently Glyph ships with a model trained using Facebook's `fasttext
<https://fasttext.cc/>`_ library over a dataset of ~5000 commits collected from
multiple large-scale open source projects (see referred publications for more
details). The library can be easily extended to accomodate more models.
Developers are welcome to contribute and improve the classification accuracy.

References
==========

* https://arxiv.org/pdf/1711.05340.pdf
* http://labsoft.dcc.ufmg.br/lib/exe/fetch.php?media=cibse-geanderson.pdf
* https://github.com/gesteves91/fasttext-commit-classification
* https://github.com/nxs5899/Multi-Class-Text-Classification----Random-Forest

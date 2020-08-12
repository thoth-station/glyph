Glyph
-----
Glyph uses Machine Learning and Natural Language Processing to understand commit messages. This knowledge can be used for classifying commits into categories such as Bug-fixes, Feature additions, Improvements etc. 

* Using Glyph with `Kebechet <https://github.com/thoth-station/kebechet>`_, smart CHANGELOG entries out of commit messages can be generated.
* Glyph can also be used as a standlone library for analyzing commits from a locally stored repository (see usage below)

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
  
Features & Usage
=================================
* **Commit Classification:** Singular commits can be classified using the following command:
.. code-block:: console

  thoth-glyph classify -m "COMMIT MESSAGE TO BE ANALYZED"
  
* **Classifying Multiple Commits:** Mulitple commit can be classified together using the classify-repo command. By default, this action classifies all the commits in the repository. Optionally, a date-range (YYYY-MM-DD) can be provided:
.. code-block:: console

  thoth-glyph classify-repo --path /path/to/git/repo --start 2020-05-01 --end 2020-05-10
  
* **Classifying Using Tags:** Commits can also be picked using git tags. The following command will pick commits between the tags v3.7.1 and v3.7.2
.. code-block:: console

  thoth-glyph classify-repo-by-tag --path /path/to/git/repo --start_tag v3.7.1 --end_tag v3.7.2
  
Model and Dataset
=================================
Currently Glyph ships with a model trained using Facebook's `fasttext <https://fasttext.cc/>`_ library over a dataset of ~5000 commits collected from multiple large-scale open source projects (see referred publications for more details). The library can be easily extended to accomodate more models. Developers are welcome to contribute and improve the classification accuracy.

References
=================================
* https://arxiv.org/pdf/1711.05340.pdf
* http://labsoft.dcc.ufmg.br/lib/exe/fetch.php?media=cibse-geanderson.pdf
* https://github.com/gesteves91/fasttext-commit-classification
* https://github.com/nxs5899/Multi-Class-Text-Classification----Random-Forest

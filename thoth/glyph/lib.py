import logging
import os
from os import path
from thoth.common import init_logging
from fasttext import load_model

import pandas as pd
from pygit2 import Repository
from pygit2 import GIT_SORT_TOPOLOGICAL

import time
import datetime
import sys

init_logging()
_LOGGER = logging.getLogger("glyph")
DEFAULT_MODEL_PATH = path.join(path.dirname(__file__), 'data/model_commits_v2_quant.bin')


def classify_by_date(path, start, end, output, model):
    start_time = 0
    end_time = sys.maxsize

    if start is not None:
        start_time = int(time.mktime(datetime.datetime.strptime(start, "%Y-%m-%d").timetuple()))

    if end is not None:
        end_time = int(time.mktime(datetime.datetime.strptime(end, "%Y-%m-%d").timetuple()))

    repo_path = os.path.join(path, ".git")
    if os.path.exists(repo_path):
        repo = Repository(repo_path)
    else:
        _LOGGER.error("Git repository not found")
        return

    orig_messages = []
    for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):
        if(commit.commit_time > start_time and commit.commit_time < end_time):
             orig_messages.append(commit.message.lower())

    classify_messages(orig_messages, model, output)


def classify_by_tag(path, start_tag, end_tag, output, model):
    repo_path = os.path.join(path, ".git")
    if os.path.exists(repo_path):
        repo = Repository(repo_path)
    else:
        _LOGGER.error("Git repository not found")
        return

    start_tag = repo.revparse_single('refs/tags/' + start_tag)

    if end_tag is None:
        end_tag = repo.revparse_single('refs/heads/master')
    else:
        end_tag = repo.revparse_single('refs/tags/' + end_tag)

    orig_messages = []
    walker = repo.walk(end_tag.id, GIT_SORT_TOPOLOGICAL)
    walker.hide(start_tag.id)

    for commit in walker:
        orig_messages.append(commit.message.lower())
    
    classify_messages(orig_messages, model, output)


def classify_messages(messages, model, output):
    if(messages is None or len(messages) == 0):
        _LOGGER.error("No commits found!")
        return

    df = pd.DataFrame(messages, columns = ['message'])
    df = df.replace('\n','', regex=True)
    commits = list(df['message'].astype(str))
    if model is None:
        _LOGGER.info("Using default model")
        model = DEFAULT_MODEL_PATH
    elif not os.path.exists(model):
        _LOGGER.error("Model not found, using default model instead")
        model = DEFAULT_MODEL_PATH

    _LOGGER.info("Model Path : " + model)
    classifier = load_model(model)
    labels = classifier.predict(commits)
    res = list(zip(*labels))
    res_list = [x[0] for x in res]
    lst2 = [item[0] for item in res_list]
    df['labels_predicted'] = lst2
    if output is None:
        print(df)
    else:
        df.to_csv(output, sep='\t')

    print(str(len(messages)) + " commits classified")

def classify_message(message, model):
    if message is None or message == "":
        _LOGGER.error("Please enter commit message")
        return
    if model is None:
        _LOGGER.info("Using default model")
        model = DEFAULT_MODEL_PATH
    elif not os.path.exists(model):
        _LOGGER.error("Model not found, using default model instead")
        model = DEFAULT_MODEL_PATH

    _LOGGER.info("Model Path : " + model)
    classifier = load_model(model)
    label = classifier.predict(message.lower())
    print("Label : " + str(label[0][0])[9:])
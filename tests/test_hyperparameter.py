import shutil

import pytest
from hyperopt import hp

from flair.data_fetcher import NLPTaskDataFetcher, NLPTask
from flair.embeddings import WordEmbeddings, StackedEmbeddings, CharLMEmbeddings
from flair.hyperparameter import SearchSpace, Parameter, SequenceTaggerParamSelector, TextClassifierParamSelector


@pytest.mark.integration
def test_sequence_tagger_param_selector(results_base_path, tasks_base_path):
    corpus = NLPTaskDataFetcher.fetch_data(NLPTask.FASHION, base_path=tasks_base_path)

    # define search space
    search_space = SearchSpace()

    # sequence tagger parameter
    search_space.add(Parameter.EMBEDDINGS, hp.choice, options=[
        StackedEmbeddings([WordEmbeddings('glove')]),
        StackedEmbeddings([WordEmbeddings('glove'), CharLMEmbeddings('news-forward'), CharLMEmbeddings('news-backward')])
    ])
    search_space.add(Parameter.USE_CRF, hp.choice, options=[True, False])
    search_space.add(Parameter.DROPOUT, hp.uniform, low=0.25, high=0.75)
    search_space.add(Parameter.WORD_DROPOUT, hp.uniform, low=0.0, high=0.25)
    search_space.add(Parameter.LOCKED_DROPOUT, hp.uniform, low=0.0, high=0.5)
    search_space.add(Parameter.HIDDEN_SIZE, hp.choice, options=[64, 128, 256, 512])
    search_space.add(Parameter.RNN_LAYERS, hp.choice, options=[1, 2])

    # training parameter
    search_space.add(Parameter.MINI_BATCH_SIZE, hp.choice, options=[4, 8, 32])
    search_space.add(Parameter.LEARNING_RATE, hp.uniform, low=0.01, high=1)
    search_space.add(Parameter.ANNEAL_FACTOR, hp.uniform, low=0.3, high=0.75)
    search_space.add(Parameter.PATIENCE, hp.choice, options=[3, 5])

    # find best parameter settings
    optimizer = SequenceTaggerParamSelector(corpus, 'ner', str(results_base_path), max_epochs=2)
    optimizer.optimize(search_space, max_evals=2)

    # clean up results directory
    shutil.rmtree(results_base_path)


@pytest.mark.integration
def test_text_classifier_param_selector(results_base_path, tasks_base_path):
    corpus = NLPTaskDataFetcher.fetch_data(NLPTask.IMDB, base_path=tasks_base_path)

    glove_embedding: WordEmbeddings = WordEmbeddings('en-glove')

    search_space = SearchSpace()

    # document embeddings parameter
    search_space.add(Parameter.EMBEDDINGS, hp.choice, options=[[glove_embedding]])
    search_space.add(Parameter.HIDDEN_SIZE, hp.choice, options=[64, 128, 256, 512])
    search_space.add(Parameter.RNN_LAYERS, hp.choice, options=[1, 2])
    search_space.add(Parameter.REPROJECT_WORDS, hp.choice, options=[True, False])
    search_space.add(Parameter.REPROJECT_WORD_DIMENSION, hp.choice, options=[64, 128, 256, 512])
    search_space.add(Parameter.BIDIRECTIONAL, hp.choice, options=[True, False])
    search_space.add(Parameter.DROPOUT, hp.uniform, low=0.25, high=0.75)
    search_space.add(Parameter.WORD_DROPOUT, hp.uniform, low=0.25, high=0.75)
    search_space.add(Parameter.LOCKED_DROPOUT, hp.uniform, low=0.25, high=0.75)

    # training parameter
    search_space.add(Parameter.LEARNING_RATE, hp.uniform, low=0, high=1)
    search_space.add(Parameter.MINI_BATCH_SIZE, hp.choice, options=[4, 8, 16, 32])
    search_space.add(Parameter.ANNEAL_FACTOR, hp.uniform, low=0, high=0.75)
    search_space.add(Parameter.PATIENCE, hp.choice, options=[3, 5])

    param_selector = TextClassifierParamSelector(
        corpus, False, str(results_base_path), document_embedding_type='lstm', max_epochs=2)
    param_selector.optimize(search_space, max_evals=2)

    # clean up results directory
    shutil.rmtree(results_base_path)

# Theoretical foundations

The main idea was to use unsupervised approach to create text segments out of a given input text.

Given an input text document T, and the desired number of segments being k. 
We are to segment the document into k semantically homogeneous segments or parts. The steps are as follows-

a)	Convert the words of the text document, T into embedding vectors using Stanford’s GloVe model (pre-trained, 6B tokens, 400k Vocab and 100Dimensional vectors) [https://www.kaggle.com/anindya2906/glove6b] 

b)	Consider the word sequences S, for all the word sequences in the text document T, the average meaning or the centroid of S is calculated by taking the average embeddings of all the words in S.

c)	The error or the cost function for a given sequence is calculated by the average weighted distance between the centroid and all the words in S.

d)	Then, the segmentation is done by using the greedy heuristic approach by iteratively choosing the best split points or segment boundaries.


### References

1. Hearst M. A. Multi-paragraph segmentation of expository text //arXiv preprint cmp-lg/9406037. – 1994.
2. Devlin, Jacob, et al. "Bert: Pre-training of deep bidirectional transformers for language understanding." arXiv preprint arXiv:1810.04805 (2018)

# Requirements

 - Python 3.7 or 3.8. 
 - 8GB of RAM to run
 
### Installation

- Upgrade the PIP version 
`python -m pip install --upgrade pip`

 - First, install pytorch library [here](https://download.pytorch.org/whl/torch_stable.html) (see pytorch.org for platform specific instructions)
 
 - Install requirements list
 `pip install -r requirements.txt`
 
### Pre-trained Word Embedding

Download the English model in Spacy by typing in the command line,

`python -m spacy download en_core_web_md`

# Usage

### Segmentation

from command line terminal run:

`python segment_generator.py <input filename> <output filename>`

### Title Generation

to generate titles 

`python headline_generator.py <file_after_segmentation> <final_result_file_name>`

# Runtime notes

Ignore error message "You should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference, because it is misleading" - T5 is already trained on summarization task. See T5 paper for details

### Possible improvements:

The possible ways the current system of segmentation can be improved are as follows-
1. Using custom Word2Vec model

    In this current approach, due to unavailability of input text data, we have used a pre-trained word embedding model (Stanford’s GloVe model). Such models, though trained on large corpus of data lack case-specificity. That is, they do not have the context of the input text and thus sometimes are not able to represent the text synonymously. 
If the input text is large, it is possible to train a custom Word2Vec model (an embedding layer) using that text corpus only and improve upon the performance.

2. Using annotated data:

    Without annotated data, this problem of text segmentation basically translates to an Unsupervised Clustering problem. With annotated data, this problem shifts towards Topic Modelling and finding Topic-Word distribution which can then be solved using techniques like LDA, LSA and others.

3. Using Transformers:

    With the recent developments in NLP space, Transformers are widely popular. Pre-trained Transformer-based models like BERT can be used for tokenization and other NLP tasks. Using such advanced models might improve the performance of text segmentation as well.
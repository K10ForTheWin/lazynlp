import os
import random
import statistics
import time

from pybloom import BloomFilter

from lazynlp.cleaner import *
from lazynlp.utils import *

def build_ngram_from_tokens(tokens, n):
    """ Create a dictionary of n-gram from the list of tokens
    """
    count = {}
    ngrams=list(zip(x, x[1:]))
    for ng in ngrams:
        count[ng]=count.get(ng,0) +1

    return count

def build_ngram(file, outfile=None, bf=None, gran='word', n=10, uncase=True, alphanumeric=True, interval=100000):
    """
    gran: granularity of the token. It can be 'word' or 'char'
    bf: BloomFilter to update the existence of n-grams. Use when the file is too large to store a dictionary count
    alphanumeric: whether to keep only alphanumeric characters and space.
    outfile: if outfile is specified, build dictionary of n-grams and write it to outfile
    interval: how often to report the progress.
    """
    if not gran in set(['word', 'char']):
        raise ValueError("gran has to be 'word' or 'char'")
    count = {}
  
    i = 1

    start = time.time()
    
    with open(file, 'r') as f:
        lines=f.readlines()
        for line in lines:
                    line = line.strip()
                    if line and uncase:
                            line = line.lower()

                        if gran == 'word'and alphanumeric:
                                line = remove_non_alphanumeric(line)
                        else:
                            line = remove_non_alpha(line)
                        line = collapse_white_spaces(line)
                        tokens = line.split()
                        line_count = build_ngram_from_tokens(tokens, n)

                        if outfile:
                            count.update()

                        if not bf is None:
                            for key in line_count:
                                bf.add(key)

                        if interval > 0 and i % interval == 0:
                            print('Process line: {}. Time: {}'.format(i, time.time() - start))
                            start = time.time()

                        i += 1
        
  
    if outfile:
        outfold = outfile[:outfile.rfind('/')]
        os.makedirs(outfold, exist_ok=True)
        dict_sorted_2_file(count, os.path.join(outfile.format(n)))

    if bf:
        return bf

    return count

def build_word_ngram(file, outfile, n=10, alphanumeric=True, norm=True, interval=100000):
    """ Build word ngrams and store in outfile
    n-grams in the format:
    [n-gram][tab][count]

    If alphanumeric, exclude all the words that contain non-alphanumeric characters
    """
    return build_ngram(file, outfile=outfile, n=n, gran='word', alphanumeric=alphanumeric, norm=norm, interval=interval)

def build_char_ngram(file, outfile, n=10, interval=100000):
    """
    Build character n-grams and store in outfile
    """
    return build_ngram(file, outfile=outfile, n=n, gran='char', interval=interval)

def estimate_overlap(source_files, target_files, gran='word', n=8, capacity=10000, error_rate=1e-5, header=0, interval=100000):
    """ Estimate overlapping of target_files with source_files using n-grams
    gran: granularity of the token. It can be 'word' or 'char'
    header: number of lines of each file to skip. It's because in our format, the first line is the url
    """
    if not gran in set(['word', 'char']):
        raise ValueError("gran has to be 'word' or 'char'")
    if isinstance(source_files, str):
        source_files = [source_files]
    if isinstance(target_files, str):
        target_files = [target_files]
    
    bf = BloomFilter(capacity=capacity, error_rate=error_rate)
    for source_file in source_files:
        bf = build_ngram(file=source_file, bf=bf, gran=gran, n=n, uncase=True, alphanumeric=True, interval=interval)

    results = []
    for file in target_files:
        print(file)
        results.append(estimate_overlap_bf(bf, file, gran=gran, n=8, header=header))
    return results

def estimate_overlap_bf(bf, target_file, gran='word', n=8, header=0):
    """ Estimate overlapping of target_file with an existing bloomfilter
    gran: granularity of the token. It can be 'word' or 'char'
    """
    if not gran in set(['word', 'char']):
        raise ValueError("gran has to be 'word' or 'char'")
        
    f = open(target_file, 'r')
    for _ in range(header + 1):
        line = f.readline()

    total, seen = 0, 0
    
    
    while line:
        line = line.strip().lower()
        
        if gran == 'word':
            line = remove_non_alphanumeric(line)
        else:
            line = remove_non_alpha(line)
        line = collapse_white_spaces(line)
        tokens = line.split()
        line_count = build_ngram_from_tokens(tokens, n)
        
        total = len(k for k in line_count)
        seen = len(k for k in line_count if k in bf)


        line = f.readline()
    
    result = seen / total
    print('{} seen out of {}: {}'.format(seen, total, result))
    return result

def file_stats(file):
    """ Return statistics about line lengths and average character per words
    """
    line_lengths, token_lengths = [], []
    with open(file, 'r') as f:
        for line in file.readlines():
            tokens = line.split()
            line_lengths.append(len(tokens))
            line_token_lengths = [len(token) for token in tokens]
            token_lengths.append([len(tokens), sum(line_token_lengths) / len(tokens)])
 
    
    total_tokens = sum([pair[0] for pair in token_lengths])
    total_chars = sum([pair[0] * pair[1] for pair in token_lengths])
    average_chars = total_chars / total_tokens
    print("Character per word: average = {}.".format(average_chars))

    report = "Word count per line: average = {}, median = {}, max = {}, min = {}, stddev = {}."
    print(report.format(statistics.mean(line_lengths), statistics.median(line_lengths), 
                        max(line_lengths), min(line_lengths),
                        statistics.stdev(line_lengths)))
    return statistics.mean(line_lengths), average_chars

def estimate_entropy(file, gran='word', max_n=10):
    pass


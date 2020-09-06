import numpy as np
import re

sws = set([
    'ourselves', 'should', 'often', 'does', 'this', 'beside', 'well',
    'among', 'throughout', 'being', 'become', 'yourselves', 'namely',
    'whom', 'nothing', 'thus', 'many', '’re', 'had', 'somewhere', 'made',
    'still', "'re", 'eight', 'of', 'yours', 'further', 'again', 'by',
    'anyhow', 'whenever', 'both', 'first', 'third', 'whither', 'all',
    'whether', 'amount', 'afterwards', 'alone', 'she', 'where', 'seemed',
    'something', 'mine', 'whatever', 'most', 'doing', 'behind',
    'thereupon', 'whole', 'hers', 'ca', 'a', 'before', 'forty', '’d',
    '‘s', 'three', 'anything', 'via', 'hereafter', 'him', 'as', 'those',
    'here', 'around', '’ve', 'much', 'some', 'whereas', 'several', 'has',
    'done', 'besides', 'am', 'hereby', '‘d', 'yet', 'make', 'none',
    'while', 'just', 'towards', 'sometimes', 'his', 'into', 'various',
    'their', 'thence', 'so', 'either', 'about', 'once', 'onto', 'thru',
    "'m", 'one', 'seems', 'between', 'say', 'mostly', 'otherwise',
    'herself', 'might', 'and', 'least', 'did', 'hence', 'any', 'do',
    'each', 'whereupon', 'becoming', 'thereby', "'ll", 'two', 'yourself',
    'these', 'through', 'four', "'s", 'last', 'on', 'along', 'could',
    "n't", 'front', 'not', 'quite', '’m', 'at', 'he', 'ten', 'very',
    'himself', 'although', 'now', 'it', 'move', 'bottom', 'within',
    'can', 'sometime', 'out', 'elsewhere', 'empty', 'such', 'after',
    'seeming', 'put', 'us', 'upon', 'please', 'used', 'except', 'n‘t',
    'ours', 'six', 'though', 'without', 'why', 'however', 'above',
    'herein', 'else', 'them', 'formerly', 'since', 'take', 'beyond',
    'whence', 'n’t', 'been', 'nor', 'wherever', 'everywhere', 'hundred',
    'but', 'latterly', 'really', 'is', 'with', 'hereupon', 'we',
    'someone', 'whereby', 'in', 'because', 'latter', 'eleven', 'serious',
    'twenty', 'name', 'may', 'itself', 'to', 'there', "'ve", 'whereafter',
    'ever', 'perhaps', 'everyone', 'sixty', 'seem', 'which', 'almost',
    'anywhere', 'the', 'wherein', 'its', 'cannot', 'keep', 'twelve',
    'moreover', 'they', 'more', 'regarding', 'next', 'you', 'your',
    'own', 'enough', 'side', 're', 'neither', 'have', 'during', 'under',
    'will', 'would', 'over', 'therein', 'became', 'beforehand', 'using',
    'part', 'my', 'that', 'themselves', '’ll', 'myself', 'somehow',
    'together', 'top', 'from', 'then', 'are', 'give', 'back', 'less',
    'always', 'never', 'becomes', 'until', "'d", 'go', 'i', 'whose',
    'below', 'former', 'our', 'be', 'even', 'due', 'fifteen', 'every',
    'than', 'rather', 'how', 'an', 'across', '‘ve', 'another', 'must',
    'noone', 'against', '’s', 'others', 'per', 'already', 'off', 'too',
    'was', 'when', 'also', 'other', 'therefore', 'see', 'up', 'indeed',
    'what', '‘re', 'down', 'nobody', 'everything', 'whoever', 'five',
    'me', 'nevertheless', 'toward', 'same', 'meanwhile', 'call', 'if',
    'anyone', 'or', 'nowhere', 'were', 'unless', 'get', 'nine', 'her',
    'for', '‘ll', 'who', 'fifty', 'few', 'only', 'anyway', 'no',
    'amongst', 'show', '‘m', 'full', 'thereafter'
    ])


def levenshtein_ratio(s, t):
    """ levenshtein_ratio_and_distance:
        Calculates levenshtein distance between two strings.
        If ratio_calc = True, the function computes the
        levenshtein distance ratio of similarity between two strings
        For all i and j, distance[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
        original code from:
        https://www.datacamp.com/community/tutorials/fuzzy-string-python
    """
    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows, cols), dtype=int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1, cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0    # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                cost = 2

            distance[row][col] = min(
                distance[row-1][col] + 1,       # Cost of deletions
                distance[row][col-1] + 1,       # Cost of insertions
                distance[row-1][col-1] + cost)   # Cost of substitutions

    # Computation of the Levenshtein Distance Ratio
    Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
    return Ratio


def process_fosname(string):
    """Function to normalize FOS names """
    good_chars = "abcdefghijklmnoprstuvwxyz0123456789 "
    string = string.lower()
    string = string.replace("-", " ")
    string = "".join(i for i in string if i in good_chars)
    string = string.replace("  ", " ")
    if string[-1] == " ":
        string = string[:-1]
    if string[0] == " ":
        string = string[1:]
    return string


def sdg_label_sort(sdg_label):
    try:
        sdg_nr = int(re.findall(r'\d+', sdg_label)[0])
    except IndexError:
        sdg_nr = sdg_label
    return sdg_nr

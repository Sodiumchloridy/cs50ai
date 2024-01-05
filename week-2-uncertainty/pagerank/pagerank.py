import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    distribution = {}

    if corpus[page]:            
        for link in corpus:
            distribution[link] = (1 - damping_factor) / len(corpus)

        for link in corpus[page]:
            distribution[link] += damping_factor / len(corpus[page])

    # Page has no outgoing links
    else:
        for link in corpus:
            distribution[link] = 1 / len(corpus)
    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_visits = { page : 0  for page in corpus }
    sample = None

    # First sample
    sample = random.choice(list(page_visits))
    page_visits[sample] += 1

    # Sample N-1
    for i in range(0, n-1):
        model = transition_model(corpus, sample, damping_factor)
        dist_weights = [model[i] for i in model]
        sample = random.choices(list(model.keys()), dist_weights, k=1)[0]
        page_visits[sample] += 1

    # Probability divide by N
    for key in page_visits:
        page_visits[key] /= n

    return page_visits


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = {}
    N = len(corpus)
    threshold = 0.0005
    count_threshold = 0

    for key in corpus:
        pagerank[key] = 1 / N

    while count_threshold <= N:
        for key in corpus:
            new = (1 - damping_factor) / N
            alpha = 0
            for page in corpus:
                if key in corpus[page]:
                    num_links = len(corpus[page])
                    alpha = alpha + pagerank[page] / num_links
            alpha = damping_factor * alpha
            new += alpha
            if abs(pagerank[key] - new) < threshold:
                count_threshold += 1
            pagerank[key] = new 
    return pagerank

if __name__ == "__main__":
    main()

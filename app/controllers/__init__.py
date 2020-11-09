import sys


def log(*vargs, **kwargs):
    print(file=sys.stderr, *vargs, **kwargs)

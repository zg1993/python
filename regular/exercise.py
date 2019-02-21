# encoding: utf8


import re
import sys

# 1. Write a Python program to check that a string contains only a certain set of characters (in this case a-z, A-Z and 0-9).
def fun1(string):
    pattern = re.compile(r'[\W_]+')
    return False if pattern.search(string) else True

def fun1_advantage(string):
    pattern = re.compile(r'[\W_]')
    return not bool(pattern.search(string))




if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: ", sys.argv[0], " str"
        exit()
    string = sys.argv[1]
    print string
    print fun1(string)


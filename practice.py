# coding: utf8

import random
from itertools import izip_longest
import sys

print sys.argv


def insert_sorted(array):
    for index, i in enumerate(array[1:], 1):
        for j in range(index):
            if i < array[j]:
                array[j], i = i, array[j]
        array[index] = i
    print array

    
def insert_sorted_optimization(array):
    for index, i in enumerate(array):
        j = index
        while (j > 0 and i < array[j-1]):
            array[j] = array[j-1] 
            j -= 1
        array[j] = i
    print array

def select_sorted(array):
    length = len(array)
    for index, i in enumerate(array):
        m = array[index]
        start = index
        while (start < length):
            if m > array[start]:
                m, array[start] = array[start], m
            start += 1
        array[index] = m
    print array


def select_sorted_optimization(array):
    for index, i in enumerate(array):
        min_index = index
        for i in range(index, len(array)):
            if array[min_index] > array[i]:
                min_index = i
        array[index], array[min_index] = array[min_index], array[index]
    print array
        

def bubble_sorted(array):
    i = len(array)
    while (i > 0):
        for j in range(i-1):
            if array[j] > array[j+1]:
                array[j], array[j+1] = array[j+1], array[j]
        i -= 1
    print array

def merge_optimization(array1, array2):
    result = []
    for a1, a2 in izip(array1, array2, fillvalue=float('inf')):
        pass
    

def merge(array1, array2):
    i = j = k = 0
    result = []
    while (i < len(array1) and j < len(array2)):
        if (array1[i] < array2[j]):
            result.append(array1[i])
            i += 1
        else:
            result.append(array2[j])
            j += 1
    while (i < len(array1)):
        result.append(array1[i])
        i += 1
    while (j < len(array2)):
        result.append(array2[j])
        j += 1
    return result

def merge_optimize(result, array, leftpos, mid, end):
    base = leftpos
    start = leftpos
    right_start = mid + 1
    while (leftpos <= mid and right_start <= end):
        if array[leftpos] < array[right_start]:
            result[start] = array[leftpos]
            start += 1
            leftpos += 1
        else:
            result[start] = array[right_start]
            start += 1
            right_start += 1
    while (leftpos <= mid):
        result[start] = array[leftpos]
        start += 1
        leftpos += 1
    while (right_start <= end):
        result[start] = array[right_start]
        start += 1
        right_start += 1
    for i in range(base, end+1):
        array[i] = result[i]
        
    
    
def merge_sorted(array, start, end):
    if end > start:
        mid = (start + end) >> 1
        left_array = merge_sorted(array, start, mid)
        right_array = merge_sorted(array, mid+1, end)
        return merge(left_array, right_array)
    return array[start:end+1]

def merge_sorted_optimization(result, array, start, end):
    if end > start:
        mid = (start + end) >> 1
        merge_sorted_optimization(result, array, start, mid)
        merge_sorted_optimization(result, array, mid + 1, end)
        merge_optimize(result, array, start, mid, end)

if __name__ == '__main__':
    
    l = [random.choice(range(20)) for _ in range(10)]

    print l
    insert_sorted(list(l))
    insert_sorted_optimization(list(l))
    select_sorted(list(l))
    select_sorted_optimization(list(l))
    bubble_sorted(list(l))
    result = [0] * len(l)
    print "merge\n", merge_sorted(list(l), 0, len(l) - 1)
    print "merge optimize\n", merge_sorted_optimization(result, l, 0, len(l)-1)
    print result


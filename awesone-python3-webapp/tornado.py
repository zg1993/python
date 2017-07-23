#!/usr/bin/env python
#-*- coding: utf-8-*-

from tornado import gen


@gen.coroutine
def divide(x, y):
	return x / y

def bad_call():
	divide(1, 0)

@gen.coroutine
def good_call():
	yield divide(1, 0)

bad_call()
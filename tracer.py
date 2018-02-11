#!/usr/bin/python3
""" Definitions and implementations of a simple logging / tracing method """
from abc import ABCMeta, abstractmethod

class Tracer(object, metaclass=ABCMeta):
    """ Base class for implementations of a simple logging / tracing method """

    @abstractmethod
    def trace(self, tracestr):
        """ Trace a simple string """

class ConsoleTracer(Tracer):
    """ Implementation of the tracer that traces the strings to the console """

    def trace(self, tracestr):
        print(tracestr)

class NullTracer(Tracer):
    """ Implementation of the tracer that doesn't trace anywhere """

    def trace(self, tracestr):
        pass

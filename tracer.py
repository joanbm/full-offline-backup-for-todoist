from abc import ABCMeta, abstractmethod

class Tracer:
    """ Base class for implementations of a simple logging / tracing method"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def trace(self, str):
        """ Trace a simple string """

class ConsoleTracer(Tracer):
    """ Implementation of the tracer that traces the strings to the console """

    def trace(self, str):
        print(str)

class NullTracer(Tracer):
    """ Implementation of the tracer that doesn't trace anywhere """

    def trace(self, str):
        pass
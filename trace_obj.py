#!/usr/bin/env python3

import pyasmtools


class Complex(metaclass=pyasmtools.TraceClass):
    def __init__(self, re, im=0.0):
        self.real = re
        self.imag = im

    def __add__(self, other):
        return Complex(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return Complex(self.real - other.real, self.imag - other.imag)

    def __mul__(self, other):
        return Complex((self.real * other.real) - (self.imag * other.imag),
            (self.imag * other.real) + (self.real * other.imag))

    def __truediv__(self, other):
        r = (other.real**2 + other.imag**2)
        return Complex((self.real*other.real - self.imag*other.imag)/r,
            (self.imag*other.real + self.real*other.imag)/r)

    def __abs__(self):
        print('\nAbsolute Value:')
        new = (self.real**2 + (self.imag**2)*-1)
        return Complex(sqrt(new.real))

    def __str__(self):
        return f"real: {self.real} imaginary: {self.imag}"

class Person:
    def  __init__(self, first_name, last_name):
        self.first_name  = first_name
        self.last_name = last_name
    def __str__(self):
        return f"first_name: {self.first_name} last_name: {self.last_name}"

class PersonWithTitle(Person, metaclass=pyasmtools.TraceClass):
    def __init__(self, first_name, last_name, title):
        super().__init__(first_name, last_name)
        self.title = title
        #print(f"__init__ id: {id(self)} self.__dict__ {self.__dict__}")


    def __str__(self):
        #print(f"__str__ id: {id(self)} self.__dict__ {self.__dict__}")
        return f"Title: {self.title} {super().__str__()}"

num = Complex(2,3)
print(num)

per = PersonWithTitle("Pooh", "Bear", "Mr")
print(per)
print("eof")

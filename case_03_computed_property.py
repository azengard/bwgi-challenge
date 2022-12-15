from math import sqrt
from unittest import TestCase


class Cache:
    """Custom Property Class with cache"""

    def __init__(self, args, fget, fset=None, fdel=None):
        self.__doc__ = fget.__doc__
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.args = args
        self.result_cache = dict()

    def __get__(self, instance, cls_):
        if self._cache(instance):
            self.result_cache = self.fget(instance)
        return self.result_cache

    def _cache(self, instance):
        changed = False
        for arg in self.args:
            instance_arg = getattr(instance, arg, None)

            if not getattr(self, arg, None):
                setattr(self, arg, instance_arg)
                changed = True

            if not getattr(self, arg) == instance_arg:
                setattr(self, arg, instance_arg)
                changed = True

        return changed

    def __set__(self, attr, value):
        if not self.fset:
            raise AttributeError()
        return self.fset.__get__(attr, type(attr))(value)

    def __delete__(self, attr):
        if not self.fdel:
            raise AttributeError()
        return self.fdel.__get__(attr, type(attr))()

    def setter(self, func):
        self.fset = func
        return self

    def deleter(self, func):
        self.fdel = func
        return self


def computed_property(*args):
    """Transform Cache() on a method decorator"""

    def inner(func):
        return Cache(fget=func, args=args)

    return inner


class Vector:
    """Class used to test decorator"""

    def __init__(self, x, y, z, color=None):
        self.x, self.y, self.z = x, y, z
        self.color = color

    @computed_property('x', 'y', 'z')
    def magnitude(self):
        print('computing magnitude')
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)


class Circle:
    """Class used to test decorator"""

    def __init__(self, radius=1):
        self.radius = radius

    @computed_property('radius', 'invalid_attr')
    def diameter(self):
        """Circle diameter from radius"""
        return self.radius * 2

    @diameter.setter
    def diameter(self, value):
        self.radius = value / 2

    @diameter.deleter
    def diameter(self):
        self.radius = 0


class TestComputedPropertyDecorator(TestCase):
    def test_decorator_cache(self):
        v = Vector(9, 2, 6)

        vec_call_1 = v.magnitude
        self.assertEqual(vec_call_1, 11.0)

        v.color = 'red'
        vec_call_2 = v.magnitude
        self.assertEqual(vec_call_2, 11.0)
        assert vec_call_1 is vec_call_2  # assert computing magnitude not called

        v.y = 18
        vec_call_3 = v.magnitude
        self.assertEqual(vec_call_3, 21.0)
        assert vec_call_2 is not vec_call_3  # assert computing magnitude called

    def test_decorator_just_ignores_invalid_attr(self):
        """circle.diameter just ignores 'invalid_attr' that was declared on method decorator"""
        circle = Circle()
        self.assertEqual(circle.diameter, 2)

    def test_decorator_setter(self):
        circle = Circle()
        self.assertEqual(circle.diameter, 2)

        circle.diameter = 3
        self.assertEqual(circle.radius, 1.5)

    def test_decorator_deleter(self):
        circle = Circle()
        del circle.diameter

        self.assertEqual(circle.radius, 0)

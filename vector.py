#
# vector.py - implementation of two dimensional vector
#
# PygameGame
#     Copyright (C) 2014  Eric Eveleigh
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math

class Vector2D(object):
    def set(self,x=0.0,y=0.0):
        self.x = float(x)
        self.y = float(y)
    def set_vect(self, vector):
        self.x = vector.x
        self.y = vector.y
    def set_tup(self, vector):
        self.set(vector[0], vector[1])
    def get_x(self):
        return self.x
    def set_x(self, x):
        self.x = float(x)
    def get_y(self):
        return self.y
    def set_y(self, y):
        self.y = float(y)
    def get(self):
        return (self.x,self.y)
    def get_int(self):
        return (int(self.x),int(self.y))
    def __init__(self, x=0.0, y=0.0):
        self.x = 0.0
        self.y = 0.0
        self.set(x,y)

    # creates new instance identical to self
    def copy(self):
        return Vector2D(self.x, self.y)
    
    # get the norm (length/magnitude) of self
    def norm(self):
        return math.sqrt(self.norm_squared())
    
    def norm_squared(self):
        return self.x**2 + self.y**2

    # scale self by scalar
    def scale(self, scalar):
        self.x *= scalar
        self.y *= scalar
        return self

    # get new vector = to self*scalar
    def scaled(self, scalar):
        vect = Vector2D(self.x, self.y)
        return vect.scale(scalar)

    # get unit vector in direction of self
    def direction(self):
        norm = self.norm()
        if norm == 0.0:
            return Vector2D(0,0)

        return self.scaled(1.0/self.norm())
        
    # rotate self theta radians
    def rotate(self, theta):
        # trivial optimization: only calculate cos/sin once
        costheta = math.cos(theta)
        sintheta = math.sin(theta)

        x = self.x
        y = self.y
        
        # Rotation matrix:
        # |x'| = |cos(t) -sin(t)||x|
        # |y'| = |sin(t)  cos(t)||y|
        self.x = x*costheta - y*sintheta
        self.y = x*sintheta + y*costheta

        return self
    
    # undo rotation of theta radians
    def rotate_inverse(self, theta):
        return self.rotate(-theta)
        
    # get new vector rotated by theta
    def rotated(self, theta):
        return self.copy().rotate(theta)

    # get new vector with undone rotation
    def unrotated(self, theta):
        return self.copy().rotate_inverse(theta)

    # get scalar product of self dot b
    def dot(self,b):
        return self.x*b.x + self.y*b.y
    
    # third component of selfxb if self and b were 3D vectors
    def cross2(self, b):
        return self.x*b.y - self.y*b.x
    
    @staticmethod
    # third component of vector cross with vect
    def cross3(z, vect):
        x = -z*vect.y
        y = z*vect.x
        return Vector2D(x,y)

    # add b to self
    def add(self, b):
        self.x += b.x
        self.y += b.y
        return self

    # get result of vec addition self+b
    def addition(self,b):
        return self.copy().add(b)

    # reverse direction of self
    def reverse(self):
        self.x = -self.x
        self.y = -self.y
        return self

    # return copy of -self vector 
    def reversed(self):
        vect = self.copy()
        return vect.reverse()

    def perp(self):
        return Vector2D(-self.y, self.x)
        
    # get normal to this vector
    def normal(self):
        return self.perp().direction()

    # find point of intersection, if any,
    # of vectors A and B, given as two position
    # vectors each
    # also returns parameter in the A direction
    @staticmethod
    def intersection(a1, a2, b1, b2):
        # calculate direction of A(1) and B(2)
        d1 = a2.addition(a1.reversed()).direction()
        d2 = b2.addition(b1.reversed()).direction()

        # Since d1 and d2 are dir. vectors, they have length 1.
        # If the d1 dot d2 equals 1 or -1 then they are co-linear
        # -> no intersection POINT if collinear
        dot = d1.dot(d2)
        if dot == 1 or dot == -1:
            return None

        # prevent div by zero
        denom = (d1.y*d2.x - d1.x*d2.y)
        if denom == 0.0:
            return None
        
        # c = a1 - b1
        c = a1.addition(b1.reversed())

        t1 = (c.x*d2.y - c.y*d2.x)/denom
        point = a1.addition(d1.scaled(t1))

        if a2.x > a1.x:
            if point.x < a1.x or point.x > a2.x:
                return None
        else:
            if point.x < a2.x or point.x > a1.x:
                return None

        if a2.y > a1.y:
            if point.y < a1.y or point.y > a2.y:
                return None
        else:
            if point.y < a2.y or point.y > a1.y:
                return None

        if b2.x > b1.x:
            if point.x < b1.x or point.x > b2.x:
                return None
        else:
            if point.x < b2.x or point.x > b1.x:
                return None

        if b2.y > b1.y:
            if point.y < b1.y or point.y > b2.y:
                return None
        else:
            if point.y < b2.y or point.y > b1.y:
                return None

        return point, t1

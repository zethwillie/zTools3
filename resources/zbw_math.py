import maya.cmds as cmds
import maya.OpenMaya as om
import math


# trig stuff - use math


# vector stuff
def length(vec=(0,0,0),*args):
    """
    finds the length of the vector
    """
    v = om.MVector(vec[0], vec[1], vec[2])
    length = v.length()

    return length

def normalizeVector(vec=(0,0,0), *args):
    """
    normalizes the given array3
    """
    normalVec = om.MVector(vec[0], vec[1], vec[2]).normal()

    return (normalVec[0], normalVec[1], normalVec[2])

def dot(vecA = [1,2,3], vecB = [4,5,6], *args):
    """
    returns the dot product of two vecs
    """
    A = om.MVector(vecA[0], vecA[1], vecA[2])
    B = om.MVector(vecB[0], vecB[1], vecB[2])

    dot = A*B

    return dot

def dotN(vecA = [1,2,3], vecB = [4,5,6], *args):
    """
    returns the normalized dot product (projection of first onto second from 0-1)
    """
    normA = normalizeVector(vecA)
    normB = normalizeVector(vecB)

    dotNorm = dotProduct(normA, normB)

    return dotNorm

def angleBetween(vecA, vecB, *args):
    """
    finds the angle between two vectors (in degrees)
    """
    d = dotN(vecA, vecB)

    rads = math.acos(d)
    degrees = rads*(180/math.pi)

    return degrees

# matrix stuff

"""
Keywords:
- RTSP: Real-Time Streaming Protocol

References:
- ZR10 website: https://shop.siyi.biz/products/siyi-zr10
- ZR10 mannual: https://www.premium-modellbau.de/media/pdf/74/b6/f9/ZR10_User_Manual_en_v1-0.pdf
- Computes CRC16 Ref: https://gist.github.com/oysstu/68072c44c02879a2abf94ef350d1c7c6?permalink_comment_id=3943460#gistcomment-3943460

Required:
- OpenCV
    (sudo apt-get install python3-opencv -y)
- imutils
    (pip install imutils)

"""


# Importing of the neccessary packages
import os                                          # Required Function : stat
import time                                        # Required Function : time, sleep
import cv2 
from imutils.video import VideoStream
import socket
import logging
import subprocess
import threading
import unittest                                    # Required Function : TestCase


# Basic Functionalities to convert int->hex and vice-versa
def toHexVal(intValue:int, 
             nbits:int)->str:
    """
    Converts an integer to hexadecimal.

    This function takes an integer value and the number of bits as input and converts the integer to its hexadecimal representation.
    It first calculates the maximum value that can be represented with the given number of bits using bitwise left shift.
    Then it validates the input value and converts any negative numbers to positive using a formula.
    After that, it formats the validated value to its hexadecimal representation using the 'x' format specifier.
    Finally, it ensures the consistency in the format of the hexadecimal representation by adding a leading zero if necessary.
    Ref: https://www.geeksforgeeks.org/python-hex-function

    Params
    ---
    intValue [int] : Integer number
    nbits [int] : Number of bits

    Returns
    ---
    [str] String of the Hexadecimal Value
    """
    max_nbits_value = 1<<nbits
    validateVal = (intValue + max_nbits_value)%max_nbits_value      # Useful to convert negative numbers to positive
    hexValue = format(validateVal, 'x')
    return hexValue.zfill((nbits + 3) // 4)                         # Ensures consistency in the format of the hexadecimal representation

def toIntVal(hexValue:str)->int:
    """
    Coverts hexidecimal value to an integer number, which can be negative
    Ref: https://www.delftstack.com/howto/python/python-hex-to-int/#convert-hex-to-signed-integer-in-python

    Params
    --
    hexValue [str] : String of the hexadecimal value

    Returns
    --
    [int] Integer value of the Hexadecimal Value
    """
    bits = 16
    intValue = int(hexValue, bits)
    if intValue & (1 << (bits-1)):                                 # Represents the negative number on the basis of the MSB
        intValue -= 1 << bits
    return intValue



class SIYI:
    """
    SIYI Class
    """
    class SIYI_RTSP:
        """
        Global Variable:
        --
        - rtspUrl
        - cameraName
        - imageWidth
        - imageHeight
        - currentFrame
        - debug
        - logger
        """
        def __init__(self, 
                     rtsp_url:str="", 
                     rtsp_port:str="", 
                     camera_name:str="SIYI ZR10", 
                     debug:bool=False) -> None:
            """
            Receiving the port address of the video straming from SIYI ZR10 Camera and initializing it.

            Params
            --
            - rtsp_url [str] : RTSP url
            - rtsp_port [str] : RTSP port
            - camera_name [str] : Name of the camera
            - debug [bool] : Printing debug messages
            """
            pass
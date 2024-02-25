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
def toHexVal(intValue: int, 
             nbits: int=16) -> str:
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
    - intValue [int] : Integer number
    - nbits [int] : Number of bits

    Returns
    ---
    [str] String of the Hexadecimal Value
    """
    max_nbits_value = 1<<nbits
    validateVal = (intValue + max_nbits_value)%max_nbits_value      # Useful to convert negative numbers to positive
    hexValue = format(validateVal, 'x')
    return hexValue.zfill((nbits + 3) // 4)                         # Ensures consistency in the format of the hexadecimal representation

def toIntVal(hexValue: str) -> int:
    """
    Coverts hexidecimal value to an integer number, which can be negative
    Ref: https://www.delftstack.com/howto/python/python-hex-to-int/#convert-hex-to-signed-integer-in-python

    Params
    ---
    - hexValue [str] : String of the hexadecimal value

    Returns
    ---
    [int] Integer value of the Hexadecimal Value
    """
    bits = 16
    intValue: int = int(hexValue, bits)
    if intValue & (1 << (bits-1)):                                 # Represents the negative number on the basis of the MSB
        intValue -= 1 << bits
    return intValue



class SIYI:
    """
    SIYI Class
    """
    class SIYI_RTSP:
        """
        Global Variables:
        ---
        - rtsp_url [str]: RTSP URL
        - camera_name [str]: Name of the camera
        - image_width [int]: Image width
        - image_height [int]: Image height
        - current_frame [Any]: Current Stored frame
        - debug [bool]: Printing debug messages
        - logger [Logger]: Logger
        - stopped [bool]: Stopped flag
        - show_window [bool]: Show window
        - last_image_time [float]: Last image time
        - connection_timeout [float]: Connection timeout
        - recv_thread [Thread]: Receive thread frame
        - stream_video [VideoStream]: Video stream
        """
        def __init__(self, 
                    rtsp_url: str = "rtsp://192.168.144.25:{port}/main.264", 
                    rtsp_port: str = "8554", 
                    camera_name: str = "SIYI ZR10", 
                    debug: bool = False) -> None:
            """
            Receiving the port address of the video streaming from SIYI ZR10 Camera and initializing it.

            Params
            ---
            - rtsp_url [str]: RTSP URL
            - rtsp_port [str]: RTSP port
            - camera_name [str]: Name of the camera
            - debug [bool]: Printing debug messages

            Returns
            ---
            None
            """

            # Setting the RTSP URL address
            self.rtsp_url: str = rtsp_url.format(port=rtsp_port)

            # Name of the Camera
            self.camera_name: str = camera_name

            # Image width and height
            self.image_width: int = 1200
            self.image_height: int = 700

            # Currently Stored frame
            self.current_frame: any = None

            # Debug Mode
            self.debug: bool = debug
            debug_level = logging.DEBUG if self.debug else logging.INFO
            log_format = '[%(levelname)s] %(asctime)s [SIYI::%(funcName)s] :\t%(message)s'
            logging.basicConfig(format=log_format, level=debug_level)
            self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

            # Flag to stop streaming loop
            self.stopped: bool = False

            # Show graphical window with frames or not
            self.show_window: bool = False
            self.last_image_time: float = time.time()

            # Connection Timeout in seconds
            self.connection_timeout: float = 10.0

            # Receiving Thread Handler
            self.recv_thread: threading.Thread = threading.Thread(target=self.recv_thread_loop)

            # Start Receiving Thread and Streaming
            self.start_connection()

        def __str__(self) -> str:
            """
            Returns a string representation of the object, including details such as 
            camera name, RTSP URL, image width, image height, current frame, debug mode, 
            stopped status, show window status, last image time, and connection timeout.
            """
            attributes = [
            f"Camera Name: {self.camera_name}",
            f"RTSP URL: {self.rtsp_url}",
            f"Image Width: {self.image_width}",
            f"Image Height: {self.image_height}",
            f"Current Frame: {self.current_frame}",
            f"Debug Mode: {'Enabled' if self.debug else 'Disabled'}",
            f"Stopped: {'Yes' if self.stopped else 'No'}",
            f"Show Window: {'Yes' if self.show_window else 'No'}",
            f"Last Image Time: {self.last_image_time}",
            f"Connection Timeout: {self.connection_timeout} seconds"
            ]
            return "\n".join(attributes)
        
        @property
        def image_width(self) -> int:
            """
            Getter for the image_width property.

            Returns
            ---
            int: The value of image_width.
            """
            return self.image_width
        
        @image_width.setter
        def image_width(self, new_val: int) -> None:
            """
            Setter for the image_width property.

            Params
            ---
            - new_val [int]: The value to set for image_width.

            Returns
            ---
            None
            """
            self.image_width = new_val

        @property
        def image_height(self) -> int:
            """
            Getter for the image_height property.

            Returns
            ---
            int: The value of image_height.
            """
            return self.image_height
        
        @image_height.setter
        def image_height(self, new_val: int) -> None:
            """
            Setter for the image_height property.

            Params
            ---
            - new_val [int]: The value to set for image_height.

            Returns
            ---
            None
            """
            self.image_height = new_val

        @property
        def debug(self) -> bool:
            """
            Getter for the debug property.

            Returns
            ---
            bool: The value of debug.
            """
            return self.debug
        
        @debug.setter
        def debug(self, new_val: bool) -> None:
            """
            Setter for the debug property.

            Params
            ---
            - new_val [bool]: The value to set for debug.

            Returns
            ---
            None
            """
            self.debug = new_val

        @property
        def show_window(self) -> bool:
            """
            Getter for the show_window property.

            Returns
            ---
            bool: The value of show_window.
            """
            return self.show_window
        
        @show_window.setter
        def show_window(self, new_val: bool) -> None:
            """
            Setter for the show_window property.

            Params
            ---
            - new_val [bool]: The value to set for show_window.

            Returns
            ---
            None
            """
            self.show_window = new_val
        
        def set_show_window(self, new_val: bool) -> None:
            """
            Setter for the show_window property.

            Params
            ---
            - new_val [bool]: The value to set for show_window.

            Returns
            ---
            None
            """
            self.show_window = new_val

        @property
        def stopped(self) -> bool:
            """
            Getter for the stopped property.

            Returns
            ---
            bool: The value of stopped.
            """
            return self.stopped
        
        @stopped.setter
        def stopped(self, new_val: bool) -> None:
            """
            Setter for the stopped property.

            Params
            ---
            - new_val [bool]: The value to set for stopped.

            Returns
            ---
            None
            """
            self.stopped = new_val

        @property
        def connection_timeout(self) -> float:
            """
            Getter for the connection_timeout property.

            Returns
            ---
            float: The value of connection_timeout.
            """
            return self.connection_timeout
        
        @connection_timeout.setter
        def connection_timeout(self, new_val: float) -> None:
            """
            Setter for the connection_timeout property.

            Params
            ---
            - new_val [float]: The value to set for connection_timeout.

            Returns
            ---
            None
            """
            self.connection_timeout = new_val

        def get_current_frame(self) -> any:
            """
            Gets the Current stored frame.

            Returns
            ---
            Any: The value of current_frame.
            """
            if self.current_frame is None:
                return None
            return self.current_frame

        def start_connection(self) -> None:
            """
            Start receiving thread and connect to the SIYI ZR10 Camera Streaming Server.
            """
            try:
                self.logger.info("Welcome to %s.\nConnecting to %s...", self.camera_name, self.rtsp_url)
                self.stream_video: VideoStream = VideoStream(self.rtsp_url).start()
                self.recv_thread.start()

            except ConnectionError as conn_err:
                # Handle connection error gracefully, such as retrying or logging and continuing with the program.
                self.logger.error("Could not establish connection to %s. Error: %s", self.cameraName, conn_err)
                exit(1)

            except FileNotFoundError as file_err:
                # Handle file not found error appropriately.
                self.logger.error("Could not find file: %s", file_err.filename)
                exit(1)

            except Exception as other_err:
                # Handle other exceptions as needed.
                self.logger.error("An error occurred while connecting to %s. Error: %s", self.cameraName, other_err)
                exit(1)

        def recv_thread_loop(self) -> None:
            """
            A function to continuously receive frames from a video stream and perform various operations on the frames.
            """
            self.last_image_time = time.time()
            while not self.stopped:
                self.logger.debug("Reading frame from %s ...", self.camera_name)
                self.current_frame = self.stream_video.read()

                current_image_time: float = time.time()
                if current_image_time - self.last_image_time > self.connection_timeout:
                    self.logger.warning("Connection timeout. Exiting...")
                    self.close_connection()
                    break
                
                if self.current_frame is None:
                    continue

                self.last_image_time = current_image_time

                if self.show_window:
                    cv2.imshow('{} Stream'.format(self.camera_name), self.current_frame)
                    
                    key = cv2.waitKey(25) & 0xFF

                    if key == ord('q'):
                        self.close_connection()
                        break

            self.logger.warning("RTSP receiving loop is done...")
            return
            
        def close_connection(self) -> None:
            """
            Closes the connection and stops the video stream.
            """
            self.logger.info("Closing stream of %s...", self.camera_name)
            self.logger.info("Disconnecting %s ...", self.rtsp_url)
            cv2.destroyAllWindows()
            self.stream_video.stop()
            self.stopped = True



    class RTMP_Sender:
        """
        
        """
        pass
import cv2
import numpy as np


# Given a valid cv2 image, return its grayscale version
def grayscale(image):
    """
    Given an OpenCV compatible image, return that image converted to grayscale
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# Add a border of the specified size to the image and return the image with that border
def add_border(image, border_size: list[int]):
    """
    Adds a border of the specified size to the image and return the image with that border

    Args:
        image: the OpenCV compatible image to add the border to
        border_size: a list of 4 integers representing how much border to add to the top, bottom,
        left, and right of the image.

    Returns: the original image with the added border
    """
    color = [209, 209, 209]  # the color of the border
    top, bottom, left, right = border_size
    return cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)


# Thicken the text in the image. To leave the font changed in height or width, use 1.
def thicken_font(image, height, width):
    """
    Thickens the font of the text in the image based on the specified parameters

    Args:
        image: the OpenCV compatible image to use as a base
        height: how much to expand the font vertically
        width: how much to expand the font horizontally 

    Returns:
        The parameter image with its text thickened
    """
    image = cv2.bitwise_not(image)
    kernel = np.ones((height, width),np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.bitwise_not(image)
    return image


def dilate(image, horizontal_param=1, vertical_param=1):
    """
    Dilate the text of the image based on the given parameters

    Args:
        image: the OpenCV compatible image to apply the dilation
        horizontal_param: How much to dilate the text horizontally. A large number will
        stretch the text horizontally
        vertical_param: How much to dilate the text vertically. A large number will
        stretch the text vertically

    Returns:
        A new image dilated based on the given parameters
    """
    # START OF MINE
    gray = grayscale(image)

    # thicken font horizontally to ensure that rows/lines are extracted from the receipt
    gray = thicken_font(gray, 1, 100)

    # Performing OTSU threshold
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_param, vertical_param))

    # Applying dilation on the threshold image to get rough outline of bounding boxes
    dilation = cv2.dilate(thresh, kernel, iterations=1)
    return dilation


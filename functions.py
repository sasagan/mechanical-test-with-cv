import cv2
import numpy as np

def create_mask(source_img):
    hsv = cv2.cvtColor(source_img, cv2.COLOR_BGR2HSV)

    hsv_min = np.array((68 , 89 , 40), np.uint8)
    hsv_max = np.array((77, 255, 255), np.uint8)

    thresh = cv2.inRange(hsv, hsv_min, hsv_max)

    mask_refined = cv2.medianBlur(thresh, 5)

    # 2. Морфологические операции
    kernel = np.ones((5, 5), np.uint8)
    # Удаляем мелкий мусор
    mask_refined = cv2.morphologyEx(mask_refined, cv2.MORPH_OPEN, kernel, iterations=1)
    # Склеиваем части объекта воедино
    mask_refined = cv2.morphologyEx(mask_refined, cv2.MORPH_CLOSE, kernel, iterations=15)

    mask_refined_inverted = cv2.bitwise_not(mask_refined)

    contours, _ = cv2.findContours(mask_refined_inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    final_mask = np.zeros_like(mask_refined_inverted)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(final_mask, [largest_contour], -1, 255, thickness=cv2.FILLED)
    return final_mask
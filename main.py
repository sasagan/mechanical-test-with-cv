from matplotlib import pyplot as plt
import cv2
import numpy as np

from classes import Point 
from functions import create_mask

cv2.namedWindow("video", cv2.WINDOW_NORMAL) 

video_path = '/home/alex/Видео/data5min3var.mp4'
cap = cv2.VideoCapture(video_path)

video_writer = cv2.VideoWriter('out_video.mp4', 
                               cv2.VideoWriter_fourcc(*'mp4v'), 
                               cap.get(cv2.CAP_PROP_FPS),
                               (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

hsv_min = np.array((0 , 0 , 52), np.uint8)
hsv_max = np.array((255, 78, 255), np.uint8)

points = []

axis_sumM = []
axis_points = []

while cap.read()[0]:
    ret , frame = cap.read()
   
    if not ret:
        break
    
    frame_mask = cv2.bitwise_and(frame, frame, mask=create_mask(frame))

    hsv = cv2.cvtColor(frame_mask, cv2.COLOR_BGR2HSV)

    hsv_min = np.array((0 , 0 , 41), np.uint8)
    hsv_max = np.array((255, 255, 255), np.uint8)

    thresh = cv2.inRange(hsv, hsv_min, hsv_max)

    kernel = np.ones((5, 5), np.uint8)
    # Удаляем мелкий мусор
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    thresh[:, 0:920] = 0
    thresh[:, 1020:1920] = 0

    

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    sumM = 0

    points_on_frame = []
    
    for cnt in contours:
        M = cv2.moments(cnt)
        
        if 250 > M['m00'] > 30: 
            # Координаты центра
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            if not points: # елси список всех точек пуст
                if not points_on_frame: # если список точек на текущем кадре пуст
                    points_on_frame += [Point(1, cx, cy)]
                else:
                    points_on_frame += [Point( max(point.id for point in points_on_frame) + 1, cx, cy)]
            else: # если список всех точек НЕ пуст
                flag_point_exist_in_points = 0
                for point_frame in reversed(points): # перебираем точки из последнего элемта списка всех точек
                    for point in point_frame:
                        if np.abs(point.x-cx) < 5 and np.abs(point.y-cy) < 5:
                            points_on_frame += [Point( point.id, cx, cy )]
                            flag_point_exist_in_points = 1
                            break
                    if flag_point_exist_in_points == 1:
                        break
                if flag_point_exist_in_points == 0:
                    max_point = max(point.id for points[1] in points for point in points[1])
                    if max_point < 33:
                        points_on_frame += [Point( max(point.id for points[1] in points for point in points[1]) + 1, cx, cy)]
                        
            sumM +=  M['m00']
    
    for p in points_on_frame:
        cv2.putText(frame, str(p.id), (p.x, p.y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        
    points += [points_on_frame]
    
    axis_sumM += [sumM]
    axis_points += [len(points_on_frame)]
    
    video_writer.write(frame)  #сохраняем новые кадры в видеофайл (не работает)
    
    #cv2.imshow('video', cv2.drawContours(thresh , contours, -1, (0, 255, 0), 2)) 
    cv2.imshow('video', frame) 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

axis_frame = [i for i in range(0, len(axis_sumM))]
plt.subplot(2,1,1)
plt.plot(axis_frame, axis_sumM)
plt.subplot(2,1,2)
plt.plot(axis_frame, axis_points)
cap.release()
cv2.waitKey(0)
cv2.destroyAllWindows()

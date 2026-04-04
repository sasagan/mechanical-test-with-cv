from matplotlib import pyplot as plt
import cv2
import numpy as np
from scipy.spatial.distance import cdist
from math import sqrt

from classes import Point, Line
from functions import create_mask, get_color_line

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

while True:
    ret , frame = cap.read()
   
    if not ret:
        break
    
    if len(points) > 10:
        del points[0]

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

    points_on_frame = {}
    
    # находим точки и присваиваем им индивидуальный id
    for cnt in contours:
        M = cv2.moments(cnt)
        
        if 250 > M['m00'] > 10: 
            # Координаты центра
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            if not points: # елси список всех точек пуст
                if not points_on_frame: # если список точек на текущем кадре пуст
                    points_on_frame[1] = Point(1, cx, cy)
                else:
                    points_on_frame[max(points_on_frame)+1] = Point( max(points_on_frame)+1, cx, cy) 
            else: # если список всех точек НЕ пуст
                flag_point_exist_in_points = 0

                for point_frame in reversed(points):
                    if flag_point_exist_in_points == 1:
                        break
                    for key_point in point_frame:
                        if np.abs(point_frame[key_point].x-cx) < 5 and np.abs(point_frame[key_point].y-cy) < 5:
                            points_on_frame[key_point] = Point( key_point, cx, cy )
                            flag_point_exist_in_points = 1
                            break

                if flag_point_exist_in_points == 0:
                    if len(points[1]) < 33:
                        points_on_frame += [Point( max(points[1]) + 1, cx, cy)]
                        
    if points:
        if len(points[len(points)-1]) != len(points_on_frame):
            print('min points')
            for key_point in reversed(points[len(points)-1]):
                try:
                    current_point = points_on_frame[key_point]
                  #  current_point = next( (p for p in points_on_frame if p.id == point.id) )
                #index, current_point = next( ((i, p) for i, p in enumerate(points_on_frame) if p.id == point.id) )
                except:
                    points_on_frame[key_point] = points[len(points)-1][key_point]
                    print('added point')

    # линии связи между точками
    lines = []
    list_points_on_frame = list(points_on_frame.values())
    np_coord_points = np.array([[p.x, p.y] for p in list_points_on_frame])
    try:
        distances = cdist(np_coord_points, np_coord_points, metric='euclidean')
    except:
        print(len(np_coord_points), np_coord_points)
    if not points:
        first_lines = []
        for i in range(len(list_points_on_frame)):
            for j in range(i+1, len(list_points_on_frame)):
                if distances[i][j] < 55:
                    first_lines += [Line(list_points_on_frame[i], list_points_on_frame[j])]


        """for i in range(len(list_points_on_frame)):
            for j in range(i+1, len(list_points_on_frame)):
                if distances[i][j] < 55:
                    first_lines += [Line(list_points_on_frame[i], list_points_on_frame[j])]
    """
    else:
        for line in first_lines:
            new_line_point1 = points_on_frame[line.point1.id]
            new_line_point2 = points_on_frame[line.point2.id]

            len_first_line = line.len
            len_new_line = round(sqrt( (new_line_point2.x-new_line_point1.x)**2 + (new_line_point2.y-new_line_point1.y)**2 ), 2)
            lines += [Line(new_line_point1, new_line_point2, round( (len_new_line - len_first_line)/len_first_line, 2) )]

    # отрисовка линий на кадре с разными цветами в зависимости от эпсилон
    if not lines:
        for line in first_lines:
            cv2.line(frame, (line.x1, line.y1), (line.x2, line.y2), (0, 255, 0), 3, cv2.LINE_AA)
    else:
        sorted_lines = sorted(lines, key=lambda line: line.epsilon)
        min_epsilon = sorted_lines[0].epsilon
        max_epsilon = sorted_lines[len(sorted_lines)-1].epsilon
        for line in sorted_lines:
            cv2.line(frame, (line.x1, line.y1), (line.x2, line.y2), get_color_line(line.epsilon, max_epsilon, min_epsilon), 3, cv2.LINE_AA)
    
    # отрисовка линий на кадре
    """for line in lines:
        cv2.line(frame, (line.x1, line.y1), (line.x2, line.y2), (0,255,0), 3, cv2.LINE_AA)
    """
    # отрисовка значения удлинения для линий
    """if not lines:
        for line in first_lines:
            cv2.putText(frame, str(line.epsilon), ( int((line.x1+line.x2)/2) , int((line.y1+line.y2)/2 )), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    else:
        for line in lines:
            cv2.putText(frame, str(line.epsilon), ( int((line.x1+line.x2)/2) , int((line.y1+line.y2)/2 )), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)"""
    
    # отрисовываем id на кадре
    """for key_p in points_on_frame:
        cv2.putText(frame, str(key_p), (points_on_frame[key_p].x, points_on_frame[key_p].y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    """    
    points += [points_on_frame]
       
    video_writer.write(frame)  #сохраняем новые кадры в видеофайл
    
    #cv2.imshow('video', cv2.drawContours(thresh , contours, -1, (0, 255, 0), 2)) 
    cv2.imshow('video', frame) 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_writer.release()
cap.release()
cv2.waitKey(0)
cv2.destroyAllWindows()

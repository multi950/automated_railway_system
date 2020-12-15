
import cv2
import numpy as np
from matplotlib import pyplot as plt

# Original (gray) image
def apply_mask(img):
    vertices =  [
        (img.shape[1] * .25, img.shape[0]),
        (img.shape[1]* .33, img.shape[0]-185),
        (img.shape[1]* .66, img.shape[0]-185),
        (img.shape[1] * .75, img.shape[0])
    ]
    vertices =  [
        (img.shape[1] * .25, img.shape[0]),
        (img.shape[1] * .25 + 61, img.shape[0] * 0),
        (img.shape[1] * .75 - 61, img.shape[0] * 0),
        (img.shape[1] * .75, img.shape[0])
    ]
    mask = np.zeros_like(img)
    match_mask_color = 255
    cv2.fillPoly(mask, np.array([vertices], np.int32), match_mask_color)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def apply_filters(img):
    blur = cv2.GaussianBlur( img,(7, 7), 7 )
    sobelx2 = cv2.Sobel( blur, cv2.CV_64F, 1, 0, ksize=3 )
    abs_sobel64f = np.absolute( sobelx2 )
    sobel_x = np.uint8( abs_sobel64f )
    edges = cv2.Canny( sobel_x, 40, 200 )
    edges = apply_mask(edges)
    return edges


def extract_lines(img):

    lines_radial = cv2.HoughLines( img, 1, np.pi/180, 10)

    if(lines_radial is None):
         return []

    length = 1000
    lines_xy = []
    for rho,theta in lines_radial[:, 0, :]:
        a = np.cos(theta)
        b = np.sin(theta)
        x1 = int(a*rho + length *(-b))
        y1 = int(b*rho + length *(a)) 
        x2 = int(a*rho - length *(-b))
        y2 = int(b*rho - length *(a)) 
        
        line = (x1, y1,  x2, y2)
        lines_xy.append(line)
    return  lines_xy


def extract_lines_p(img):
    
    lines = cv2.HoughLinesP(img,
                            rho=2,
                            theta=np.pi/180,
                            threshold=40,
                            lines=np.array([]),
                            minLineLength=30,
                            maxLineGap=100)
    return lines.squeeze()

def process_video(src = 'output.mp4'):
    cap = cv2.VideoCapture(src)
    flag = True
    while True:
    
        if cv2.waitKey (1) & 0xFF == ord(' '):
            flag = not(flag)
            #print(flag)

        if flag == True: 
            ret, frame = cap.read()
            if frame is None:
                break
            cv2.imshow('frame', process_frame(frame, 200))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            continue
        
    cap.release()
    cv2.destroyAllWindows()


def apply_lines(img, lines, amount = 2, line_angle = 0, first_point = None):
    previous_x = 0
    for index,(x1, y1, x2, y2) in enumerate(lines):
        y = y2 - y1 if (y2 - y1) != 0 else y2 + 1 - y1
        x = x2 - x1 if (x2 - x1) != 0 else x2 + 1 - x1
        angle = (y)/(x)
        if(first_point is not None and angle < 0 and abs(first_point[0] - x2) > 4 ):
            continue
        if(first_point is not None and angle > 0 and abs(first_point[0] - x1) > 4 ):
            continue
        if(abs(angle) < line_angle):
            continue
        cv2.line(img, (x1,y1), (x2,y2),(255, 255, 255), 2 )
        if(index >= amount - 1):
            break
    return img


def move_lines(lines, x = 0, y = 0):
    for index, line in enumerate(lines):
        lines[index] = move_line(line, x, y)
    return lines

def move_line(line, x = 0, y = 0):
    if(x is None): 
        x = 0
    if(y is None): 
        y = 0

    x1, y1, x2, y2 = line
    x1 += x
    y1 += y
    x2 += x  
    y2 += y
    return (x1, y1, x2, y2)

def get_start_point(line):
    #print(line)
    (x1, y1, x2, y2) = line
    if y1 > y2:
        return (x1, y1)
    else:
        return (x2, y2)

def get_end_point(line):
    #print(line)
    (x1, y1, x2, y2) = line
    if y1 < y2:
        return (x1, y1)
    else:
        return (x2, y2)

# returns the box
# 
def get_box(frame, point, size):
    (x, y) = point
    x = x - int(size/2)
    #print("get box: ", x,x+size,y-size,y)
    box = frame[y-size:y,x:x+size]
    return box

def process_frame(full_img, line_y_limit = 0):

     
    
        filtered_image = apply_filters(full_img)
        
        #lines = extract_lines(filtered_image)

        lines = extract_lines_from_area(filtered_image, y1 = full_img.shape[0]-line_y_limit, y2 = full_img.shape[0], line_p=True)

        lines = cut_endpoints(lines, filtered_image.shape[0])
        box_size = 30

        left_rail = 275
        right_rail = 375

        lines = list(filter(lambda line: is_close(line, [left_rail, right_rail], 20), lines))


        full_img = apply_lines(full_img  , lines, 2, 0.5)


        return full_img
        #cv2.waitKey(0)

def img_from_box_algorithm(lines):
    start_point_1 = get_start_point(lines[0])
    start_point_2 = get_start_point(lines[1])
    box1 = get_box(filtered_image, start_point_1, 60)
    box2 = get_box(filtered_image, start_point_2, 60)
    for i in range(5):

        x1, y1, x2, y2 = get_box_coordinates(start_point_1, box_size)
        lines_in_box1 = extract_lines_from_area(filtered_image, x1, y1, x2, y2, line_p=False)
        x1, y1, x2, y2 = get_box_coordinates(start_point_2, box_size)
        lines_in_box2 = extract_lines_from_area(filtered_image, x1, y1, x2, y2, line_p=False)
        full_img = draw_marker(full_img, start_point_1, box_size)
        full_img = draw_marker(full_img, start_point_2, box_size)
        full_img = apply_lines(full_img  , lines_in_box1, 1, 0.5, start_point_1)
        full_img = apply_lines(full_img  , lines_in_box2, 1, 0.5, start_point_1)
        if (len(lines_in_box1) != 0):
            start_point_1 = get_end_point(lines_in_box1[0]) 
        if (len(lines_in_box2) != 0):
            start_point_2 = get_end_point(lines_in_box2[0])
    return full_img


def is_close(line, targets, distance = 4):
    (x_start, y_start) = get_start_point(line)
    for target in targets:
        if(abs(x_start - target) <= distance):
            return True
    return False



def get_box_coordinates(point, box_size):
    x1 = point[0] - int(box_size/2)
    x2 = point[0] + int(box_size/2)
    y1 = point[1] - int(box_size)
    y2 = point[1]
    return (x1, y1, x2, y2)

def extract_lines_from_area(img, x1 = None, y1 = None, x2 = None, y2 = None, line_p = False):
    roi = img[y1:y2,x1:x2]
    if(line_p):
        lines = extract_lines_p(roi)
    else:
        lines = extract_lines(roi)
    lines = cut_endpoints(lines, roi.shape[0])   
    lines = move_lines(lines, x1, y1)
    
    return lines
      

def move_point(point, x = 0, y = 0):
    point[0] += x
    point[1] += y
    return point

def draw_marker(img, xy, marker_size):
    (x, y) = xy
    y -= int(marker_size/2)
    return cv2.drawMarker(img, (x, y), (255, 255, 255),
                markerType=cv2.MARKER_SQUARE,
                markerSize=marker_size,
                thickness=2,
                line_type=cv2.LINE_AA)


def cut_endpoints(lines, img_height):
    for index, line in enumerate(lines):
        line = cut_endpoint(line, img_height)
        lines[index] = line
    return lines
    
def cut_endpoint(lines, img_height):
    
    (x1, y1, x2, y2) = lines
    if (x2 - x1 == 0): 
        x2 += 1
    if (y2 - y1 == 0): 
        y2 += 1
    m = float(y2 - y1)/(x2 - x1)
    c = float(y2 - m*x2)
    y1 = img_height
    y2 = 0
    x1 = int((y1 - c) / m)
    x2 = int((y2 - c) / m)
    return (x1,y1,x2,y2)
    



image = process_frame(cv2.imread("railway-detection/image-smallbw.jpg"), 200)
#cv2.imshow('frame', image)

process_video()
wait_time = 500
while cv2.getWindowProperty('frame', cv2.WND_PROP_VISIBLE) >= 1:
    keyCode = cv2.waitKey(wait_time)
    if (keyCode & 0xFF) == ord("q"):
        cv2.destroyAllWindows()
        break
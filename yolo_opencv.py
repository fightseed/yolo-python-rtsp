#############################################
# Object detection - YOLO - OpenCV
# Author : Arun Ponnusamy   (July 16, 2018)
# Website : http://www.arunponnusamy.com
############################################

import os
import cv2
import argparse
import numpy as np
import imageio
import datetime

OUTPUT_DIR = "output"

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--image', required=False,
                help = 'path to input image', default = 'sampledata/frontdoor.mp4')
ap.add_argument('-c', '--config', required=False,
                help = 'path to yolo config file', default = 'yolov3.cfg')
ap.add_argument('-w', '--weights', required=False,
                help = 'path to yolo pre-trained weights', default = 'yolov3.weights')
ap.add_argument('-cl', '--classes', required=False,
                help = 'path to text file containing class names',  default = 'yolov3.txt')
args = ap.parse_args()


def get_output_layers(net):
    
    layer_names = net.getLayerNames()
    
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers

def save_bounded_image(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    dirname = os.path.join(OUTPUT_DIR, label, datetime.datetime.now().strftime('%Y-%m-%d'))
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    
    filename = label + '_' + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S_%f') + '_conf' + "{:.2f}".format(confidence) + '.jpg'
    print ('Saving bounding box:' + filename)
    roi = orgImg[y:y_plus_h, x:x_plus_w]
    cv2.imwrite(os.path.join(dirname, filename), cv2.cvtColor(roi, cv2.COLOR_RGB2BGR))  

def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    color = COLORS[class_id]

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def detect(image):
        
    Width = image.shape[1]
    Height = image.shape[0]
    scale = 0.00392
    
    classes = None
    
    with open(args.classes, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    
    net = cv2.dnn.readNet(args.weights, args.config)
    
    blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
    
    net.setInput(blob)
    
    outs = net.forward(get_output_layers(net))
    
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4
    
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
    
    
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    
    for i in indices:
        i = i[0]
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
        save_bounded_image(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))

    writer.append_data(image)

# Doing some Object Detection on a video
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

#reader = imageio.get_reader(args.image)
#fps = reader.get_meta_data()['fps']
#writer = imageio.get_writer('output.mp4', fps = fps)
#totalImages = str(len(reader))

#for i, image in enumerate(reader):
#    if i > 110 and i < 250:
#        detect(image)
# writer.close()

writer = imageio.get_writer('output.mp4', fps = fps)
cap = cv2.VideoCapture('rtsp://192.168.0.210:7447/xxx') 
frame_counter = 0
while(True):
    # Capture frame-by-frame
    print('Processing frame ' + str(frame_counter))
    ret, frame = cap.read()
    if not frame is None:
        detect(frame)
    frame_counter=frame_counter+1
    if frame_counter > 150:
        break
       
writer.close()

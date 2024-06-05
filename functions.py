from vision.ssd.vgg_ssd import create_vgg_ssd, create_vgg_ssd_predictor
from vision.ssd.mobilenetv1_ssd import create_mobilenetv1_ssd, create_mobilenetv1_ssd_predictor
from vision.ssd.mobilenetv1_ssd_lite import create_mobilenetv1_ssd_lite, create_mobilenetv1_ssd_lite_predictor
from vision.ssd.squeezenet_ssd_lite import create_squeezenet_ssd_lite, create_squeezenet_ssd_lite_predictor
from vision.ssd.mobilenet_v2_ssd_lite import create_mobilenetv2_ssd_lite, create_mobilenetv2_ssd_lite_predictor
from vision.utils.misc import Timer
import cv2
import sys
import numpy as np
import time
from constants import *

def initialize_models(net_type, model_path, label_path, size_candidate):
    class_names = [name.strip() for name in open(label_path).readlines()]

    if net_type == 'mb1-ssd':
        net = create_mobilenetv1_ssd(len(class_names), is_test=True)
    else:
        print("The net type is wrong")
        sys.exit(1)
    net.load(model_path)

    if net_type == 'mb1-ssd':
        predictor = create_mobilenetv1_ssd_predictor(net, candidate_size=size_candidate)
    else:
        predictor = create_vgg_ssd_predictor(net, candidate_size=size_candidate)

    return class_names, predictor

def predict_image(filepath, class_names, predictor):
  
  target_filepath = './static/temp_file_annotated.{}'.format(filepath.split('.')[-1])

  orig_image = cv2.imread(filepath)
  height, width, *_ = orig_image.shape
  image = cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), -1)
  boxes, labels, probs = predictor.predict(image, 10, 0.4)

  for i in range(boxes.size(0)):
    box = boxes[i, :]
    probability = int(probs[i]*100)
    cv2.rectangle(orig_image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), classes_dict[class_names[labels[i]]]['color'], 4)
    label = "{}, probability:{}%".format(classes_dict[class_names[labels[i]]]['team'], probability)
    cv2.putText(orig_image, label, (int(box[0]) + 20, int(box[1]) + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
  cv2.imwrite(target_filepath, orig_image)
  
  return target_filepath, int(height/2), int(width/2)

def predict_video(filepath, class_names, predictor):
    
    target_content_path = "./static/temp_file_annotated.mp4"
    
    cap = cv2.VideoCapture(filepath)  # capture from file

    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    timer = Timer()
    width = int(cap.get(3))
    height = int(cap.get(4))
    fps2 = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'h264') 
    out = cv2.VideoWriter(target_content_path, fourcc, fps2, (width,height))

    while True:
        ret, orig_image = cap.read()
        if orig_image is None:
            continue
        while(ret):
            image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB)
            timer.start()
            boxes, labels, probs = predictor.predict(image, 10, 0.7)
            interval = timer.end()
            print('Time: {:.2f}s, Detect Objects: {:d}.'.format(interval, labels.size(0)))
            for i in range(boxes.size(0)):
                box = boxes[i, :]
                probability = int(probs[i]*100)
                label = "{}, probability:{}%".format(classes_dict[class_names[labels[i]]]['team'], probability)
                cv2.rectangle(orig_image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), classes_dict[class_names[labels[i]]]['color'], 4)
                cv2.putText(orig_image, label, (int(box[0])+20, int(box[1])+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            out.write(orig_image)
            fps = cap.get(cv2.CAP_PROP_FPS)
            print ('FPS : {0}'.format(fps))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            ret, orig_image = cap.read()
        break
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    #TODO: maybe add timestamp here as well? (to enable multiple users)
    return target_content_path, int(width/2), int(height/2)
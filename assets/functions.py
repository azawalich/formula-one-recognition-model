import numpy as np
import supervision as sv
import cv2
from roboflow import Roboflow
import tempfile
import functools
from assets import constants as cst

def initialize_roboflow(key_api):
    rf = Roboflow(api_key=key_api)
    project = rf.workspace().project(cst.roboflow_project)
    model = project.version(cst.roboflow_project_version).model
    return model

def predict_image(filepath, roboflow_model):
    target_filepath = './static/temp_file_annotated.{}'.format(filepath.split('.')[-1])

    result = roboflow_model.predict(filepath, confidence=cst.confidence_val, overlap=cst.overlap_val).json()

    labels = [item["class"] for item in result["predictions"]]

    detections = sv.Detections.from_roboflow(result)

    label_annotator = sv.LabelAnnotator()
    box_annotator = sv.BoxAnnotator()

    image = cv2.imread(filepath)

    image_annotated = box_annotator.annotate(scene=image, detections=detections)
    image_annotated = label_annotator.annotate(scene=image_annotated, detections=detections, labels=labels)

    cv2.imwrite(target_filepath, image_annotated)

    return target_filepath

# define call back function to be used in video processing
def video_callback(frame: np.ndarray, index:int, pathfile, model_roboflow, byte_tracker, box_annotator) -> np.ndarray:    
    
    video_info = sv.VideoInfo.from_video_path(pathfile)
    zone = sv.PolygonZone(polygon=cst.polygon, frame_resolution_wh=(video_info.width, video_info.height))
    zone_annotator = sv.PolygonZoneAnnotator(thickness=cst.thickness, text_thickness=cst.text_thickness, text_scale=cst.text_scale, zone=zone, color=cst.colors.colors[0])
    # model prediction on single frame and conversion to supervision Detections
    # with tempfile.NamedTemporaryFile(suff?ix=".jpg") as temp:
    results = model_roboflow.predict(frame).json()

    detections = sv.Detections.from_inference(results)

    # tracking detections
    detections = byte_tracker.update_with_detections(detections)

    labels = []

    for single_detection in detections:
        if type(single_detection) is tuple:
            class_chosen = single_detection[3]
            probability = int(round(single_detection[2]*100,0))
        else:
            class_chosen = single_detection.class_id[0]
            probability = int(round(single_detection.confidence*100,0))
            
        long_label = "{}, probability: {}%".format(cst.classes[class_chosen], probability)
        indeks = list(cst.classes.keys()).index(class_chosen)
        labels.append(long_label)

    box_annotator.color = cst.colors.colors[indeks]
    zone_annotator.color = cst.colors.colors[indeks]
    
    annotated_frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
    annotated_frame = zone_annotator.annotate(scene=annotated_frame)
    
    # return frame with box and line annotated result
    return annotated_frame

def predict_video(filepath, roboflow_model, tracker_byte, annotator_box):

    video_callback_partial = functools.partial(video_callback, pathfile=filepath, model_roboflow=roboflow_model, byte_tracker=tracker_byte, box_annotator=annotator_box)
    target_content_path = "./static/temp_file_annotated.mp4"
    # process the whole video
    sv.process_video(
        source_path = filepath,
        target_path = target_content_path,
        callback=video_callback_partial
    )

    return target_content_path
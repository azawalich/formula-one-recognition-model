import numpy as np
import supervision as sv

polygon = np.array([
    [0, 0],
    [50, 0],
    [50, 50],
    [0, 50]
])

classes = {
    1: "Williams",
    37: "Alpine",
    3: "Red_Bull",
    797: "Ferrari",
    773: "Haas",
    1107: "Mercedes",
    808: "McLaren",
    2: "Alpha_Tauri",
    0: "BWT"
}

colors = sv.ColorPalette(colors=[
    sv.Color(r=0, g=130, b=250), 
    sv.Color(r=255, g=245, b=0), 
    sv.Color(r=6, g=0, b=239), 
    sv.Color(r=192, g=0, b=0), 
    sv.Color(r=120, g=120, b=120), 
    sv.Color(r=0, g=210, b=190), 
    sv.Color(r=255, g=135, b=0), 
    sv.Color(r=200, g=200, b=200), 
    sv.Color(r=255, g=0, b=255)
    ])

roboflow_project = "detection-f1-cars"
roboflow_project_version = 11
confidence_val = 40
overlap_val = 30
image_size = 16 
indeks = 0 # default color
track_activation_threshold=0.25
lost_track_buffer=30
minimum_matching_threshold=0.8
frame_rate=30
thickness=4
text_thickness=4
text_scale=2
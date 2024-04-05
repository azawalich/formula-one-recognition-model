import numpy as np
import supervision as sv

polygon = np.array([
    [0, 0],
    [50, 0],
    [50, 50],
    [0, 50]
])

classes_dict = {
    1: {
      'team': "Williams",
      'color': sv.Color(r=200, g=200, b=200) # Alpha Tauri original color
    },
    37: {
      'team': "Alpine",
      'color': sv.Color(r=255, g=245, b=0)
    },
    3: {
      'team': "Red Bull",
      'color': sv.Color(r=255, g=0, b=255) # BWT original color
    },
    797: {
      'team': "Ferrari",
      'color': sv.Color(r=6, g=0, b=239) # Red Bull original color
    },
    773: {
      'team': "Haas",
      'color': sv.Color(r=120, g=120, b=120)
    },
    1107: {
      'team': "Mercedes",
      'color': sv.Color(r=0, g=210, b=190)
    },
    808: {
      'team': "McLaren",
      'color': sv.Color(r=255, g=135, b=0)
    },
    0: {
      'team': "Alpha Tauri",
      'color': sv.Color(r=0, g=130, b=250) # Williams original color
    },
    2: {
      'team': "BWT",
      'color': sv.Color(r=192, g=0, b=0) # Ferrari original color
    }
}

colors_palette = sv.ColorPalette(colors=[])
classes = {}
for single_item in list(classes_dict.keys()):
    colors_palette.colors.append(classes_dict[single_item]['color'])
    classes[single_item] = classes_dict[single_item]['team']

default_color_palette = sv.ColorPalette(colors=[sv.Color(r=6, g=0, b=239)])
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
thickness=1
text_thickness=1
text_scale=1
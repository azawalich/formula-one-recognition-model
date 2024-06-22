net_type = 'mb1-ssd'
model_path = './models/carspls/mb1-ssd-Epoch-537-Loss-0.664390986164411.pth'
label_path = './models/carspls/labels.txt'
size_candidate = 200
classes_dict = {
    "BACKGROUND": {
      'team': "Background",
      'color': (0,0,0)
    },
    "alfa_romeo": {
      'team': "Alfa Romeo Racing",
      'color': (155,0,0)
    },
    'williams': {
      'team': "Williams",
      'color': (255,255,255)
    },
    "renault": {
      'team': "Renault",
      'color': (0,210,190) # original mercedes colour 
    },
    "redbull": {
      'team': "Red Bull Racing",
      'color': (220,0,0) # original ferrari colour 
    },
    "ferrari": {
      'team': "Ferrari",
      'color': (30,65,255) # original red bull racing colour 
    },
    "haas": {
      'team': "Haas",
      'color': (240,215,135)
    },
    "mercedes": {
      'team': "Mercedes",
      'color': (255,245,0) # original renault colour 
    },
    "mclaren": {
      'team': "McLaren",
      'color': (70,155,255) # original toro rosso colour 
    },
    "toro_rosso": {
      'team': "Toro Rosso",
      'color': (255,135,0) # original mclaren colour 
    },
    "bwt": {
      'team': "Racing Point",
      'color': (245,150,200)
    }
}


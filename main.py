import base64
import os
import glob
import argparse

from assets import constants as cst
from assets import functions as fct

import supervision as sv
import uvicorn
from fastapi import FastAPI, UploadFile, File, Request, APIRouter
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount(
    "/static", 
    StaticFiles(directory="static"), 
    name="static"
)

templates = Jinja2Templates(directory="templates")
# api_key_gp = os.environ['ROBOFLOW_API_KEY']
api_key_gp = "rXEt6FwM5uzppisJT2IF"

model = fct.initialize_roboflow(key_api=api_key_gp)
byte_tracker = sv.ByteTrack(
    track_activation_threshold=cst.track_activation_threshold, 
    lost_track_buffer=cst.lost_track_buffer, 
    minimum_matching_threshold=cst.minimum_matching_threshold, 
    frame_rate=cst.frame_rate
)
box_annotator = sv.BoxAnnotator(
    thickness=cst.thickness, 
    text_thickness=cst.thickness, 
    text_scale=cst.thickness, 
    color=cst.colors_palette
)

@app.get("/healthcheck")
async def root():
    return {"message": "Hello World"}

@app.get("/")
def dynamic_file(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
 
@app.post("/predict")
def dynamic(request: Request, file: UploadFile = File()):
    
    is_video = 0
    is_image = 0

    base64_extensions = {
        '.jpg': "/9j/",
        '.png': "iVBO",
        '.gif': "R0lG",
        '.tif': "SUkq"
    }
    base64_extensions_bytes_flattened = [x for xs in list(base64_extensions.items()) for x in xs] 

    # cleanup stuff at the beginning of each processing
    files = glob.glob('./static/temp_file*')
    for f in files:
        os.remove(f)

    data = file.file.read()
    file.file.close()

    # encoding the content
    encoded_entry_content = base64.b64encode(data).decode("utf-8")

    start_bytes_source_file = encoded_entry_content[0:4]

    # TODO: I think it could be improved, to get filenames more easily
    if start_bytes_source_file in base64_extensions_bytes_flattened: #.jpg, .png, .gif, .tif, .tif
        is_image = 1
        source_file_extension = [k for k,v in base64_extensions.items() if v == start_bytes_source_file][0]
    # elif start_bytes_source_file in ["RkxW", "UklG"]: #.flv, .wav and others
        # is_video = 1
        # content_filepath = "./video.mp4"
    else: # others, strange, let's assume it is video
        is_video = 1
        source_file_extension = ".mp4"
        
    source_content_filepath = "./static/temp_file{}".format(source_file_extension)

    with open(source_content_filepath, "wb") as binary_file:
        binary_file.write(data)
    binary_file.close()

    if is_image == 1:
        result_content_filepath = fct.predict_image(
            source_content_filepath, 
            model
        )

    if is_video == 1:    
        result_content_filepath = fct.predict_video(
            source_content_filepath, 
            model, 
            byte_tracker, 
            box_annotator
        )

    result_content_filepath = result_content_filepath.replace('./static/', '')

    return templates.TemplateResponse(
        "predict.html", {
            "request": request, 
            "content_filepath": result_content_filepath, 
            "is_image": is_image, 
            "is_video": is_video
            }
        )

@app.get("/annotated-video/{video}")
async def see_video(video):
    return FileResponse(video) 

uvicorn.run(app, host = "0.0.0.0")
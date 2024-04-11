import base64
import os
import glob
import argparse
import time
from minio import Minio
from minio.error import InvalidResponseError
import urllib3

from assets import constants as cst
from assets import functions as fct

import supervision as sv
import uvicorn
from fastapi import FastAPI, UploadFile, File, Request, APIRouter
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--minio-url')
parser.add_argument('-a', '--access-key')
parser.add_argument('-s', '--secret-key')
parser.add_argument('-r', '--roboflow-api-key')
parser.add_argument('-d', '--debugging-local')
args = parser.parse_args()

httpClient = urllib3.PoolManager(cert_reqs="CERT_NONE")

minio_client = Minio(args.minio_url,
               access_key=args.access_key,
               secret_key=args.secret_key,
               http_client=httpClient
              )

bucket_name = "recognize"

app = FastAPI()
app.mount(
    "/static", 
    StaticFiles(directory="static"), 
    name="static"
)

templates = Jinja2Templates(directory="templates")
api_key_gp = args.roboflow_api_key

files = {
    item: os.path.join('static', item)
    for item in os.listdir('static')
}

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

#TODO: could create endpoint with API response only

@app.get("/healthcheck")
async def root():
    return {"message": "Hello World"}

@app.get("/")
def dynamic_file(request: Request, local_debugging = args.debugging_local):
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "debugging_local": local_debugging
            }
        )
 
@app.post("/predict")
def dynamic(request: Request, file: UploadFile = File(), debugging_local = args.debugging_local):
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

    original_filename = file.filename
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

    current_timestamp = int(str(time.time()).replace('.', ''))

    minio_client.fput_object(
        bucket_name, '{}_{}'.format(current_timestamp, original_filename), source_content_filepath
    )

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
            box_annotator,
            original_filename,
            minio_client,
            bucket_name
        )

    current_timestamp = int(str(time.time()).replace('.', ''))

    minio_client.fput_object(
        bucket_name, '{}_annotated_{}'.format(current_timestamp, original_filename), result_content_filepath
    )

    result_content_filepath = result_content_filepath.replace('./static/', '')

    return templates.TemplateResponse(
        "predict.html", {
            "request": request, 
            "content_filepath": result_content_filepath, 
            "is_image": is_image, 
            "is_video": is_video,
            'video': {'path': result_content_filepath, 'name': result_content_filepath.split('/')[-1]},
            "debugging_local": debugging_local
            }
        )

@app.get("/get_video/{video_name}")
async def get_video(video_name: str, response_class=FileResponse):
    video_path = files.get(video_name)
    if video_path:
        return StreamingResponse(open(video_path, 'rb'))
    else:
        return Response(status_code=404)

uvicorn.run(app, host = "0.0.0.0")
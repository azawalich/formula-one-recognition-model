import base64
import os
import glob
import argparse
import time
from minio import Minio
from minio.error import InvalidResponseError
import urllib3
from datetime import timedelta
from functions import * 
from constants import * 

import uvicorn
from fastapi import FastAPI, UploadFile, File, Request, APIRouter
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--minio-url')
parser.add_argument('-a', '--access-key')
parser.add_argument('-s', '--secret-key')
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

class_names, predictor = initialize_models(net_type, model_path, label_path, size_candidate)

files = {
    item: os.path.join('static', item)
    for item in os.listdir('static')
}

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
        result_content_filepath, height_half, width_half = predict_image(
            source_content_filepath, 
            class_names, 
            predictor
        )

    if is_video == 1:    
        result_content_filepath, height_half, width_half = predict_video(
            source_content_filepath, 
            class_names, 
            predictor
        )

    current_timestamp = int(str(time.time()).replace('.', ''))
    minio_filename = '{}_annotated_{}'.format(current_timestamp, original_filename)

    minio_client.fput_object(
        bucket_name, minio_filename, result_content_filepath
    )

    minio_file_url = minio_client.get_presigned_url(
        "GET", bucket_name,minio_filename, expires=timedelta(hours=1)
    )

    result_content_filepath = result_content_filepath.replace('./static/', '')

    return templates.TemplateResponse(
        "predict.html", {
            "request": request, 
            "content_filepath": result_content_filepath, 
            "is_image": is_image, 
            "is_video": is_video,
            "width_half": width_half, 
            "height_half": height_half,
            "url": minio_file_url,
            "debugging_local": debugging_local
            }
        )

uvicorn.run(app, host = "0.0.0.0")
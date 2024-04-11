# formula-one-recognition-model
Repository holds code and data for video classification model - of cars representing particular teams in Formula 1.

# Repository structure
- `/assets`: Python modules for separating functions from `main.py` API file,
- `/input`: data for model training, validation and testing are stored here. The amount of images commited is an example - I reduced their number to lessen the amount of storage held in GitHub/GitLab,
- `/static`: folder for serving model-annotated files. Cleaned-up after sending any request to `/predict` API endpoint,
- `/templates`: HTML templates to render with `Jinja` Python templating framework,
- `formula-one-video-classification.ipynb`: improved / fixed jupyter notebook explaining model usage process (by [tarik-yilmaz-kanzileri on Roboflow](https://universe.roboflow.com/tarik-yilmaz-kanzileri/detection-f1-cars)),
- `main.py`: Python file with API implementation and endpoints created with `FastAPI` framework,
- `README.md`: `Markdown`-based file you are currently reading,
- `requirements.txt`: file with minimum package requirements necessary for API to work properly,
- `environment.yaml`: file with full package requirements, necessary for above-mentioned `jupyter notebook` to work without errors.

# Docker image
## Building
```
docker build --no-cache \
--build-arg MINIO_URL="<change_me>" \
--build-arg ROBOFLOW_API_KEY="<change_me>" \
-t f1-recognition-model:v0.4 -f Dockerfile .
```
## Running
```
docker run -it \
-e MINIO_URL="<change_me>" \
-e MINIO_ACCESS_KEY="<change_me>" \
-e MINIO_SECRET_KEY="<change_me>" \
-e ROBOFLOW_API_KEY="<change_me>" \
f1-recognition-model:v0.4
```

# Adding image to use in minikube
`minikube image load f1-recognition-model:v0.4`

# Example
## Image
### Base
![sample image](./input/lando-norris-mclaren-mcl35m-1.png)
### Annotated
![sample image annotated](./input/lando-norris-mclaren-mcl35m-1_annotated.png)
## Video
### Base
![sample video](./input/sample_video_1.mp4)
### Annotated
![sample video annotated](./input/sample_video_1_annotated.mp4)

# Model 
## Statistics
- Version: `11`,
- Classes:
  - confirmed:
    - `Ferrari`,
    - `Mclaren`,
    - `Mercedes`,
    - `Redbull`.
  - not confimed:
    - `Williams`,
    - `Alpine`,
    - `Haas`,
    - `Alpha_Tauri`,
    - `BWT`.
  - missing:
    - `Sauber`.
- mAP: `95.5%`,
- Precision: `92.0%`,
- Recall: `93.9%`.

## Output
bounding box with Team name and probability

## Training Graphs
![training graphs](https://storage.googleapis.com/roboflow-platform-cache/0rwi5tTqGphZ9WeAqy8Y1qh5G9S2/3gsXbN6o6fS93VJgZoc8/11/results.png)

# Sources / Acknowledgements
## F1 Cars Video
### classification model: [by Tarik Yilmaz Kanzileri, available here](https://universe.roboflow.com/tarik-yilmaz-kanzileri),
### containerization and API creation: [by Aleksander Zawalich, available here](https://github.com/azawalich).
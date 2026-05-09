import urllib.request

url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
urllib.request.urlretrieve(url, "face_landmarker_v2_with_blendshapes.task")

print("Download complete")
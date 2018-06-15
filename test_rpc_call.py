import jsonrpcclient
import base64
import cv2
import subprocess
import yaml
import json

with open("turtles.png", "rb") as f:
    img = f.read()
    image_64 = base64.b64encode(img).decode("utf-8")

f_landmark_address = "0x88DeC961e30F973b6DeDbae35754a3c557380BEE"
f_detect_address = "0x4cBe33Aa28eBBbFAa7d98Fa1c65af2FEf6885EF2"

# TODO compare the result one gets from face_detect library with the one we have.
expected_response  = {"bounding boxes": "[rectangle(572,112,676,215), rectangle(841,161,991,311), rectangle(365,42,469,146), rectangle(411,286,535,411), rectangle(742,93,867,217), rectangle(145,112,294,261)]", "predictions": "['fear', 'happy', 'sad', 'happy', 'anger', 'happy']"}

def test_emotion_rpc_call():
        response = jsonrpcclient.request("http://127.0.0.1:{}".format(8001), "classify",image=image_64, image_type="png")
        assert response == expected_response

def test_face_detect_agent_availability():
    process = subprocess.Popen(["snet","registry","query","face_detect"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try:
        outs, errs = process.communicate(timeout=30)
        record = yaml.load(outs)
        assert f_detect_address == record["record"]["agent"]
    except TimeoutExpired:
        # Kill process and then communicate to make sure it has exited.
        process.kill()
        outs, errs = proc.communicate()

def test_face_detect_agent_call():
    request = {"image": image_64, "algorithm": "dlib_cnn"}
    request_dump = json.dumps(request)
    with open('request_face','wt') as f:
        f.write(request_dump)
    process = subprocess.Popen(["snet", "client", "call", "--no-confirm", "find_face", "request_face"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try: 
        outs, errs = process.communicate(timeout=120)
        result = yaml.load(outs)
        with open('result_face.yaml', 'wb') as f:
            f.write(outs)
    except TimeoutExpired:
        process.kill()
        outs. errs = proc.communicate()

# def test_face_landmarks_agent_availability():
#     process = subprocess.Popen(["snet","registry","query","face_landmarks"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
#     try:
#         outs, errs = process.communicate(timeout=30)
#         record = yaml.load(outs)
#         assert f_landmark_address == record["record"]["agent"]
# 
#     except TimeoutExpired:
#         # Kill process and then communicate to make sure it has exited.
#         process.kill()
#         outs, errs = proc.communicate()
# 
# def test_face_landmarks_agent_call():
#     process = subprocess.Popen(["snet", "client", "call", "get_landmarks",""], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
#     try:
#         outs, errs = process.communicate(timeout=30)
#         assert self.f_landmark_address == record["record"]["agent"]
#         record = yaml.load(outs)
#     except TimeoutExpired:
#         # Kill process and then communicate to make sure it has exited.
#         process.kill()
#         outs, errs = proc.communicate()

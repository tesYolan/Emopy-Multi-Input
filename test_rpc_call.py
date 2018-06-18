""" Tests for integration with other agents.

This test file checks the availability of different end points on the alpha to relay on them
to create interdependent inter-operation to provide specified requirements
"""
import base64
import jsonrpcclient
import pprint
import subprocess
import yaml

import sys
# TODO be better at python3.6 module management
sys.path = sys.path + ['.']
import snet

with open("turtles.png", "rb") as f:
    IMG = f.read()
    IMAGE_64 = base64.b64encode(IMG).decode("utf-8")

F_LANDMARK_ADDRESS = "0x88DeC961e30F973b6DeDbae35754a3c557380BEE"
F_DETECT_ADDRESS = "0x4cBe33Aa28eBBbFAa7d98Fa1c65af2FEf6885EF2"

PP = pprint.PrettyPrinter(indent=4)

# TODO compare the result one gets from face_detect library with the one we have.
EXPECTED_RESPONSE = {"bounding boxes": "[rectangle(572,112,676,215), rectangle(841,161,991,311), rectangle(365,42,469,146), rectangle(411,286,535,411), rectangle(742,93,867,217), rectangle(145,112,294,261)]",
                     "predictions": "['fear', 'happy', 'sad', 'happy', 'anger', 'happy']"}

RETURNED_RESULT_DLIB_CNN = {'faces': [{'x': 847, 'y': 166, 'w': 113, 'h': 124}, {'x': 571, 'y': 116, 'w': 95, 'h': 104}, {'x': 409, 'y': 292, 'w': 114, 'h': 125}, {
    'x': 363, 'y': 39, 'w': 114, 'h': 125}, {'x': 155, 'y': 131, 'w': 114, 'h': 125}, {'x': 754, 'y': 85, 'w': 114, 'h': 125}]}

RETURNED_RESULT_DLIB_HOG = {'faces': [{'x': 569, 'y': 116, 'w': 108, 'h': 107}, {'x': 841, 'y': 168, 'w': 129, 'h': 129}, {'x': 366, 'y': 44, 'w': 108, 'h': 108}, {
    'x': 153, 'y': 125, 'w': 129, 'h': 129}, {'x': 411, 'y': 297, 'w': 129, 'h': 129}, {'x': 741, 'y': 96, 'w': 129, 'h': 129}]}


def test_emotion_rpc_call():
    """test_emotion_rpc_call"""
    response = jsonrpcclient.request(
        "http://127.0.0.1:{}".format(8001), "classify", image=IMAGE_64, image_type="jpg")
    assert response == EXPECTED_RESPONSE, "Is local jsonrpcserver running"


def test_face_detect_agent_availability():
    """test_face_detect_agent_availability"""
    print(snet.agent_availability("face_detect"))
    record, _, errs = snet.agent_availability("face_detect")
    assert errs is None, "Something went bad when querying for face_detect. Does it exist?"
    assert F_DETECT_ADDRESS == record["record"]["agent"], "Face detect address registered and expected address do not match. Expected {} but got {}".format(F_DETECT_ADDRESS, record["record"]["agent"])


def test_face_detect_agent_call():
    """test_face_detect_agent_call"""
    result, _, errs = snet.agent_job_create(F_DETECT_ADDRESS)
    assert errs is None, "There is error when creating jobs at agent {}".format(F_DETECT_ADDRESS)

    endpoint, _, errs = snet.agent_job_endpoint(F_DETECT_ADDRESS)
    assert errs is None, "Error when looking for endpoint of an agent at {}".format(F_DETECT_ADDRESS)

    request = {"image": IMAGE_64, "algorithm": "dlib_cnn"}

    response = snet.agent_rpc_call(request, "find_face", result, endpoint)

    assert response == RETURNED_RESULT_DLIB_CNN, "Expected results and returned face detections don't match"


def test_face_landmarks_agent_availability():
    """test_face_landmarks_agent_availability"""
    record, _, errs = snet.agent_availability("face_landmarks")
    assert errs is None, "Something went bad when querying for face_detect. Does it exist?"
    assert F_LANDMARK_ADDRESS == record["record"]["agent"], "Face detect address registered and expected address do not match. Expected {} but got {}".format(F_LANDMARK_ADDRESS, record["record"]["agent"])



def test_face_landmarks_agent_call():
    """test_face_landmarks_agent_call"""
    result, out, errs = snet.agent_job_create(F_LANDMARK_ADDRESS)
    assert errs is None, "There is error when creating jobs at agent {}".format(F_DETECT_ADDRESS)

    endpoint, out, errs = snet.agent_job_endpoint(F_LANDMARK_ADDRESS)
    assert errs is None, "Error when looking for endpoint of an agent at {}".format(F_DETECT_ADDRESS)

    request = {"image": IMAGE_64, "landmark_model": "68", "face_bboxes": RETURNED_RESULT_DLIB_HOG['faces']}

    response = snet.agent_rpc_call(request, "get_landmarks", result, endpoint)
    PP.pprint(response)

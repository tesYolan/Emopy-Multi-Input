""" Tests for integration with other agents.

This test file checks the availability of different end points on the alpha to relay on them
to create interdependent inter-operation to provide specified requirements
"""
import base64
import jsonrpcclient
import pprint
import subprocess
import yaml

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
    process = subprocess.Popen(
        ["snet", "registry", "query", "face_detect"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try:
        outs, errs = process.communicate(timeout=30)
        assert errs is None, "Something went bad when querying for face_detect. Does it exist?"
        record = yaml.load(outs)
        assert F_DETECT_ADDRESS == record["record"]["agent"], "Face detect address registered and expected address do not match. Expected {} but got {}".format(
            F_DETECT_ADDRESS, record["record"]["agent"])
    except subprocess.TimeoutExpired:
        # Kill process and then communicate to make sure it has exited.
        process.kill()
        outs, errs = process.communicate()


def test_face_detect_agent_call():
    """test_fBadace_detect_agent_call"""
    process = subprocess.Popen(["snet", "agent", "--at", F_DETECT_ADDRESS, "create-jobs", "--number", "1", "--funded",
                                "--signed", "--no-confirm", "--max-price", "1000000"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try:
        outs, errs = process.communicate(timeout=120)
        print(outs)
        assert errs is None, "There is error when creating jobs at agent {}".format(
            F_DETECT_ADDRESS)
        result = yaml.load(outs)['jobs'][0]
    except subprocess.TimeoutExpired:
        process.kill()
        outs, errs = process.communicate()

    # Now, let's get the end point of the service.

    process = subprocess.Popen(["snet", "contract", "Agent", "--at", F_DETECT_ADDRESS,
                                "endpoint"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try:
        outs, errs = process.communicate(timeout=120)
        assert errs is None, "Error when looking for endpoint of an agent at {}".format(
            F_DETECT_ADDRESS)
        endpoint = outs.decode('utf-8').splitlines()[0]
        print(endpoint)
    except subprocess.TimeoutExpired:
        process.kill()
        outs, errs = process.communicate()

    request = {"image": IMAGE_64, "algorithm": "dlib_cnn",
               "job_address": result["job_address"], "job_signature": result["job_signature"]}

    response = jsonrpcclient.request(endpoint, "find_face", request)

    assert response == RETURNED_RESULT_DLIB_CNN, "Expected results and returned face detections don't match"


def test_face_landmarks_agent_availability():
    """test_face_landmarks_agent_availability"""
    process = subprocess.Popen(["snet", "registry", "query", "face_landmarks"],
                               stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try:
        outs, errs = process.communicate(timeout=30)
        record = yaml.load(outs)
        print(record)
        assert errs is None
    except subprocess.TimeoutExpired:
        # Kill process and then communicate to make sure it has exited.
        process.kill()
        outs, errs = process.communicate()


def test_face_landmarks_agent_call():
    """test_face_landmarks_agent_call"""
    process = subprocess.Popen(["snet", "agent", "--at", F_LANDMARK_ADDRESS, "create-jobs", "--number", "1", "--funded",
                                "--signed", "--no-confirm", "--max-price", "1000000"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try:
        outs, errs = process.communicate(timeout=120)
        assert errs is None, "There is error when creating jobs at agent {}".format(
            F_LANDMARK_ADDRESS)
        result = yaml.load(outs)['jobs'][0]
        print(result)
    except subprocess.TimeoutExpired:
        # Kill process and then communicate to make sure it has exited.
        process.kill()
        outs, errs = process.communicate()

    process = subprocess.Popen(["snet", "contract", "Agent", "--at", F_LANDMARK_ADDRESS,
                                "endpoint"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    try:
        outs, errs = process.communicate(timeout=120)
        assert errs is None, "Error when looking for endpoint of an agent at {}".format(
            F_LANDMARK_ADDRESS)
        endpoint = outs.decode('utf-8').splitlines()[0]
        print(endpoint)
    except subprocess.TimeoutExpired:
        process.kill()
        outs, errs = process.communicate()

    request = {"image": IMAGE_64, "landmark_model": "68", "face_bboxes": RETURNED_RESULT_DLIB_HOG['faces'],
               "job_address": result["job_address"], "job_signature": result["job_signature"]}

    response = jsonrpcclient.request(endpoint, "get_landmarks", request)

    PP.pprint(response)

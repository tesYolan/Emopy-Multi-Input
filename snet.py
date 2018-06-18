""" Scripts wrapping around snet-cli till sdk is available
"""
import subprocess
import yaml
import jsonrpcclient


def agent_availability(agent_name):
    """agent_availability

    :param agent_name: the name of the agent one desire to query snet.
    """
    process = subprocess.Popen(
        ["snet", "registry", "query", agent_name], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    record = None
    try:
        outs, errs = process.communicate(timeout=30)
        assert errs is None, "Something went bad when querying for face_detect. Does it exist?"
        record = yaml.load(outs)
    except subprocess.TimeoutExpired:
        # Kill process and then communicate to make sure it has exited.
        process.kill()
        outs, errs = process.communicate()
    return record, outs, errs


def agent_job_create(address):
    """agent_job_create

    :param address: the address of the agent to create the job at.
    """
    process = subprocess.Popen(["snet", "agent", "--at", address, "create-jobs", "--number", "1", "--funded", "--signed", "--no-confirm", "--max-price", "1000000"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try:
        outs, errs = process.communicate(timeout=120)
        print(outs)
        assert errs is None, "There is error when creating jobs at agent {}".format(
            address)
        job = yaml.load(outs)['jobs'][0]
    except subprocess.TimeoutExpired:
        process.kill()
        outs, errs = process.communicate()

    return job, outs, errs


def agent_job_endpoint(address):
    """agent_job_endpoint

    :param address: the agent to find the endpoint for.
    """
    process = subprocess.Popen(["snet", "contract", "Agent", "--at", address,
                                "endpoint"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try:
        outs, errs = process.communicate(timeout=120)
        endpoint = outs.decode('utf-8').splitlines()[0]
    except subprocess.TimeoutExpired:
        process.kill()
        outs, errs = process.communicate()
    return endpoint, outs, errs


def agent_rpc_call(request, method, job, endpoint):
    """agent_rpc_call

    :param request: the json that is required by the agent.
    :param method: the method to call on that agent.
    :param job: the job dict file that has job_address and job_signature.
    :param endpoint: the end point of the agent.
    """
    request["job_address"] = job["job_address"]
    request["job_signature"] = job["job_signature"]

    response = jsonrpcclient.request(endpoint, method, request)

    return response

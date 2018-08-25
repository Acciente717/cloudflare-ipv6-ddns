import subprocess
import json


def generate_curl_command(conf, page):
    """
    Generate command to invoke "curl" for Cloudflare API communication.
    """
    
    pattern = """\
curl -X GET "https://api.cloudflare.com/client/v4/zones/%s/dns_records?page=%d" \
-H "X-Auth-Email:%s" -H "X-Auth-Key:%s" -H "Content-Type: application/json" \
"""
    command = pattern % (conf["zone_id"], page, conf["email"], conf["api_key"])
    
    return command


def load_user_config_file():
    """
    Load user configuration file in order to use Cloudflare API.
    """
    
    with open("./config.json") as file:
        conf = json.load(file)
    
    if conf["proxied"]:
        conf["proxied"] = "true"
    else:
        conf["proxied"] = "false"
    
    return conf


def invoke_curl_command(command):
    """
    Invoke "curl" to use Cloudflare API to update DNS record.
    """
    
    curl_subp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    stdout, _ = curl_subp.communicate()
    curl_subp.wait()
    curl_response = json.loads(stdout)
    
    return curl_response


def print_error_message(response):
    """
    Print human friendly error message.
    """
    
    print("Error occured when communicating to Cloudflare API.")
    print("The API returned the message below:")
    for error in response["errors"]:
        error_message = error["message"]
        print(error_message)
        
        
def find_record_id(page_num, conf):
    """
    Search through all pages to find desired record id.
    """
    
    dns_name = conf["name"]
    found = False
    record_id = None
    
    for i in range(page_num):
        curl_cmd = generate_curl_command(conf, i + 1)
        response = invoke_curl_command(curl_cmd)
        for entry in response["result"]:
            if entry["name"] == dns_name and entry["type"] == "AAAA":
                found = True
                record_id = entry["id"]
                break
        if found:
            break
        
    return record_id


def main():
    conf = load_user_config_file()

    dns_name = conf["name"]

    curl_cmd = generate_curl_command(conf, 1)
    response = invoke_curl_command(curl_cmd)

    if not response["success"]:
        print_error_message(response)
        exit(1)

    page_num = response["result_info"]["total_pages"]

    record_id = find_record_id(page_num, conf)

    if record_id is None:
        print("No DNS record of type AAAA is found given the name %s" % dns_name)
    else:
        print("Record id of name \"%s\" is: %s" % (dns_name, record_id))


if __name__ == "__main__":
    main()

import datetime
import subprocess
import json
import time


class CurlFailError(Exception):
    def __init__(self, msg=""):
        super(CurlFailError, self)


def invoke_ip_command():
    """
    Invoke "ip -6 addr" command, and read the output from pipe.
    """
    
    ip_subp = subprocess.Popen("ip -6 addr", shell=True, stdout=subprocess.PIPE)
    stdout, stderr = ip_subp.communicate()
    ip_subp.wait()
    
    return stdout


def find_optimal_ipv6_address(ip_response):
    """
    Given the stdout from "ip -6 addr", filter out the optimal ipv6
    address according to the lft time. (longer is better)
    """
    
    lines = str(ip_response, encoding="utf8").split("\n")
    
    opt_ipv6 = None
    opt_lft = -1
    
    for idx, line in enumerate(lines):
        if "inet6" in line and "fe80" not in line and "::1" not in line:
            ipv6 = line.split()[1].split("/")[0]
            property_line = lines[idx + 1]
            lft = int(property_line.split()[3][:-3])
            if lft > opt_lft:
                opt_ipv6, opt_lft = ipv6, lft
    
    return opt_ipv6


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


def generate_curl_command(conf, ipv6_addr):
    """
    Generate command to invoke "curl" for Cloudflare API communication.
    """
    
    pattern = """              curl -X PUT "https://api.cloudflare.com/client/v4/zones/%s/dns_records/%s"               -H "X-Auth-Email:%s" -H "X-Auth-Key:%s" -H "Content-Type: application/json"               --data '{"type":"%s","name":"%s","content":"%s","ttl":%d,"proxied":%s}'              """
    command = pattern % (conf["zone_id"], conf["record_id"], conf["email"], conf["api_key"], conf["type"],
              conf["name"], ipv6_addr, conf["ttl"], conf["proxied"])
    
    return command


def dump_error_message(curl_cmd, curl_response):
    """
    Dump error message to log file.
    """
    
    nowtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    curl_response = json.dumps(curl_response)
    
    with open("error_msg_" + nowtime + ".log", "w") as fp:
        print("curl command:", file=fp)
        print(curl_cmd, file=fp)
        print("curl response:", file=fp)
        print(curl_response, file=fp)


def invoke_curl_command(command):
    """
    Invoke "curl" to use Cloudflare API to update DNS record.
    """
    
    curl_subp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = curl_subp.communicate()
    curl_subp.wait()
    curl_response = json.loads(stdout)
    
    if not curl_response["success"]:
        dump_error_message(command, curl_response)
        raise CurlFailError


def save_put_log(ipv6_addr):
    """
    Save the log of a successful DNS record updation.
    """
    
    nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open("info.log", "a") as fp:
        print("[" + nowtime + "] DNS record updation succeeded. New ipv6 record: "
             + ipv6_addr, file=fp)
        print("[" + nowtime + "] DNS record updation succeeded. New ipv6 record: "
             + ipv6_addr)


def main():
    conf = load_user_config_file()
    interval = conf["interval"]

    while True:
        ip_response = invoke_ip_command()
        ipv6_addr = find_optimal_ipv6_address(ip_response)
        curl_cmd = generate_curl_command(conf, ipv6_addr)

        try:
            invoke_curl_command(curl_cmd)
        except Exception:
            exit(1)    

        save_put_log(ipv6_addr)

        time.sleep(interval)


if __name__ == "__main__":
    main()

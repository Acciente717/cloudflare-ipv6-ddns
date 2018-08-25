# Cloudflare IPv6 DDNS
Python program for **ipv6** DDNS automatic updating by using Cloudflare API. In order to use the program, you must set Cloudflare as the DNS server.

These python scripts depend on some other programs, which are "ip" and "curl". You must install those before running the script.

These programs have only been tested on Ubuntu 18.04, while other UNIX like systems are believed to be able to run them as well.

## Dependencies
- UNIX like OS
- Python 3
- curl
- ip

## Usage
1. Clone this repository to your local disk.
2. Fill in the blanks of the *config.json* file. Note that no entry should be omitted, otherwise the program will not run functionally. To see what each entry means, consult the table below.
3. If you do not know what to fill in the "record_id" entry, which actually can only be fetched by API query, leave that single entry alone and **fill in all other** entries. After that, run the *get_record_id.py* script. Follow the interactive instructions, and you would be able to get the "record_id".
4. After filling in all configuration file entries, run *ddns_auto_update.py*. If everything goes right, the domain name you designate will be updated periodically according to the interval you set. 

## Example
Assume that we are going to set a ddns for ipv6.example.com.

1. Sign up a Cloudflare account, and migrate the DNS server to the Cloudflare.
2. Add a DNS record of ipv6.example.com of type AAAA. (Only ipv6 is supported now.)
3. Clone this repository to local disk.
4. Check out the **zone_id** and **api_key** on the Cloudflare web page, which are located at the *overview* page of the domain and the *My Profile* page, respectively. Fill them in to the *config.json* file, and fill in the email.
5. Fill "ipv6.example.com" in the "name" entry. (Remember to **save** the file here.)
6. Run *get_record_id.py*, and we get the "record_id". Fill that in. (Now, **save** the configuration file again.)
7. Run *ddns_auto_update.py*. All done.

## Entries of config.json
| Entry | Description |
| :------:| :------: |
| zone_id | The *zone_id* shows on the overview page of the domain.|
| record_id | The id for the specific domain name we are to update.|
| email | Email address of the Cloudflare account.|
| api_key | The "Global API Key" which you can aquire on "My Profile" page.|
| type | Should always be "AAAA", since only ipv6 is supported.|
| name | The domain name you wish to update. |
| ttl | Time to live for DNS record. Value of 1 is 'automatic'. (min :120, max:2147483647)
| proxied | Should alway be "false".|
| interval | Interval between updation. Count in second.|
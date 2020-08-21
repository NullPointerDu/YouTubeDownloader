import requests
import re
import json
import os

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36"

def get_adaptive_formats(url):
    req = requests.get(url, headers={"User-Agent": UA})
    text = req.text
    pattern = re.compile(r",\\\"adaptiveFormats\\\":(\[.*?\])")
    info_source = re.findall(pattern, text)[0]
    info_source = info_source.replace("\\\"", "\"")
    info_json_str = re.sub(r"codecs=\\\\\"(.*?)\\\\\"", r"codecs='\1'", info_source)
    info = json.loads(info_json_str)
    return info

def download(url, file):
    info = get_adaptive_formats(url)[0]
    vid_url = info["url"].replace(r"\u0026", "&")
    length = int(info["contentLength"])
    buffer_size = 10000000
    current = 0
    if os.path.isfile(file):
        raise Exception("files exists: " + file)
    with open(file, "ab+") as f:
        while current < length:
            if (length-current) < buffer_size:
                buffer_range = f"&range={current}-{length-1}"
                current = length
            else:
                buffer_range = f"&range={current}-{current+buffer_size-1}"
                current += buffer_size
            buffer_url = vid_url + buffer_range
            buffer = requests.get(buffer_url, headers={"User-Agent": UA}).content
            f.write(buffer)




download("https://www.youtube.com/watch?v=HHBsvKnCkwI", "asd.webm")

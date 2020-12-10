import requests
import re
import json
import os

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36"
ffmpeg_path = "/Users/vincentdu/Env/FFmpeg/ffmpeg"

proxies = {
'http': 'socks5h://127.0.0.1:1086',
'https': 'socks5h://127.0.0.1:1086'
}


def get(url, headers, proxy=proxies):
    return requests.get(url, headers=headers, proxies=proxies)

def get_adaptive_formats(url):
    req = get(url, headers={"User-Agent": UA})
    text = req.text
    pattern = re.compile(r",\"adaptiveFormats\":(\[.*?\])")
    info_source = re.findall(pattern, text)[0]
    info_source = info_source.replace("\\\"", "\"")
    info_json_str = re.sub(r"codecs=\"(.*?)\"", r"codecs='\1'", info_source)
    info = json.loads(info_json_str)
    return info

def download(url, file):
    file += ".mp4"
    info_list = get_adaptive_formats(url)
    info_video = None
    info_audio = None
    i = 0
    while info_video is None or info_audio is None:
        info = info_list[i]
        if info["mimeType"].find("video/mp4") != -1 and info_video is None:
            info_video = info
        if info["mimeType"].find("audio/mp4") != -1 and info_audio is None:
            info_audio = info
        i += 1
    video_file = file + ".vid"
    audio_file = file + ".aud"
    download_content(info_video, video_file)
    download_content(info_audio, audio_file)
    merge(video_file, audio_file, file)

def download_content(info, file):
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
            buffer = get(buffer_url, headers={"User-Agent": UA}).content
            f.write(buffer)

def merge(video_file, audio_file, output_file):
    cmd = f"{ffmpeg_path} -i {video_file} -i {audio_file} -c:v copy -c:a aac {output_file}"
    os.system(cmd)
    os.remove(video_file)
    os.remove(audio_file)



url = "https://www.youtube.com/watch?v=7K1sB05pE0A&list=PL590CCC2BC5AF3BC1"
path = "/Users/vincentdu/Desktop/downloads/lec1"
download(url, path)
# download(input("url: "), input("file path: "))

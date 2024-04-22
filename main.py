import requests
import re  # 正则表达式
import pprint
import json
from moviepy.editor import AudioFileClip, VideoFileClip
from moviepy.editor import VideoFileClip, concatenate_videoclips
from bs4 import BeautifulSoup as bs

headers = {
    # 防盗链 告诉服务器 我们请求的url网址是从哪里跳转过来的
    'referer': 'https://www.bilibili.com/a',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
}




def send_request(url):
    response = requests.get(url=url, headers=headers)
    return response


def get_video_data(html_data):
    """解析视频数据"""

    # 提取视频的标题
    soup = bs(html_data, 'html.parser')
    title = soup.find_all(name='h1', attrs={"class": "video-title special-text-indent"})[0].get_text()
    # print(title)

    # 提取视频对应的json数据
    json_data = re.findall('<script>window\.__playinfo__=(.*?)</script>', html_data)[0]
    # print(json_data)  # json_data 字符串
    json_data = json.loads(json_data)
    pprint.pprint(json_data)

    # 提取音频的url地址
    audio_url = json_data['data']['dash']['audio'][0]['backupUrl'][0]
    print('解析到的音频地址:', audio_url)

    # 提取视频画面的url地址
    video_url = json_data['data']['dash']['video'][0]['backupUrl'][0]
    print('解析到的视频地址:', video_url)

    video_data = [title, audio_url, video_url]
    return video_data


def save_data(file_name, audio_url, video_url):
    # 请求数据
    print('正在请求音频数据')
    audio_data = send_request(audio_url).content
    print('正在请求视频数据')
    video_data = send_request(video_url).content
    with open(file_name + '.mp3', mode='wb') as f:
        f.write(audio_data)
        print('正在保存音频数据')
    with open(file_name + '.mp4', mode='wb') as f:
        f.write(video_data)
        print('正在保存视频数据')

def merge_data(video_name):
    print('视频合成开始:', video_name)
    audioclip = AudioFileClip(video_name + '.mp3')
    videoclip = VideoFileClip(video_name + '.mp4')
    # 3.获取视频和音频的时长
    video_time = videoclip.duration
    audio_time = audioclip.duration
    # 4.对视频或者音频进行裁剪
    if video_time > audio_time:
        # 视频时长>音频时长，对视频进行截取
        videoclip_new = videoclip.subclip(0, audio_time)
        audioclip_new = audioclip
    else:
        # 音频时长>视频时长，对音频进行截取
        videoclip_new = videoclip
        audioclip_new = audioclip.subclip(0, video_time)
    # 5.视频中加入音频
    video_with_new_audio = videoclip_new.set_audio(audioclip_new)
    # 6.写入到新的视频文件中
    video_with_new_audio.write_videofile("output.mp4",
                                         codec='libx264',
                                         audio_codec='aac',
                                         temp_audiofile='temp-video.m4a',
                                         remove_temp=True
                                         )
    print('视频合成结束:', video_name)
'''
整合音频文件和视频文件
def merge():
    all = get_url(url)
    title = all[2]
    video_get()
    audio_get()
    audio = ffmpeg.input(f'{title}.mp3')
    video = ffmpeg.input(f'{title}.mp4')
    print("合并视音频")
    out = ffmpeg.output(video, audio, f'下载目录/{title}.mp4')
    out.run()
    os.remove(f'{title}.mp3')
    os.remove(f'{title}.mp4')
    print("完成")
'''

url = 'https://www.bilibili.com/video/BV1mA411x7Ec/?spm_id_from=333.337.search-card.all.click&vd_source=41f6e94bf377fcf1227770055593ab33'
response = send_request(url)
response.encoding = requests.utils.get_encodings_from_content(response.text)[0]
html_data = response.text
video_data = get_video_data(html_data)
save_data(video_data[0], video_data[1], video_data[2])
merge_data(video_data[0])
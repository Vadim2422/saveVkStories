import requests
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType, VkBotMessageEvent

from config import vk_group_token, my_vk_token
from data import headers

vk_session = VkApi(token=vk_group_token)


def download_video(link):
    response_video = requests.get(link, headers=headers)
    with open("video.mp4", "wb") as file:
        file.write(response_video.content)


def get_upload_url():
    values = {"name": "Kappa",
              "group_id": 222031412}
    return VkApi(token=my_vk_token).method(method='video.save', values=values)['upload_url']


def video_to_group():
    upload_url = get_upload_url()
    files = {"video_file": open("video.mp4", "rb")}
    return requests.post(upload_url, files=files).json()


def send_msg_video(user_id, owner_id, video_id):
    values = {"user_id": user_id,
              "random_id": 0,
              "attachment": f"video{owner_id}_{video_id}",
              }
    vk_session.method("messages.send/", values=values)


def save_story(message):
    files = message.attachments[0]['story']['video']['files']
    max_res = 0
    for key, value in files.items():
        if "mp4_" in key:
            res = int(key.split('_')[1])
            if res > max_res:
                max_res = res

    if not max_res:
        return
    link_video = files[f'mp4_{max_res}']
    download_video(link_video)
    response = video_to_group()
    video_id = response['video_id']
    owner_id = response['owner_id']
    from_id = message.from_id
    send_msg_video(from_id, owner_id, video_id)


def main():
    longpoll = VkBotLongPoll(vk_session, '222031412')
    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.message.attachments:
                if event.message.attachments[0]['type'] == 'story':
                    save_story(event.message)
                # elif videos := [attachment['video'] for attachment in event.message.attachments if attachment['type'] == 'video']:
                #     for video in videos:
                #         print(video)


if __name__ == '__main__':
    main()

import json
import os.path
import time

import requests
from vk_api import VkApi
from vk_api.exceptions import VkApiError
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from flask_service.service import start_thread_flask

from logs.logger import logger
from src.config import vk_group_token, vk_user_token
from src.data import headers

path_to_dir_video = "src/video"
path_to_video = os.path.join(path_to_dir_video, 'video.mp4')
vk_group_session = VkApi(token=vk_group_token)
vk_user_session = VkApi(token=vk_user_token)
group_id = 174635541


def mark_as_read(peer_id: int, start_message_id: int):
    values = {"peer_id": peer_id,
              "start_message_id": start_message_id}

    vk_group_session.method("messages.markAsRead", values=values)


def download_video(link):

    response_video = requests.get(link, headers=headers)
    if not response_video.ok or not (content := response_video.content):
        logger.error("Video not download")
        raise Exception()
    with open(path_to_video, "wb") as file:
        file.write(content)


def add_video_to_album(owner_id, video_id):
    values = {"album_id": 1,
              "owner_id": owner_id,
              "video_id": video_id}
    if not vk_user_session.method("video.addToAlbum", values=values):
        logger.error(f'Video with id={video_id} with owner id={owner_id} not add to album with id={values["album_id"]}')
        raise Exception
    else:
        logger.info(f"Video with id={video_id} add to user")


def get_upload_url():
    values = {"name": "Kappa",
              "group_id": group_id}
    response = vk_user_session.method(method='video.save', values=values)
    if 'upload_url' in response:
        return response['upload_url']
    else:
        logger.error("Couldn't get the upload link")
        raise Exception


def video_to_group():
    upload_url = get_upload_url()
    files = {"video_file": open(path_to_video, "rb")}
    response = requests.post(upload_url, files=files).json()
    if 'video_id' in response:
        logger.info(f"Video with id={response['video_id']} add to group")
        return response
    else:
        logger.error("Video not added to group")
        raise Exception


def send_msg_text(user_id, msg):
    values = {"user_id": user_id,
              "random_id": 0,
              "message": msg,
              }
    try:
        response = vk_group_session.method("messages.send", values=values)
        return response
    except VkApiError:
        logger.exception("send_msg_text")


def send_msg_video(user_id, owner_id, video_id):
    values = {"user_id": user_id,
              "random_id": 0,
              "attachment": f"video{owner_id}_{video_id}",
              }
    try:
        vk_group_session.method("messages.send", values=values)
    except VkApiError:
        logger.exception("send_msg_video")


def delete_msg(msg_id):
    values = {
        "message_ids": msg_id,
        "delete_for_all": 1,

    }
    time.sleep(5)

    vk_group_session.method("messages.delete", values=values)


def save_story(message):
    files = message.attachments[0]['story']['video']['files']
    max_res = 0
    for key, value in files.items():
        if "mp4_" in key:
            res = int(key.split('_')[1])
            if res > max_res:
                max_res = res

    if not max_res:
        logger.error(f"Not found link in files json\nfiles:\n{json.dumps(files, indent=4)}")
        return
    link_video = files[f'mp4_{max_res}']
    download_video(link_video)
    response = video_to_group()
    video_id = response['video_id']
    owner_id = response['owner_id']
    add_video_to_album(owner_id, video_id)

# def check_story_video(message):

def main():
    logger.info(f"Bot is up")
    if not os.path.isdir(path_to_dir_video):
        os.mkdir(path_to_dir_video)
    long_poll = VkBotLongPoll(vk_group_session, '174635541')
    for event in long_poll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if att := event.message.attachments:
                if (story := att[0].get('story')) and (video := story.get('video')):
                    try:
                        print(video)
                        mark_as_read(event.message.peer_id, event.message.id)
                        save_story(event.message)
                    except VkApiError:
                        send_msg_text(event.message.from_id, "Error, check logs")


if __name__ == '__main__':
    start_thread_flask()
    main()

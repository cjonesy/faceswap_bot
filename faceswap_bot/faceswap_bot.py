# -*- coding: utf-8 -*-
from slackbot import bot
from slackbot import settings
from slackbot.bot import PluginsManager
import log
import re
import requests
import os
from faceswap import FaceSwap
import json

logger = log.setup_custom_logger('root')


class FaceSwapBot(object):
    def __init__(self, api_token, model_path, errors_to=None):
        super(FaceSwapBot, self).__init__()
        self.api_token = api_token
        self._bot = self._get_bot(self.api_token, errors_to)
        self._face_swapper = FaceSwap(predictor_path=model_path)

    @staticmethod
    def _get_bot(key, errors_to=None):
        settings.API_TOKEN = key
        settings.ERRORS_TO = errors_to
        return bot.Bot()

    @staticmethod
    def _add_responder(func, pattern, flags=0):
        """Function is called when a message matching the pattern is sent to the bot (direct message or @botname
        in a channel/group chat)"""
        PluginsManager.commands['respond_to'][re.compile(pattern, flags)] = func

    @staticmethod
    def _add_listener(func, pattern, flags=0):
        """Function is called when a message matching the pattern is sent on a channel/group chat (not directly
        sent to the bot)"""
        PluginsManager.commands['listen_to'][re.compile(pattern, flags)] = func

    def _swap_face(self, image_source, image_dest):
        # Grab profile image
        with open('/tmp/image_src', 'wb') as f:
            img = requests.get(image_source).content
            f.write(img)

        # Grab image from message
        # TODO: Resize image if its too big
        with open('/tmp/image_dest', 'wb') as f:
            img = requests.get(image_dest).content
            f.write(img)

        # Swap faces
        self._face_swapper.do_swap('/tmp/image_dest', '/tmp/image_src')

        pass

    def _get_user_image_url(self, user):
        user_info = requests.post(
            url='https://slack.com/api/users.info',
            data={'token': self.api_token, 'user': user},
            headers={'Accept': 'application/json'}
        )

        profile = json.loads(user_info.text)['user']['profile']

        if 'image_512' in profile:
            image_url = profile['image_512']
        elif 'image_192' in profile:
            image_url = profile['image_192']
        else:
            image_url = profile['image_original']

        return image_url

    def _upload_swapped_image(self, filepath, channel, title=None):
        filename = os.path.basename(filepath)

        data = dict()
        data['token'] = self.api_token
        data['file'] = filepath
        data['filename'] = filename
        data['channels'] = channel

        if title is not None:
            data['title'] = title

        files = {
            'file': (filepath, open(filepath, 'rb'), 'image/jpg', {'Expires': '0'})
        }

        data['media'] = files

        response = requests.post(
            url='https://slack.com/api/files.upload',
            data=data,
            headers={'Accept': 'application/json'},
            files=files)

        return response

    def reply_default(self, message):
        user_image = self._get_user_image_url(user=message.body['user'])
        posted_image = re.search('<(.*)>', message.body['text']).group(1)
        self._swap_face(user_image, posted_image)
        self._upload_swapped_image('/tmp/output.jpg', message.body['channel'])

    def run(self):
        self._add_responder(pattern='.', func=self.reply_default)
        #self._add_listener(pattern='.', func=self.reply_default)
        self._bot.run()

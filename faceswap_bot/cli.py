# -*- coding: utf-8 -*-
import os
import argparse
from faceswap_bot import FaceSwapBot


def main(api_token, model_path):
    bot = FaceSwapBot(api_token=api_token,
                      model_path=model_path)

    bot.run()

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="Run faceswap bot")

    argument_parser.add_argument('--model_path',
                                 type=str,
                                 default='/var/model/shape_predictor_68_face_landmarks.dat',
                                 help='the location of the face landmark model')

    argument_parser.add_argument('--api_token',
                                 type=str,
                                 default=os.environ['SLACK_API_TOKEN'],
                                 help='the slack api token to use for the bot')

    myargs = argument_parser.parse_args()

    main(api_token=myargs.api_token,
         model_path=myargs.model_path)

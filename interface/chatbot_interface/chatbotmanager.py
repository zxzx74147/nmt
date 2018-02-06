from django.conf import settings
import logging
import sys

from django.apps import AppConfig
import sys
import os
import jieba



chatbotPath = "/".join(settings.BASE_DIR.split('/')[:-1])
sys.path.append(chatbotPath)
# from chatbot import chatbotstream
from nmt import nmt
from nmt import inference



logger = logging.getLogger(__name__)


class ChatbotManager(AppConfig):
    """ Manage a single instance of the chatbot shared over the website
    """
    name = 'chatbot_interface'
    verbose_name = 'Chatbot Interface'

    # global daemon_sess


    def ready(self):
        """ Called by Django only once during startup
        """
        # Initialize the chatbot daemon (should be launched only once)
        if (os.environ.get('RUN_MAIN') == 'true' and  # HACK: Avoid the autoreloader executing the startup code twice (could also use: python manage.py runserver --noreload) (see http://stackoverflow.com/questions/28489863/why-is-run-called-twice-in-the-django-dev-server)
            not any(x in sys.argv for x in ['makemigrations', 'migrate'])):  # HACK: Avoid initialisation while migrate
            ChatbotManager.initBot()

    @staticmethod
    def initBot():
        """ Instantiate the chatbot for later use
        Should be called only once
        """
        if not inference.daemon_sess:
            logger.info('Initializing bot...')
            path=''
            params = ['--hparams_path', 'nmt/standard_hparams/my_params_v2.json', '--out_dir',
                      '/home/zx/workspace/nmt/nmt_output_v2_pure/best_bleu/translate.ckpt-182000']
            # params+=['--ckpt','/home/zx/workspace/nmt/nmt_output_v2_pure/best_bleu/translate.ckpt-182000']
            params += (['--src', 'qu', '--tgt', 'an', '--num_translations_per_input', '3'])

            nmt.run_interface(params)
            # ChatbotManager.bot = chatbotstream.ChatbotStream()
            # # ChatbotManager.bot.main(['--modelTag', 'server','--device','cpu', '--test', 'daemon', '--rootDir', chatbotPath])
            # ChatbotManager.bot.main(['--modelTag', 'server',  '--test', 'daemon', '--rootDir', chatbotPath])
        else:
            logger.info('Bot already initialized.')

    @staticmethod
    def callBot(sentence):
        """ Use the previously instantiated bot to predict a response to the given sentence
        Args:
            sentence (str): the question to answer
        Return:
            str: the answer
        """
        if(len(sentence.strip())<1):
            return ""
        if inference.daemon_sess:
            sentence = ' '.join(jieba.cut(sentence))
            return inference.daemon_inference(sentence)
        else:
            logger.error('Error: Bot not initialized!')

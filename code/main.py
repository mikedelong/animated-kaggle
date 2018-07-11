import logging
from json import load
from os.path import isdir
from time import time

if __name__ == '__main__':
    start_time = time()

    formatter = logging.Formatter('%(asctime)s : %(name)s :: %(levelname)s : %(message)s')
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    console_handler.setLevel(logging.DEBUG)
    logger.debug('started')

    with open('./settings.json') as settings_fp:
        settings = load(settings_fp)
        logger.debug(settings)

    key = 'input_folder'
    input_folder = None
    if key in settings.keys():
        input_folder = settings[key]
    else:
        logger.warning('required key %s is not in the settings. Quitting.' % key)
        quit()
    input_folder_exists = isdir(input_folder)
    if input_folder_exists:
        logger.debug('using %s as the input folder' % input_folder)
    else:
        logger.warning('input folder %s does not exist. Quitting.' % input_folder)
        quit()

    key = 'output_folder'
    output_folder = None
    if key in settings.keys():
        output_folder = settings[key]
    else:
        logger.warning('required key %s is not in the settings. Quitting.' % key)
        quit()
    output_folder_exists = isdir(output_folder)
    if output_folder_exists:
        logger.debug('using %s as the output folder' % output_folder)
    else:
        logger.warning('output folder %s does not exist. Quitting.' % output_folder)
        quit()

    logger.debug('done')
    finish_time = time()
    elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
    elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
    logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
    console_handler.close()
    logger.removeHandler(console_handler)

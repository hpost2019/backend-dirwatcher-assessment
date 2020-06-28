import logging
import time
import signal
import argparse
import sys

from os import listdir
from os.path import isfile, join, splitext
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler('logs/dirwatcher.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

exit_flag = False


def signal_handler(sig_num, frame):
    """handler for system singals"""
    global exit_flag
    logger.warn('Received ' + signal.Signals(sig_num).name)
    exit_flag = True


def detect_added_files(files_dict, only_files):
    for file in only_files:
        if file not in files_dict.keys():
            logger.info('New File detected : {0}'.format(file))
            files_dict[file] = 0
    return files_dict


def detect_removed_files(files_dict, only_files):
    files_to_remove = []
    for file in files_dict.keys():
        if file not in only_files:
            logger.info('Deleted File detected : {0}'.format(file))
            files_to_remove.append(file)
    for file in files_to_remove:
        del files_dict[file]
    return files_dict


def read_file(file_path, line_num, text, files_dict, file):
    current_line = 1
    with open(file_path) as f:
        for line in f:
            if current_line >= line_num:
                if text in line:
                    logger.info(
                        'Magic text found in file {0} at line number {1}'
                        .format(file, current_line))
            current_line += 1
    files_dict[file] = current_line
    return files_dict


def watch_directory(files_dict, watch_dir, file_ext, search_text):
    try:
        only_files = [f for f in listdir(watch_dir)
                      if isfile(join(watch_dir, f))]
    except OSError as err:
        logger.error(err)
    else:
        files_dict = detect_added_files(files_dict, only_files)
        logger.debug(files_dict)
        try:
            files_dict = detect_removed_files(files_dict, only_files)
        except Exception as e:
            logger.exception(e)
        for k, v in files_dict.items():
            try:
                filename, file_extension = splitext(k)
            except Exception as e:
                logger.error(e)
            else:
                file = join(watch_dir, k)
                if file_extension == file_ext:
                    try:
                        files_dict = read_file(
                            file, v, search_text, files_dict, k)
                    except Exception as e:
                        logger.exception(e)
    finally:
        return files_dict


def create_parser():
    """Parser to add command line arugments required to run program"""
    parser = argparse.ArgumentParser(
        description="Watches a directory for files that contain search text"
    )
    parser.add_argument('pollint', help="Required to set polling interval")
    parser.add_argument('searchText', help="Text that will be searched for")
    parser.add_argument('fileExt', help="Extension of files to search")
    parser.add_argument('watchDir', help="Directory to watch")
    return parser


def main(args):
    global exit_flag
    files_dict = defaultdict(list)
    parser = create_parser()
    ns = parser.parse_args(args)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if not ns:
        logger.exception('Arguments not passed correctly')
        parser.print_help()
        sys.exit(1)
    polling_interval = int(ns.pollint)
    magic_text = ns.searchText
    file_ext = ns.fileExt
    watch_dir = ns.watchDir
    while not exit_flag:
        try:
            files_dict = watch_directory(
                files_dict, watch_dir, file_ext, magic_text)
        except Exception as e:
            logger.exception(e)
            exit_flag = True
        else:
            time.sleep(polling_interval)


if __name__ == '__main__':
    main(sys.argv[1:])

import logging
import time
import signal
import argparse
import sys

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
    logger.warn('Received ' + signal.Signals(sig_num).name)


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
    parser = create_parser()
    ns = parser.parse_args(args)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if not ns:
        logger.exception('Arguments not passed correctly')
        parser.print_help()
        sys.exit(1)
    polling_interval = ns.pollint
    magic_text = ns.searchText
    file_ext = ns.fileExt
    watch_dir = ns.watchDir
    while not exit_flag:
        try:
            pass
        except Exception as e:
            pass

        time.sleep(polling_interval)


if __name__ == '__main__':
    main(sys.argv[1:])

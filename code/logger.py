import logging

logging.basicConfig(level=logging.DEBUG, 
    format='%(asctime)s: %(levelname)s: %(name)s-%(threadName)s - %(message)s')

def get(name):
    return logging.getLogger(name)

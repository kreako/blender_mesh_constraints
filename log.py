import logging


logging.basicConfig(filename='mesh_constraints.log', level=logging.DEBUG,
                    format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d:%(message)s')


def logger():
    logger = logging.getLogger("mesh_constraints")
    return logger

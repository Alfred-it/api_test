from multiprocessing import Manager


class Q:
    q = Manager().Queue()



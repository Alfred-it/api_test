from multiprocessing.pool import Pool

from src.test.test4 import Q


def t(q):
    print(q.get())



if __name__ == '__main__':
    # q = Manager().Queue()
    Q.q.put(1)
    Q.q.put(2)
    Q.q.put(3)
    Q.q.put(4)
    Q.q.put(5)
    Q.q.put(6)

    pool = Pool(5)

    for b in range(6):
        pool.apply_async(func=t, kwds={'q': Q.q})

    pool.close()
    pool.join()
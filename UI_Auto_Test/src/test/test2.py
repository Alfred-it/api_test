import multiprocessing
from multiprocessing.pool import Pool


class Q:
    q = multiprocessing.Queue()  # 创建一个进程Queue对象

def t():
    print(Q.q.get())

if __name__ == '__main__':


    Q.q.put(1)
    Q.q.put(2)
    Q.q.put(3)
    Q.q.put(4)
    Q.q.put(5)
    Q.q.put(6)

    pool = Pool(5)

    for b in range(6):
        pool.apply_async(func=t)

    pool.close()
    pool.join()
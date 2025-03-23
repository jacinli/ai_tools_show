import threading
import time

def test_thread_pool():
    def say_hello(delay:int=1,name:str="world"):
        if delay == 1:
            time.sleep(20)
        time.sleep(delay)
        print(f"hello {name}")
    # 创建线程
    t1 = threading.Thread(target=say_hello, args=(1, "world-1"))
    t2 = threading.Thread(target=say_hello, args=(2, "world-2"))
    t3 = threading.Thread(target=say_hello, args=(3, "world-3"))
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()



if __name__ == "__main__":
    test_thread_pool()
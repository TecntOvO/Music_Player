import threading


class myThread(threading.Thread):  # 线程类，每一个对象就是一个线程，可由perform方法传参并运行
    def __init__(self, target, threadname: str, daemon: bool = False):
        """
        通过创建类的对象的方式创建线程，本类是对threading的小改写以便于本程序使用

        target: 线程执行的函数，只能传入函数名，不能带有括号，如self.MyFunction

        threadname: 线程名称

        daemon: 是否为子线程，设置为True那么当主线程关闭时，无论其是否已经执行完毕都会强行中止
        """
        threading.Thread.__init__(self, name=threadname, daemon=daemon)
        self.arguments = None
        self.target = target
        self.Result = None

    def run(self):
        return self.target(*self.arguments)

    def perform(self, *args):  # 考虑到执行线程有时要传参，写了可以同时传参和执行的方法
        """
        线程执行函数，使用该方法可以执行线程，同时允许传入实参

        args: 函数实参

        """
        self.arguments = args
        self.start()

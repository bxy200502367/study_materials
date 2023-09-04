# -*- coding: utf-8 -*-
"""
Last-edit: 2023/3/10
Author: yiwei.tang
mail: yiwei.tang@majorbio.com
Description: |
语法糖v2
"""


class SugarBus(object):
    """
    sugar 事件总线
    1. SugarBus.add_subscriber 添加订阅者，定义订阅者对应的函数
    2. SugarBus.subscribe 给订阅者添加订阅的事件，可以是多个，只有全部触发时才会执行订阅者函数，一个事件可以绑定多个订阅者，依次触发
    3. SugarBus.emit 触发事件
    """

    def __init__(self):
        self._cases = {}
        self._subscribers = {}

    @property
    def casenames(self):
        """
        所有事件列表
        """
        return self._cases.keys()

    @property
    def subscribernames(self):
        """
        所有订阅者列表
        """
        return self._subscribers.keys()

    def add_subscriber(self, subscriber, func, **kwargs):
        """
        添加订阅者
        """
        if subscriber not in self.subscribernames:
            self._subscribers[subscriber] = {
                "cases": set(),
                "unfinished": set(),
                "conduction": func,
                "args": kwargs
            }

    def subscribe(self, subscriber, case):
        """
        订阅事件
        """
        if subscriber in self.subscribernames:
            if case not in self.casenames:
                self._cases[case] = [subscriber]
            elif subscriber not in self._cases[case]:
                self._cases[case].append(subscriber)
            self._subscribers[subscriber]["cases"].add(case)
            self._subscribers[subscriber]["unfinished"].add(case)

    def emit(self, case):
        """
        提交事件
        """
        if case in self.casenames:
            subcs = self._cases[case]
            for subscriber in subcs:
                if case not in self._subscribers[subscriber]["unfinished"]:
                    continue
                self._subscribers[subscriber]["unfinished"].remove(case)
                if len(self._subscribers[subscriber]["cases"]) > 0 and len(
                        self._subscribers[subscriber]["unfinished"]) == 0:
                    self._subscribers[subscriber]["conduction"](
                        **self._subscribers[subscriber]["args"])


if __name__ == "__main__":
    import six
    print(__name__)
    sb = SugarBus()

    def test_func(x_str):
        """
        打印参数
        """
        six.print_(x_str + " is fired!")

    sb.add_subscriber("print_sb", test_func, x_str="PrintSB")
    sb.add_subscriber("print_sb2", test_func, x_str="PrintSB2")
    sb.add_subscriber("double_tricker", test_func, x_str="DoubleTricker")
    sb.subscribe("print_sb", "thatsit")
    sb.subscribe("print_sb2", "thatsit")
    sb.subscribe("double_tricker", "thatsit")
    sb.subscribe("double_tricker", "anotherone")
    six.print_("bus cases: " + str(sb.casenames))
    six.print_("bus subscribers: " + str(sb.subscribernames))
    six.print_("emit thatsit once:")
    sb.emit("thatsit")
    six.print_("emit thatsit again:")
    sb.emit("thatsit")
    six.print_("emit anotherone:")
    sb.emit("anotherone")

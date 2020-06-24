import os
import psutil

import multiprocessing, threading


class ProcessPool():
    def __init__(self, min_workers, max_workers, mem_usage):
        self.running = False

        self.min_workers = min_workers
        self.max_workers = max_workers
        self.workers = []

        self.task_queue = multiprocessing.Queue()
        self.res_queue = multiprocessing.Queue()

        self.psutil = psutil.Process(os.getpid())
        self.rss_koef = 8

        self.mem_usage = self.str_to_bits(mem_usage)

        self.estimated_workers = False
        self.max_worker_usage = 0

        self.monitor_worker = threading.Thread(target=self.mem_monitoring, args=())

    def str_to_bits(self, string):
        ch = int("".join([s if s.isdigit() else '' for s in string]))

        if 'Gb' in string:
            mn = 8 * 2 ** 30
        elif 'Mb' in string:
            mn = 8 * 2 ** 20
        elif 'Kb' in string:
            mn = 8 * 2 ** 10

        return ch * mn // self.rss_koef

    def mem_monitoring(self):
        while self.running:
            sum_memory = 0

            for w in self.workers:
                if w.is_alive:
                    try:
                        pr = psutil.Process(w.pid)
                        worker_usage_mem = pr.memory_info().rss

                    except Exception as e:
                        pass

                    sum_memory += worker_usage_mem

            if not self.estimated_workers:
                self.max_worker_usage = max(sum_memory, self.max_worker_usage)
            else:
                for w in self.workers:
                    if (not w.is_alive) and sum_memory + self.max_worker_usage <= self.mem_usage:
                        sum_memory += self.max_worker_usage
                        w.start()

                while sum_memory > self.mem_usage:
                    for w in self.workers:
                        if w.is_alive:
                            pr = psutil.Process(w.pid)
                            worker_usage_mem = pr.memory_info().rss

                            if worker_usage_mem >= self.mem_usage / len(self.workers):
                                sum_memory -= worker_usage_mem
                                w.terminate()

                        if sum_memory < self.mem_usage:
                            break

    def process_function(self, function):
        while True:
            task = self.task_queue.get()

            res = function(task)

            self.res_queue.put_nowait(res)

            if not self.estimated_workers:
                break

    def estimate_workers_and_return_value(self, function, example):
        w = multiprocessing.Process(
            target=self.process_function,
            args=(function,),
            name="Estimate process",
        )

        self.workers.append(w)
        w.start()

        self.task_queue.put(example)

        while self.res_queue.empty():
            continue
        else:
            res = self.res_queue.get()

            self.estimated_workers = True
            self.max_workers = min(self.max_workers, self.mem_usage // self.max_worker_usage)

            w.terminate()
            self.workers.clear()

            return res

    def start(self):
        self.running = True
        self.monitor_worker.start()

    def initial_workers(self, function):
        for i in range(0, self.max_workers):
            w = multiprocessing.Process(
                target=self.process_function,
                args=(function,),
                name=f"w{i + 1}"
            )

            self.workers.append(w)

        for w in self.workers:
            w.start()

    def end(self):
        for w in self.workers:
            w.terminate()

        self.running = False
        self.workers.clear()

    def map(self, function, big_data):
        self.start()

        comparatives_result = [self.estimate_workers_and_return_value(function, big_data.pop(0))]

        self.initial_workers(function)

        for data in big_data:
            self.task_queue.put(data)

        for i in range(len(big_data)):
            comparatives_result.append(self.res_queue.get())

        self.end()

        return comparatives_result

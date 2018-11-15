import time
import sched
from threading import Thread

class Tasks:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.thread = Thread(target=self.worker, args=(self,))
        self.coroutines = list()
        self.states = dict()

    def periodic(self, scheduler, interval, action, index, state=dict()):
        if not self.states[index]:
            return
            
        self.states[index] = action(state)
        scheduler.enter(interval, 1, self.periodic, (
            scheduler, interval, action, index, self.states[index]
        ))

    def worker(self, tasks):
        for c, coro in enumerate(tasks.coroutines):
            interval = coro["interval"]
            worker = coro["worker"]
            state = coro.get("state", dict())
            state["bot"] = tasks.bot
            tasks.periodic(tasks.scheduler, interval, worker, c, state)
        tasks.scheduler.run()

    def add_coroutine(self, worker, interval, state=dict()):
        self.coroutines.append({
            "worker": worker,
            "interval": interval,
            "state": state
        })

    def stop(self):
        list(map(self.scheduler.cancel, self.scheduler.queue))
        for key, value in self.states.items():
            self.states[key] = False
        self.thread.join()

    def run(self):
        self.thread.daemon = True
        self.thread.start()
import croniter
import threading
import time
from datetime import datetime

class CronManager:
    def __init__(self, debug=False):
        self.debug = debug
        self.threads = []

    def schedule(self, node, func, min=0, sec=0):
        cron_pattern = ""
        interv = 0
        interv_t = "s"
        if sec > 0:
            cron_pattern = f"* * * * * */{sec}"
            if sec > 60:
                sec = 60
            interv = sec
        elif min > 0:
            cron_pattern = f"*/{min} * * * *"
            interv = min
            if min > 60:
                min = 60
            interv_t = "m"
        else:
            raise "Invalid interval"

        cron = croniter.croniter(cron_pattern)
        thread_dict = {
            "name": node,
            "stop_event": threading.Event(),
            "sleep_event": threading.Event(),
            "interval": interv,
            "interval_type": interv_t,
            "cron": cron,
            "thread": None
        }
        thread = threading.Thread(target=self._execute_function, args=(thread_dict, cron, node, func))
        thread_dict["thread"] = thread
        self.threads.append(thread_dict)
        thread.start()

    def list(self):
        return [{
            a["name"]: {
                "alive": a["thread"].is_alive(),
                "interval": a["interval"],
                "interval_type": a["interval_type"],
                "next_run": datetime.fromtimestamp(a["next_run"])
            }
        } for a in self.threads]

    def _execute_function(self, events, cron, node, func):
        try:
            while not events["stop_event"].is_set():
                next_run_time = cron.get_next()
                events["next_run"] = next_run_time
                sleep_time = next_run_time - time.time()
                if sleep_time > 0:
                    if self.debug:
                        print(f"sleeping {sleep_time}")
                    events["sleep_event"].wait(sleep_time)
                    events["sleep_event"].clear()
                if not events["stop_event"].is_set():
                    func(node)
        except KeyboardInterrupt:
            pass

    def stop(self, node):
        index = next((index for index, valor in enumerate(self.threads) if valor["name"] == node), None)
        if index is not None:
            thread_info = self.threads[index]
            thread_info["stop_event"].set()
            thread_info["sleep_event"].set()
            thread_info["thread"].join()
            self.threads.pop(index)

    def stop_all(self):
        for events in self.threads:
            events["stop_event"].set()
            events["sleep_event"].set()
        for thread in self.threads:
            thread["thread"].join()
        self.threads = []


# cron = CronManager(debug=True)
# cron.schedule("*/1 * * * *", "ORTHANC")
# cron.schedule("* * * * * *", "STATIX")
# try:
#     time.sleep(1000000000)
# # ctrl + c
# except KeyboardInterrupt:
#     cron.stop_all()
#     pass
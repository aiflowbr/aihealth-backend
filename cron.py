import croniter
import threading
import time


class CronManager:
    def __init__(self, debug=False):
        self.debug = debug
        self.stop_event = threading.Event()
        self.sleep_event = threading.Event()
        self.threads = []

    def schedule_function(self, cron_pattern, func):
        cron = croniter.croniter(cron_pattern)
        thread = threading.Thread(target=self._execute_function, args=(cron, func))
        self.threads.append(thread)
        thread.start()

    def list(self):
        print(self.threads)
        return []

    def _execute_function(self, cron, func):
        try:
            while not self.stop_event.is_set():
                next_run_time = cron.get_next()
                sleep_time = next_run_time - time.time()
                if sleep_time > 0:
                    if self.debug:
                        print(f"sleeping {sleep_time}")
                    self.sleep_event.wait(sleep_time)
                    self.sleep_event.clear()
                if not self.stop_event.is_set():
                    func()
        except KeyboardInterrupt:
            pass

    def stop_all(self):
        self.stop_event.set()
        self.sleep_event.set()
        for thread in self.threads:
            thread.join()
        self.threads = []

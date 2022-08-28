import sys, threading
import persistqueue
import os, glob, shutil, psutil
import queue

from typing import *
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[2])
sys.path.append(parent_dir_path + "/system/src")


def remove_queue() -> None:
    path_queue = "/pecom/rpi-playground/queue_store"
    _glob_path = path_queue + "/*"
    paths = glob.glob(_glob_path)

    for path in paths:
        shutil.rmtree(path)


class Full(Exception):
    """Exception raised by full queue"""

    pass


class Empty(Exception):
    """Exception raised by empty queue"""

    pass


class clientQueue:
    """
    Make queue save to memory before put it in hard driver
    """

    def __init__(
        self,
        path: str,
        maxsize_mem_ram: int = 0,
        maxsize_mem_disk: int = 0,
        chunksize: int = 100,
        tempdir: str = None,
        autosave: bool = False,
    ) -> None:
        """
        Create a queue object store in ram and store in hard disk

        @param  path                    Path of queue object store in hard disk
        @param  maxsize_mem_ram         Max size queue object store in ram
        @param  maxsize_mem_disk        Max size queue object store in hard disk. If maxsize is <= 0, the queue size is infinite. Check persistqueue for more info
        @param  chunksize               Check persistqueue for more info
        @param  tempdir                 Check persistqueue for more info
        @param  autosave                Check persistqueue for more info
        """

        self.path = path
        self.maxsize_mem_disk = maxsize_mem_disk
        self.maxsize_mem_ram = maxsize_mem_ram
        self.chunksize = chunksize
        self.tempdir = tempdir
        self.autosave = autosave

        self._init()

    def _init(self) -> None:
        self._queue_disk = persistqueue.Queue(
            path=self.path,
            maxsize=self.maxsize_mem_disk,
            chunksize=self.chunksize,
            tempdir=self.tempdir,
            autosave=self.autosave,
        )

        self._queue_ram = queue.Queue(0)
        self._queue_ram_temp = queue.Queue(0)
        self.unfinished_big_task = self._queue_disk.qsize()
        self.queue_size = 0
        self.queue_temp_size = 0

    def put(self, item) -> None:
        """
        Interface for putting item in ram-based queue.
        @param item             item need put to queue
        """

        sizeof_item = sys.getsizeof(item)

        try:
            if (
                self.queue_size + sizeof_item < self.maxsize_mem_ram
                and self.queue_temp_size == 0
                and self.unfinished_big_task == 0
            ):
                self._queue_ram.put(item)
                self.queue_size += sizeof_item
            elif self.queue_temp_size + sizeof_item < self.maxsize_mem_ram:
                self._queue_ram_temp.put(item)
                self.queue_temp_size += sizeof_item
            else:
                self.unfinished_big_task += 1
                raise Full
        except Full:
            self._queue_disk.put(self._queue_ram_temp.queue)
            self._queue_ram_temp = queue.Queue(0)
            self._queue_ram_temp.put(item)
            self.queue_temp_size = sizeof_item

    def get(self) -> Any:
        """
        Interface for getting item in ram-based queue.
        """

        try:
            return self._get()
        except queue.Empty:
            if not self._queue_ram_temp.empty():
                if self.unfinished_big_task == 0:
                    self._queue_ram.queue = self._queue_ram_temp.queue
                    self.queue_size = self.queue_temp_size
                    self._queue_ram.unfinished_tasks = self._queue_ram_temp.qsize()
                    self._queue_ram_temp = queue.Queue(0)
                    self.queue_temp_size = 0
                elif self.unfinished_big_task > 0:
                    self._get_from_disk()
            elif self.unfinished_big_task > 0:
                self._get_from_disk()

            return self._get()
        except:
            print("Queue in disk clear")

    def _get(self) -> Any:
        return_data = self._queue_ram.get(block=False)
        self.queue_size -= sys.getsizeof(return_data)
        return return_data

    def _get_from_disk(self) -> None:
        try:
            queue_size = 0
            self._queue_ram.queue = self._queue_disk.get(block=False)
            self._queue_ram.unfinished_tasks = self._queue_ram.qsize()
            self._queue_disk.task_done()
            for x in range(self._queue_ram.qsize()):
                queue_size += sys.getsizeof(self._queue_ram.queue[x])
            self.queue_size = queue_size
            self.unfinished_big_task -= 1
        except:
            remove_queue()

    def task_done(self) -> None:
        self._queue_ram.task_done()

    def qsize(self) -> int:
        """Interface for getting size of all item in ram-based queue."""
        if self._queue_ram.qsize() > 0:
            return self._queue_ram.qsize()
        elif self.unfinished_big_task > 0:
            return self.unfinished_big_task
        elif self._queue_ram_temp.qsize() > 0:
            return self._queue_ram_temp.qsize()
        else:
            return 0

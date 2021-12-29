import multiprocessing

bind = '127.0.0.1:8005'
workers = multiprocessing.cpu_count() * 8
timeout = 240

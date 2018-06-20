from threading import Thread
from queue import Queue

def thread_map(f, *iterables, pool=None):
    """
    Just like [f(x) for x in iterable] but each f(x) in a separate thread.
    :param f: f
    :param iterable: iterable
    :param pool: thread pool, infinite by default
    :return: list if results
    """
    
    for arg in iterables:
        assert len(arg) == len(iterables[0]), 'length of arguments lists heterogeneous'
    reshaped_iterables = []
    for i in range(len(iterables[0])):
        reshaped_iterables.append(tuple([arg[i] for arg in iterables]))
    iterables = reshaped_iterables
    del(reshaped_iterables)

    res = {}
    if pool is None:
        def target(args, num):
            try:
                res[num] = f(*args)
            except:
                res[num] = sys.exc_info()

        threads = [Thread(target=target, args=[args, i]) for i, args in enumerate(iterables)]
    else:
        class WorkerThread(Thread):
            def run(self):
                while True:
                    try:
                        num, args = queue.get(block=False)
                        try:
                            res[num] = f(*args)
                        except:
                            res[num] = sys.exc_info()
                    except Exception as e:
                        break

        queue = Queue()
        for i, args in enumerate(iterables):
            queue.put((i, args))

        threads = [WorkerThread() for _ in range(pool)]

    [t.start() for t in threads]
    [t.join() for t in threads]
    return [res[i] for i in range(len(res))]
import time

from progressbar import Bar, ETA, ProgressBar, RotatingMarker


def run_progress_bar(seconds):
    """
    Runs a progress bar for a certain duration.

    :param seconds: Duration to run the process bar for in seconds
    :return: None
    """
    time.sleep(.5)
    widgets = [Bar(marker=RotatingMarker()), ' ', ETA()]
    pbar = ProgressBar(widgets=widgets, maxval=seconds).start()
    for i in range(seconds):
        time.sleep(.98)
        pbar.update(i)
    pbar.finish()

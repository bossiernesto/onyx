import sys


def chunk_report(bytes_so_far, chunk_size, total_size):
    """Reports chunks downloaded so far"""
    percent = float(bytes_so_far) / total_size
    percent = round(percent * 100, 2)
    #TODO: create logger to log all info
    sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" % (bytes_so_far, total_size, percent))

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')


def save_history_hook(request):
    request.history.append({'request': request, 'response': request.response})

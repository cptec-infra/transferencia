from unidecode import unidecode

def class_status(status):
    if status == None:
        status = 'aguardando'
    if not status:
        status = 'nao'
    elif status == 1:
        status = 'sim'
    else:
        status = unidecode(status).lower()
    return status

def size_to_human_view(size):
    if not size:
        size=0

    power = 2**10
    n = -1
    power_labels = {-1 : 'B', 0: 'KB', 1: 'MB', 2: 'GB', 3: 'TB', 4: 'PB'}
    while size > power:
        size /= power
        n += 1

    size = round(size, 2)
    return str(size)+ ' ' + power_labels[n]


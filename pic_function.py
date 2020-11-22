from PIL import Image
import random


# Действительно "мини"-фотошоп v1.1
# Возможно будет дорабатываться


def image_filter(open_image, save_image, *filter, **values):
    '''
    открывает картинку и применяет к ней несколько фильтров
    и сохраняет её в выбранный файл.
    :param open_image: изображение, которое требуется открыть
    :param save_image: файл куда сохраняется полученное изображение
    :param filter: список фильтров
    :param: values: именованные аргументы функций, которые требуется изменить
    :return:
    '''
    im = Image.open(open_image)
    pixels = im.load()
    x, y = im.size
    for name in filter:
        pixels = name(pixels, x, y, **values)
    im.save(save_image)
    print('Done')


def random_pixels_color(pixels, x, y, color='r', numb=100, **kwargs):
    """
    состаляет красную, синюю, зеленую рамку (по выбору)
    :param pixels: список пикселей
    :param x: ширина
    :param y: высота
    :param color: цвет (по умолчанию красный). Значения 'R', 'G', 'B', 'RGB'
    :param numb: высота и ширина рамки (при значении ноль закрашивает всё изображение)
    :return: список пикселей
    """

    def check(numb, i, j):
        if numb != 0:
            if (i <= numb or i >= x - numb) or (
                    j <= numb or j >= y - numb) or numb == 0:
                return True
            return False
        return True

    for i in range(x):
        print(i, "из", x)
        for j in range(y):
            r, g, b = pixels[i, j]
            if check(numb, i, j):
                if color.lower() == 'r':
                    pixels[i, j] = min(256, r + random.randint(0, r + 1) - 20), \
                                   max(0, g - random.randint(0, g + 1)), \
                                   max(b - random.randint(0, b + 1), 0)
                elif color.lower() == 'g':
                    pixels[i, j] = max(0, r - random.randint(0, r + 1)), \
                                   min(256, g + random.randint(0, g + 1) - 20), \
                                   max(b - random.randint(0, b + 1), 0)
                elif color.lower() == 'r':
                    pixels[i, j] = max(0, r - random.randint(0, r + 1)), \
                                   max(0, g - random.randint(0, g + 1)), \
                                   min(b + random.randint(0, b + 1) - 20, 256)
                elif color.lower() == 'rgb':
                    pixels[i, j] = min(256, r + random.randint(0, r + 1) - 20), \
                                   min(256, g + random.randint(0, g + 1) - 20), \
                                   min(b + random.randint(0, b + 1) - 20, 256)
                else:
                    pixels[i, j] = max(0, r - random.randint(0, r + 1)), \
                                   max(0, g - random.randint(0, g + 1)), \
                                   max(b - random.randint(0, b + 1), 0)
    return pixels


def bw_pixels(pixels, x, y, numb=100, **kwargs):
    """
    Составляет черно-белую рамку шириной и высотой numb
    :param pixels: список пикселей
    :param x: ширина
    :param y: высота
    :param numb: ширина и высота рамки (при значении ноль закрашивает всё изображение)
    :return: список пикселей
    """

    def check(numb, i, j):
        if numb != 0:
            if (i <= numb or i >= x - numb) or (
                    j <= numb or j >= y - numb) or numb == 0:
                return True
            return False
        return True

    for i in range(x):
        print(i, "из", x)
        for j in range(y):
            if check(numb, i, j):
                r, g, b = pixels[i, j]
                if sum((r, g, b)) > 512:
                    pixels[i, j] = tuple(
                        [random.randint(0, 156) + 100 for i in range(3)])
                elif 448 < sum((r, b, g)) <= 512:
                    pixels[i, j] = tuple(
                        [random.randint(0, 156) + 75 for i in range(3)])
                elif 384 < sum((r, b, g)) <= 448:
                    pixels[i, j] = tuple(
                        [random.randint(0, 156) + 50 for i in range(3)])
                elif 320 < sum((r, b, g)) <= 384:
                    pixels[i, j] = tuple(
                        [random.randint(0, 156) + 25 for i in range(3)])
                elif 256 < sum((r, b, g)) <= 384:
                    pixels[i, j] = tuple(
                        [random.randint(0, 156) for i in range(3)])
                elif 192 < sum((r, b, g)) <= 256:
                    pixels[i, j] = tuple(
                        [random.randint(0, 101) for i in range(3)])
                elif 128 < sum((r, b, g)) <= 256:
                    pixels[i, j] = tuple(
                        [random.randint(0, 76) for i in range(3)])
                elif 64 < sum((r, b, g)) <= 128:
                    pixels[i, j] = tuple(
                        [random.randint(0, 51) for i in range(3)])
                elif 32 < sum((r, g, b)) <= 64:
                    pixels[i, j] = tuple(
                        [random.randint(0, 26) for i in range(3)])
                else:
                    pixels[i, j] = tuple([0 for i in range(3)])
    return pixels


def prosvet(pixels, x, y, kol_vo=1, up_or_right='up', coeff=1, **kwargs):
    '''
    осветляет картинку некоторым кол-вом полос
    :param pixels: список пикселей
    :param x: ширина
    :param y: высота
    :param kol_vo: кол-во полос
    :param up_or_right: направление полос. Возможные значения: up, right, down, left
    :param coeff: коэффициент высветления
    :return: список пикселей
    '''
    if up_or_right == 'up' or up_or_right == 'down':
        h = y // 256 * coeff
        if kol_vo != 0:
            size = x // kol_vo
        else:
            size = x // 1
    else:
        h = x // 256
        size = y // kol_vo
    check = True
    if up_or_right == 'up':
        for i in range(x):
            print(i, "из", x)
            if i != 0 and i % size == 0:
                check = not check
            if check:
                for j in range(y):
                    r, g, b = pixels[i, j]
                    pixels[i, j] = min(j // h + r, 255), min(j // h + g,
                                                             255), min(j // h + b, 255), h
    elif up_or_right == 'left':
        for i in range(y):
            print(i, "из", y)
            if i != 0 and i % size == 0:
                check = not check
            for j in range(x):
                if check:
                    r, g, b = pixels[i, j]
                    pixels[j, i] = min((x - j) // h + r, 255), min(
                        (x - j) // h + g, 255), min(
                        (x - j) // h + b, 255), h
    elif up_or_right == 'down':
        for i in range(x):
            print(i, "из", x)
            if i != 0 and i % size == 0:
                check = not check
            if check:
                for j in range(y):
                    r, g, b = pixels[i, j]
                    pixels[i, j] = min((y - j) // h + r, 255), min(
                        (y - j) // h + g, 255), min(
                        (y - j) // h + b, 255), h
    else:
        for i in range(y):
            print(i, "из", y)
            if i != 0 and i % size == 0:
                check = not check
            for j in range(x):
                if check:
                    r, g, b = pixels[j, i]
                    pixels[j, i] = min(j // h + r, 255), min(j // h + g,
                                                             255), min(j // h + b, 255), h
    return pixels


def negativ(pixels, x, y, kol_vo=1, up_or_right='up', coeff=1, **kwargs):
    '''
        " негативит " картинку некоторым кол-вом полос
        :param pixels: список пикселей
        :param x: ширина
        :param y: высота
        :param coeff: коэффициент затемнения негатива
        :param kol_vo: кол-во полос
        :param up_or_right: направление полос. Возможные значения: up, right, down, left
        :return: список пикселей
        '''
    if up_or_right == 'up' or up_or_right == 'down':
        h = max(1, y // 256) * coeff
        if kol_vo != 0:
            size = x // kol_vo
        else:
            size = x // 1
    else:
        h = max(1, x // 256) * coeff
        if kol_vo != 0:
            size = y // kol_vo
        else:
            size = y // 1
    check = True
    if up_or_right == 'up':
        for i in range(x):
            print(i, "из", x)
            if i % size == 0 and size != x:
                check = not check
            if check:
                for j in range(y):
                    r, g, b = pixels[i, j]
                    pixels[i, j] = max(int(j // h - r), 0), \
                                   max(int(j // h - g), 0), \
                                   max(int(j // h - b), 0), h
    elif up_or_right == 'down':
        for i in range(x):
            print(i, "из", x)
            if i % size == 0 and size != x:
                check = not check
            if check:
                for j in range(y):
                    r, g, b = pixels[i, j]
                    pixels[i, j] = max(int((x - j) // h - r), 0), \
                                   max(int((x - j) // h - g), 0), \
                                   max(int((x - j) // h - b), 0), h
    elif up_or_right == 'left':
        for i in range(y):
            print(i, "из", y)
            if i % size == 0 and size != y:
                check = not check
            for j in range(x):
                if check:
                    r, g, b = pixels[j, i]
                    pixels[j, i] = max(int((x - j) // h - r), 0), \
                                   max(int((x - j) // h - g), 0), \
                                   max(int((x - j) // h - b), 0), h
    else:
        for i in range(y):
            print(i, "из", y)
            if i % size == 0 and size != y:
                check = not check
            for j in range(x):
                if check:
                    r, g, b = pixels[j, i]
                    pixels[j, i] = max(int(j // h - r), 0), \
                                   max(int(j // h - g), 0), \
                                   max(int(j // h - b), 0), h
    return pixels


def zatemn(pixels, x, y, kol_vo=1, up_or_right='up', coeff=1, **kwargs):
    '''
        затемняет картинку некоторым кол-вом полос
        :param pixels: список пикселей
        :param x: ширина
        :param y: высота
        :param kol_vo: кол-во полос
        :param coeff коэффицент затемнения полос
        :param up_or_right: направление полос. Возможные значения: up, right, left, down
        :return: список пикселей
    '''
    check = True
    if up_or_right == 'up' or up_or_right == 'down':
        h = max(1, y // 256) * coeff
        size = x // kol_vo
    else:
        h = max(1, x // 256) * coeff
        size = y // kol_vo
    if up_or_right == 'down':
        for i in range(x):
            print(i, "из", x)
            if i % size == 0 and size != x:
                check = not check
            for j in range(y):
                if check:
                    r, g, b = pixels[i, j]
                    pixels[i, j] = max(int(r - (y - j) // h), 0), \
                                   max(int(g - (y - j) // h), 0), \
                                   max(int(b - (y - j) // h), 0), h
    elif up_or_right == 'up':
        for i in range(x):
            print(i, "из", x)
            if i % size == 0 and size != x:
                check = not check
            if check:
                for j in range(y):
                    r, g, b = pixels[i, j]
                    pixels[i, j] = max(int(r - j // h), 0), max(int(g - j // h), 0), \
                                   max(int(b - j // h), 0), h
    elif up_or_right == 'left':
        for i in range(y):
            print(i, "из", y)
            if i % size == 0 and size != y:
                check = not check
            for j in range(x):
                if check:
                    r, g, b = pixels[j, i]
                    pixels[j, i] = max(int(r - (x - j) // h), 0), \
                                   max(int(g - (x - j) // h), 0), \
                                   max(int(b - (x - j) // h), 0), h
    else:
        for i in range(y):
            print(i, "из", y)
            if i % size == 0 and size != y:
                check = not check
            for j in range(x):
                if check:
                    r, g, b = pixels[j, i]
                    pixels[j, i] = max(int(r - j // h), 0), \
                                   max(int(g - j // h), 0), \
                                   max(int(b - j // h), 0), h
    return pixels

if __name__ == "__main__":
    image_filter('2.jpg', 'analize.png', negativ)
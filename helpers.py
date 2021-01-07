
def get_declinated_minute_word(num):
    if num not in (11, 12, 13, 14):
        num_modulo_10 = num % 10
        if num_modulo_10 == 1:
            return 'минуту'
        elif num_modulo_10 in (2, 3, 4):
            return 'минуты'
    return 'минут'

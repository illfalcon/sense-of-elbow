invitations = ["встреч", "тренинг", "семинар", "стажировк", "фестивал", "форум", "конференци", "вебинар",
               "мастер-класс", "хакатон", "конкурс", "забег", "акселератор", "инкубатор", "концерт", "школ",
               "супервизи", "презентаци", "консультаци", "концерт", "аукцион", "организу", "открыт набор",
               "подать заявк", "зарегистрироваться", "познакомиться", "обменяться опытом", "узнать о",
               "получить информацию о", "Встреч", "Тренинг", "Семинар", "Стажировк", "Фестивал", "Форум",
               "Конференци", "Вебинар", "Мастер-класс", "Хакатон", "Конкурс", "Забег", "Акселератор", "Инкубатор",
               "Концерт", "Школ", "Супервизи", "Презентаци", "Консультаци","Концерт", "Аукцион", "Организует",
               "Открыт набор", "Подать заявку", "Зарегистрироваться","Познакомиться", "Обменяться опытом", "Узнать о ",
               "Получить информацию о ","Приглашаем", "приглашаем", "Состоится", "состоится", "пройдет", "Пройдет",
               "пройдёт", "Пройдёт", "открывается", "Открывается", "откроется", "откроется", "проводим", "Проводим",
               "Проведем", "проведем", "Проведём", "проведём", "приглашаются", "Приглашаются", "проведет", "проведёт",
               "Проведет", "Проведёт", "курс", "Курс"
]


def contains_invitation(string):
    for inv in invitations:
        if inv in string:
            return True
    return False


def find_event(lines, beg):
    up = beg
    down = beg
    while down - beg < 4 | down < len(lines):
        if contains_invitation(lines[down]):
            return '\n'.join(lines[beg:down+1])
        down += 1
    while beg - up < 4 | up >= 0:
        if contains_invitation(lines[up]):
            return '\n'.join(lines[up:beg+1])
        up -= 1
    return ""


def find_event_simple(text):
    if contains_invitation(text):
        return text
    return ""

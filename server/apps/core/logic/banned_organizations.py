import re

from server.apps.core.logic.morphy import morphy


ORGANIZATIONS = [
    (
        "Национал-большевистская партия",
        "НБП",
    ),
    (
        "ВЕК РА",
        "Ведической Культуры Российских Ариев",
    ),
    ("Рада земли Кубанской Духовно Родовой Державы Русь",),
    ("церкви Православных Староверов-Инглингов",),
    ("Нурджулар",),
    ("К Богодержавию",),
    ("Таблиги Джамаат",),
    (
        "Свидетели Иеговы",
        "Свидетелей Иеговы",
    ),
    (
        "Всетатарского Политического Общественного Движения",
        "РЕВТАТПОД",
    ),
    ("Артподготовка",),
    (
        "Штольц Хабаровск",
        "Штольц Дальний Восток",
        "Штольц-Югент",
    ),
    ("В честь иконы Божией Матери Державная",),
    (
        "Сектор 16",
        "BugulmaUltras",
    ),
    (
        "фонд содействия национальному самоопределению народов Мира Независимость",
    ),
    ("футбольных фанатов «Поколение»",),
    ("Молодежная правозащитная группа",),
    ("Курсом Правды и Единения",),
    ("Каракольская инициативная группа",),
    ("Автоград Крю", "Autograd Crew", "Kamaz Ultras", "Blue White Crew"),
    ("Союз Славянских Сил Руси",),
    (
        "Алля-Аят",
        "Алль Аят",
        "Алля Аят",
        "Элле Аят",
        "Алла Аят",
        "Эллэ Аят",
        "Аль Аят",
    ),
    ("Ак Умут",),
    ("Русская республика Русь",),
    (
        "Арестантское уголовное единство",
        "Арестантское уркаганское единство",
        "Арестантский уклад един",
    ),
    ("Башкорт",),
    ("Комитет Нация и свобода",),
    (
        "White Hooligans Capital",
        "Белые хулиганы столицы",
        "White Hardcor Cats",
        "White Hardcore Cats",
        "SIBERIAN FRONT",
        "Сибирский фронт",
    ),
]

ANNOTATION = "(организация признана запрещенной в Российской Федерации)"


def normalize_text(text):
    words = re.split(r"[^\w]", text)
    normalized_list = []
    for word in words:
        if not word:
            continue
        normalized_word = morphy(word)[0]
        normalized_list += [normalized_word.normal_form]
    return normalized_list


def find_organization_in_text(text):
    if ANNOTATION in text:
        return
    normalized_text = normalize_text(text)
    for names in ORGANIZATIONS:
        for name in names:
            normalized_name = normalize_text(name)
            pos = find_sublist_position(normalized_text, normalized_name)
            if pos is not None:
                return pos


def find_sublist_position(lst, sublist):
    sublist_length = len(sublist)
    if sublist_length > len(lst):
        return
    for index in range(len(lst) - sublist_length):
        if lst[index : index + sublist_length] == sublist:
            return index + sublist_length


def add_annotation(text, pos):
    dividers = " ,.:;!?-"
    word_count = 0
    between = True
    for index, char in enumerate(text):
        if char in dividers:
            if not between:
                between = True
                word_count += 1
        else:
            between = False
            continue
        if word_count == pos:
            return text[:index] + " " + ANNOTATION + text[index:]


def annotate_banned_organizations(text):
    pos = find_organization_in_text(text)
    if not pos:
        return
    return add_annotation(text, pos)

from itertools import groupby



def num2signed(value):
    if value > 0:
        return '+%s' % value
    elif value < 0:
        return value
    return 0


def _get_uniques(items) -> list:
    ret = []
    for item in items:
        if not item in ret:
            ret.append(item)
    return ret

    
COLORS = [
    (77, 201, 246),
    (246, 112, 25),
    (245, 55, 148),
    (83, 123, 196),
    (172, 194, 54),
    (22, 106, 143),
    (0, 169, 80),
    (88, 89, 91), 

    (202, 201, 197),  # Light gray
    (171, 9, 0),  # Red
    (166, 78, 46),  # Light orange
    (255, 190, 67),  # Yellow
    (122, 159, 191),  # Light blue
    (140, 5, 84),  # Pink
    (166, 133, 93),  # Light brown
    (75, 64, 191),  # Red blue
]


def next_color(color_list=COLORS):
    step = 0
    while True:
        for color in color_list:
            yield list(map(lambda base: (base + step) % 256, color))
        step += 197


def get_colors():
        return next_color()


def color_dataset_options(color) -> dict:
    default_opt = {
        "backgroundColor": "rgba(%d, %d, %d, 0.9)" % color,
        "borderColor": "rgba(%d, %d, %d, 1)" % color,
        "pointBackgroundColor": "rgba(%d, %d, %d, 1)" % color,
        "pointBorderColor": "#fff",
    }
    return default_opt


def prepare_chart_data(data, conformity, processors={}, chart_type=None) -> dict:
    '''
    Подготавливает структуру данных в виде 
    необходимом для отрисовки чартов
    '''
    # Посредством определениия существования определенных ключей в 
    # списке сопоставления
    # или если указан тип чарта, можно определить структуру возвращаемых данных
    has_names = 'name' in conformity
    has_extra = 'extra' in conformity

    is_pie = chart_type == 'pie'

    datasets = []
    color_generator = get_colors()

    # Хак для чистки предыдущих графиков если для текущего нет данных
    if len(data) == 0:
        datasets.append({'data': []})

    # Возможная, предварительная обработка данных
    if len(processors) > 0:
        for row in data:
            for processor in processors.keys():
                if conformity[processor] in row:
                    row[conformity[processor]] = processors[processor](row[conformity[processor]]) if row[conformity[processor]] is not None else None

    # Данные для чартов типа "Bar", "Line"
    labels = []
    for row in data:
        if not row[conformity['label']] in labels:
            labels.append(row[conformity['label']])
    if has_names:
        names = [row[conformity['name']] for row in data]
        for name in _get_uniques(names):
            dataset = { 'label': name, 'data': [] }
            if has_extra:
                dataset.update({'extra': []})
            for label in labels:
                value = ''
                extra = ''
                for row in data:
                    if row[conformity['name']] == dataset['label']:
                        if row[conformity['label']] == label:
                            value = row[conformity['value']]
                            if has_extra:
                                extra = row[conformity['extra']]
                            break
                dataset['data'].append(value)
                if has_extra:
                    dataset['extra'].append(extra)
            dataset.update(color_dataset_options(tuple(next(color_generator))))
            datasets.append(dataset)
    else:
        if len(data) > 0:
            dataset = {
                'data': [],
                "backgroundColor": [],
                "borderColor": [],
                "pointBackgroundColor": [],
                "pointBorderColor": "#fff",
                'maxBarThickness': 50,
                }
            if has_extra:
                dataset.update({'extra': []})
            if not is_pie:
                color = tuple(next(color_generator))
            for label in [el for el, _ in groupby(labels)]:
                if is_pie:
                    color = tuple(next(color_generator))
                    dataset['label'] = label
                value = ''
                extra = ''
                for row in data:
                    if row[conformity['label']] == label:
                        value = row[conformity['value']]
                        if has_extra:
                            extra = row[conformity['extra']]
                        break
                dataset['data'].append(value)
                if has_extra:
                    dataset['extra'].append(extra)
                dataset['backgroundColor'].append("rgba(%d, %d, %d, 0.9)" % color)
                dataset['borderColor'].append("rgba(%d, %d, %d, 1)" % color)
                dataset['pointBackgroundColor'].append("rgba(%d, %d, %d, 1)" % color)
            datasets.append(dataset)
    return {'labels': labels, 'datasets': datasets}


import os
import re


FILEPATH = ''  # путь к папке с текстами

ALL_VOWELS = 'аеёиоуыэюя'

REGEXP = {
    'spaces': re.compile(r'[\s\xa0]+', re.DOTALL),
    'stress_variants': re.compile(r'(\'{2,}|\'"|`)'),
    'stress_as_downstroke': re.compile(r'_([а-яё])\'?_', re.IGNORECASE),
    'unstressed_yo': re.compile(r"(ё|Ё)(?!')"),
    'unspaced_punctuation': re.compile(r'(?<=[\w\'])([^\w\-\s\']+)(?=[\w\'])', re.IGNORECASE),
    'punctuation': re.compile(r'[^\w\s]+', re.IGNORECASE),
    'only_vowels': re.compile(r"[{}]'?".format(ALL_VOWELS), re.IGNORECASE),
}

ALL_TEMPLATES = {
    12: [(1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0)],
    13: [(1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0),
         (1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0),
         (1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0),
         (1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0),
         (1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0)],
    14: [(1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0),
         (1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0),
         (1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0),
         (1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0),
         (1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0),
         (1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0),
         (1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0),
         (1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0),
         (1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0),
         (1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0)],
    15: [(1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0),
         (1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0),
         (1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0),
         (1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0),
         (1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0),
         (1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0),
         (1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0),
         (1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0),
         (1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0),
         (1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0)],
    16: [(1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0),
         (1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0),
         (1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0),
         (1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0),
         (1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0)],
    17: [(1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0)]
}


def pos_float(f):
    res = abs(round(f, 10))
    if res < 1e-9:
        res = 0.0
    return res


def preprocess_line(text):
    text = REGEXP['spaces'].sub(' ', text)
    text = REGEXP['stress_variants'].sub("'", text)
    text = REGEXP['stress_as_downstroke'].sub(r"\1'", text)
    text = REGEXP['unstressed_yo'].sub(r"\1'", text)
    text = REGEXP['unspaced_punctuation'].sub(r'\1 ', text)
    text = text.strip(' ')
    return text


class Word(object):    

    dictionary = {}

    def __init__(self, text):
        self.text = text
        self.base_form = REGEXP['punctuation'].sub('', text.lower())

        if self.base_form in self.dictionary:
            self.dictionary[self.base_form][2] += 1
            self.syl_count = len(self.structure())
        else:
            vowels = REGEXP['only_vowels'].findall(text)
            self.syl_count = len(vowels)
            structure = []
            stress_counts = [0]
            if self.syl_count > 0:
                for vowel in vowels:
                    if vowel.endswith("'"):
                        structure.append(1)
                    else:
                        structure.append(0)

                if 1 not in structure:
                    structure = [1 for s in structure]

                if sum(structure) != 1:
                    structure = [pos_float(s / sum(structure)) for s in structure]

                stress_counts = [1 if s == 1 else 0 for s in range(self.syl_count + 1)]

            self.dictionary[self.base_form] = [structure, stress_counts, 1]

        self.surface = self.structure()

    def structure(self):
        return self.dictionary[self.base_form][0]

    def stress_counts(self):
        return self.dictionary[self.base_form][1]

    def check_template(self, template):
        if self.syl_count == 0:
            return 1
        res = self.stress_counts()[int(sum(template))]
        if 1 in template:
            res *= sum(s * t for s, t in zip(self.structure(), template))
        return res

    def apply_template(self, template):
        data = self.dictionary[self.base_form]
        k = (data[2] - 1) / data[2]

        self.surface = []
        new_structure = []
        for dval, tval in zip(data[0], template):
            if tval not in (1, 0):
                new_structure.append(dval)
                self.surface.append(dval)
            else:
                new_structure.append(pos_float(dval * k + tval / data[2]))
                self.surface.append(tval)
        data[0] = new_structure
        
        data[1] = [pos_float(k * d) for d in data[1]]
        t_stress_count = sum(template)
        plus_prob = t_stress_count % 1
        minus_prob = 1 - plus_prob
        data[1][int(t_stress_count)] += pos_float(minus_prob / data[2])
        if plus_prob > 0:
            data[1][int(t_stress_count) + 1] += pos_float(plus_prob / data[2])

        self.dictionary[self.base_form] = data
        
    def force_define(self):
        if self.syl_count == 0:
            self.surface = []
            return
        max_prob = max(self.structure())
        if max_prob == 0:
            self.surface = self.structure()
        else:
            self.surface = [1 if s == max_prob else 0 for s in self.structure()]
            if sum(self.surface) != 1:
                self.surface = [pos_float(s / sum(self.surface)) for s in self.surface]

    def text_with_stress(self):
        if self.syl_count == 0:
            return self.text
        res = []
        current_syllable = 0
        for letter in self.text.replace("'", ''):
            res.append(letter)
            if letter.lower() in ALL_VOWELS:
                if self.surface[current_syllable] == 1:
                    res.append("'")
                elif self.surface[current_syllable] != 0:
                    res.append('`')
                current_syllable += 1
        return ''.join(res)


class Line(object):

    def __init__(self, text):
        self.text = preprocess_line(text)
        self.words = [Word(w) for w in self.text.replace('-', ' ').split(' ')]
        self.syl_count = sum(w.syl_count for w in self.words)
        self.not_processed = (self.text.startswith('#') or
                              self.text.isupper() or
                              self.syl_count < 10)
        self.is_defined = self.not_processed

    def combined_structure(self):
        res = []
        for word in self.words:
            res.extend(word.structure())
        return res

    def check_template(self, template):
        res = 1
        for word in self.words:
            if word.syl_count == 0:
                continue
            temp_part, template = template[:word.syl_count], template[word.syl_count:]
            res *= word.check_template(temp_part)
        return res

    def find_best_template(self):
        templates = ALL_TEMPLATES.get(self.syl_count, None)
        if templates is None:
            return None
        if len(templates) <= 1:
            return templates[0]
        scores = [self.check_template(t) for t in templates]
        best_score = max(scores)
        res = [t for t, s in zip(templates, scores) if s == best_score]
        if len(res) > 1:
            res = [pos_float(sum(r) / len(r)) for r in zip(*res)]
        else:
            res = res[0]
        return res

    def apply_template(self, template):
        if all(t in (1, 0) for t in template):
            self.is_defined = True
        for word in self.words:
            if word.syl_count == 0:
                continue
            temp_part, template = template[:word.syl_count], template[word.syl_count:]
            word.apply_template(temp_part)

    def force_define(self):
        for word in self.words:
            if word.syl_count == 0:
                continue
            word.force_define()

    def text_with_stress(self):
        if self.not_processed:
            return self.text.replace("'", '')
        return ' '.join(w.text_with_stress() for w in self.words)


def process_text(lines):
    for line in lines:
        if not line.is_defined:
            template = line.find_best_template()
            if template is not None:
                line.apply_template(template)
    return lines


def final_form(lines):
    lens = dict.fromkeys(range(12, 18), 0)
    lens[None] = 0
    defined = 0
    texts = []
    for line in lines:
        if not line.not_processed:
            if 12 <= line.syl_count <= 17:
                lens[line.syl_count] += 1
            else:
                line.force_define()
                lens[None] += 1
            if line.is_defined:
                defined += 1
        texts.append(line.text_with_stress())
    total = sum(lens.values())
    stats = ['Всего строк: {}'.format(total)]
    stats.extend([
        'Строк длины {}: {} ({}% от всех)'.format(
            l, lens[l], round(lens[l] / total * 100, 2))
        for l in range(12, 18)])
    stats.append('Слишком длинных/коротких строк: {} ({}% от всех)'.format(
        lens[None], round(lens[None] / total * 100, 2)))
    stats.extend(['', 'Строк со снятой неоднозначностью: {} ({}%)'.format(
        defined, round(defined / total * 100, 2))])
    res = ['# ' + s for s in stats] + ['\n'] + texts
    return '\n'.join(res)


def process_all_files(path, iters=1):
    all_texts = {}
    print('Loading texts from files')
    for filename in os.listdir(path):
        if '_PROCESSED' in filename:
            continue
        with open(path + filename) as f:
            text = f.read()
        all_texts[filename.rsplit('.', 1)[0]] = [Line(l) for l in text.split('\n')]

    for i in range(iters):
        print('\nITERATION #{}/{}'.format(i + 1, iters))
        for file in all_texts:
            print('File: {}.txt'.format(file))
            all_texts[file] = process_text(all_texts[file])
    print('\nSaving processed texts to files')
    for file in all_texts:
        with open(path + file + '_PROCESSED.txt', 'w') as f:
            f.write(final_form(all_texts[file]))

if __name__ == '__main__':
    process_all_files(FILEPATH, 3)

import sys


penalties = {}
finger_effort = {}
letter_freq = {}
digram_freq = {}
trigram_freq = {}
_text = ''


class Key:
    def __init__(self, letter, finger, hand, row, col):
        self.letter = letter
        self.finger = finger
        self.hand = hand
        self.row = row
        self.col = col

    def add_effort(self, effort):
        self.effort = effort


class Keyboard:
    def __init__(self, name, layout):
        self.name = name
        # divide layout into a table 3x10
        self.layout = []
        for row in range(3):
            self.layout.append([])
            for col in range(10):
                finger, hand = self.get_hand_finger(row, col)
                key = Key(layout[row][col], finger, hand, row, col)
                self.layout[row].append(key)
        # add other row for thumbs
        self.layout.append([])
        finger, hand = self.get_hand_finger(3, 0)
        key = Key(' ', finger, hand, 3, 0)
        self.layout[3].append(key)

        # calculate effort
        for row in self.layout:
            for key in row:
                key.add_effort(self.calc_effort(key))

        # print name
        # print(f'Keyboard: {self.name}')
        # print layout
        # self.print_layout()
        # evaluate
        self.evaluate()
        # self.print_statistics()
        # print('-' * 20)

    def define_home_row(self):
        # define home key per finger
        home_row = {}
        home_row['left'] = {}
        home_row['right'] = {}
        home_row['left']['pinky'] = (1, 0)
        home_row['left']['ring'] = (1, 1)
        home_row['left']['middle'] = (1, 2)
        home_row['left']['index'] = (1, 3)
        home_row['right']['index'] = (1, 6)
        home_row['right']['middle'] = (1, 7)
        home_row['right']['ring'] = (1, 8)
        home_row['right']['pinky'] = (1, 9)
        home_row['left']['thumb'] = (3, 0)
        return home_row

    def get_hand_finger(self, row, col):
        if col == 0 or col == 9:
            finger = 'pinky'
        elif col == 1 or col == 8:
            finger = 'ring'
        elif col == 2 or col == 7:
            finger = 'middle'
        elif col == 3 or col == 4 or col == 5 or col == 6:
            finger = 'index'
        if col < 5:
            hand = 'left'
        else:
            hand = 'right'

        if row == 3:
            finger = 'thumb'
        return finger, hand

    def calc_effort(self, key):
        global finger_effort
        # calculate distance from home key using same finger and hand
        hand = key.hand
        finger = key.finger

        # get home row
        home_row = self.define_home_row()
        home_key = self.layout[home_row[hand][finger][0]][home_row[hand][finger][1]]

        # calculate distance using Pythagorean theorem
        distance = ((key.row - home_key.row)**2 + (key.col - home_key.col)**2)**0.5 + 1
        effort = finger_effort[finger] * distance
        effort = round(effort, 1)
        return effort

    def get_effort(self, keys, distance):
        global penalties

        if keys[-1].letter == keys[-2].letter:
            self.statistics['Same finger'] += 1
            return keys[-1].effort

        effort = keys[-1].effort
        # penalties
        last_key = keys[-2]
        current_key = keys[-1]

        if last_key.hand == current_key.hand and last_key.finger == current_key.finger:
            self.statistics['Same finger'] += 1
            # finger repetition penalty
            effort += penalties['Same finger'] * distance * keys[-1].effort
        # hand repetition penalty
        elif last_key.hand == current_key.hand:
            effort += penalties['Swap hand'] * distance * keys[-1].effort
        else:
            self.statistics['Swap hand'] += 1

        return effort

    def evaluate(self):
        global _text
        global letter_freq
        global digram_freq
        global trigram_freq
        # print(f'Evaluating {self.name} keyboard...')
        # use text and get total effort and total distance

        self.statistics = {}
        self.statistics['total_effort'] = 0
        self.statistics['total_distance'] = 0
        self.statistics['total_presses'] = 0
        self.statistics['key_presses'] = [[0 for x in range(10)] for y in range(4)]
        # finger frequency
        self.statistics['finger_freq'] = {}
        self.statistics['finger_freq']['left'] = {'pinky': 0, 'ring': 0, 'middle': 0, 'index': 0, 'thumb': 0}
        self.statistics['finger_freq']['right'] = {'pinky': 0, 'ring': 0, 'middle': 0, 'index': 0}
        # row frequency
        self.statistics['row_freq'] = {'0': 0, '1': 0, '2': 0, '3': 0}

        self.statistics['Lateral movement'] = 0
        self.statistics['Swap hand'] = 0
        self.statistics['Same finger'] = 0

        for digram, freq in digram_freq.items():
            letter1, letter2 = digram
            key1, key2 = '', ''
            for row in self.layout:
                for key in row:
                    if key.letter == letter1:
                        key1 = key
                    if key.letter == letter2:
                        key2 = key
            # calculate distance
            home_row = self.define_home_row()
            if key1.finger == key2.finger and key1.hand == key2.hand:
                # distance is from home position to key1 to key2
                homex, homey = home_row[key1.hand][key1.finger]
                key1x, key1y = (key1.row, key1.col)
                key2x, key2y = (key2.row, key2.col)
                dis = ((key1x - homex)**2 + (key1y - homey)**2)**0.5
                dis += ((key2x - key1x)**2 + (key2y - key1y)**2)**0.5
                distance = dis
            else:
                # distance is from home position to key1 to key2
                home1x, home1y = home_row[key1.hand][key1.finger]
                home2x, home2y = home_row[key2.hand][key2.finger]
                key1x, key1y = (key1.row, key1.col)
                key2x, key2y = (key2.row, key2.col)
                dis1 = ((key1x - home1x)**2 + (key1y - home1y)**2)**0.5
                dis2 = ((key2x - home2x)**2 + (key2y - home2y)**2)**0.5
                distance = dis1 + dis2

            # calculate effort
            effort = self.get_effort([key1, key2], distance) * freq
            self.statistics['total_effort'] += effort
            self.statistics['total_distance'] += distance * freq

        for letter, freq in letter_freq.items():
            # calculate presses
            for row in self.layout:
                for key in row:
                    if key.letter == letter:
                        self.statistics['key_presses'][key.row][key.col] += freq
                        self.statistics['total_presses'] += freq
                        self.statistics['row_freq'][str(key.row)] += freq
                        self.statistics['finger_freq'][key.hand][key.finger] += freq

                        # calculate lateral movement
                        # if finger index and col 4 or 5
                        if key.finger == 'index' and key.col in [4, 5]:
                            self.statistics['Lateral movement'] += freq

        self.statistics['total_effort'] /= self.statistics['total_presses']

        # calculate finger frequency percentage
        for hand in self.statistics['finger_freq']:
            for finger in self.statistics['finger_freq'][hand]:
                self.statistics['finger_freq'][hand][finger] /= self.statistics['total_presses']
                self.statistics['finger_freq'][hand][finger] *= 100

        # swap hand divided by total digrams
        self.statistics['Swap hand'] /= len(digram_freq)
        self.statistics['Swap hand'] *= 100
        # same finger divided by total digrams
        self.statistics['Same finger'] /= len(digram_freq)
        self.statistics['Same finger'] *= 100

        # lateral movement / index finger freq% of total presses
        index_freq = self.statistics['finger_freq']['left']['index'] + self.statistics['finger_freq']['right']['index']
        index_freq = (index_freq / 100) * self.statistics['total_presses']
        self.statistics['Lateral movement'] /= index_freq
        self.statistics['Lateral movement'] *= 100

        return self.statistics

    def print_statistics(self):
        print()
        print(f'{self.name} keyboard statistics:')
        print(f'Total presses: {self.statistics["total_presses"]}')
        print('Key presses:')
        for row in self.statistics['key_presses']:
            for col in row:
                print(col, end='\t')
            print()
        print()
        print('Finger frequency:')
        total_left = 0
        for finger in self.statistics['finger_freq']['left']:
            total_left += self.statistics['finger_freq']['left'][finger]
        print(f'Left hand: {total_left:.2f}%')
        for finger in self.statistics['finger_freq']['left']:
            print(f'\t{finger}: {self.statistics["finger_freq"]["left"][finger]:.2f}%')
        total_right = 0
        for finger in self.statistics['finger_freq']['right']:
            total_right += self.statistics['finger_freq']['right'][finger]
        print(f'Right hand: {total_right:.2f}%')
        for finger in self.statistics['finger_freq']['right']:
            print(f'\t{finger}: {self.statistics["finger_freq"]["right"][finger]:.2f}%')
        print()
        print('Row frequency:')
        for row in self.statistics['row_freq']:
            print(f'\tRow {row}: {self.statistics["row_freq"][row]:.2f}%')
        print()
        print('Penalties:')
        print(f'\tLateral movement: {self.statistics["Lateral movement"]}')
        print(f'\tSwap hand: {self.statistics["Swap hand"]}')
        print(f'\tSame finger: {self.statistics["Same finger"]}')
        print()
        print('Total effort:', self.statistics['total_effort'])
        print('Total distance:', self.statistics['total_distance'])

    def print_layout(self):
        # print layout
        for row in self.layout:
            for key in row:
                print(key.letter, end=' ')
            print()

    def print_effort_layout(self):
        # print effort
        for row in self.layout:
            for key in row:
                print(key.effort, end=' ')
            print()


def print_tests(keyboard):
    # print fingers
    for row in keyboard.layout:
        for key in row:
            print(key.finger, end=' ')
        print()
    print()

    # print hands
    for row in keyboard.layout:
        for key in row:
            print(key.hand, end=' ')
        print()
    print()


def print_comparison(keyboards):
    global penalties
    print(f"{'Keyboard comparison:':-^60}")
    print('------------------------------------------------------------')

    # print penalties
    print('Penalties:')
    print(f'Same finger: {penalties["Same finger"]:.2f}')
    print(f'Swap hand: {penalties["Swap hand"]:.2f}')
    print(f'Lateral movement: {penalties["Lateral movement"]:.2f}')
    print()

    # sort by effort
    keyboards.sort(key=lambda x: x.statistics['total_effort'])
    print('Sorted by effort:')

    # print comparison
    print(f"{'Name':^20}", end='')
    print(f"{'Effort':^18}", end='')
    print(f"{'Distance':^18}", end='')
    print(f"{'Lateral movement':^18}", end='')
    print(f"{'Swap hand':^18}", end='')
    print(f"{'Same finger':^18}")
    for keyboard in keyboards:
        print(f"{keyboard.name:<20}", end='')
        effort = f"{keyboard.statistics['total_effort']:^18.2f}"
        distance = f"{keyboard.statistics['total_distance']:^18.2f}"
        lateral_movement = f"{keyboard.statistics['Lateral movement']:^18.2f}"
        swap_hand = f"{keyboard.statistics['Swap hand']:^18.2f}"
        same_finger = f"{keyboard.statistics['Same finger']:^18.2f}"
        print(effort, distance,
              lateral_movement, swap_hand, same_finger)
    print()

    # print best by category
    print('Best effort:', keyboards[0].name,
            f'{keyboards[0].statistics["total_effort"]:.2f}')
    # sort by distance
    keyboards.sort(key=lambda x: x.statistics['total_distance'])
    print('Best distance:', keyboards[0].name,
            f'{keyboards[0].statistics["total_distance"]:.2f}')
    # sort by lateral movement
    keyboards.sort(key=lambda x: x.statistics['Lateral movement'])
    print('Best lateral movement:', keyboards[0].name,
            f'{keyboards[0].statistics["Lateral movement"]:.2f}%')
    # sort by swap hand
    keyboards.sort(key=lambda x: x.statistics['Swap hand'])
    print('Best swap hand:', keyboards[0].name,
            f'{keyboards[0].statistics["Swap hand"]:.2f}%')
    # sort by same finger
    keyboards.sort(key=lambda x: x.statistics['Same finger'])
    print('Best same finger:', keyboards[0].name,
            f'{keyboards[0].statistics["Same finger"]:.2f}%')


# try to create a layout with minimal effort
def create_layout(test_num=10):
    import random
    test_num = max(test_num, 10)
    # create array of letters
    letters = 'abcdefghijklmnñopqrstuvwxyz.,/'
    better_than_qwerty = 0

    qwerty = Keyboard('QWERTY', ['qwertyuiop', 'asdfghjklñ', 'zxcvbnm,./'])

    keyboards = []
    for i in range(test_num):
        # sort letters randomly and create layout 3x10
        tmp = ''.join(random.sample(letters, len(letters)))
        # split in 3 rows of 10 letters
        layout = [tmp[i:i + 10] for i in range(0, len(tmp), 10)]

        keyboards.append(Keyboard(f'layout_{i}', layout))

        if keyboards[-1].statistics['total_effort'] < qwerty.statistics['total_effort']:
            better_than_qwerty += 1

    # sort keyboards by effort
    keyboards.sort(key=lambda x: x.statistics['total_effort'])

    print(f'In a random layout generation {better_than_qwerty} out of {test_num} layouts are better than QWERTY')
    print('-----------------------------------------------------')
    min_keyboard = keyboards[0]
    print(f'Best random layout: {min_keyboard.name}')
    min_keyboard.print_layout()

    # return 10 best layouts
    return keyboards[:10]


def test_popular_keyboards():
    keyboards = []
    keyboards.append(
        Keyboard('QWERTY',      ['qwertyuiop', 'asdfghjklñ', 'zxcvbnm,./']))
    keyboards.append(
        Keyboard('Dvorak',      ['/,.pyfgcrl', 'aoeuidhtns', 'ñqjkxbmwvz']))
    keyboards.append(
        Keyboard('Colemak',     ['qwfpgjluyñ', 'arstdhneio', 'zxcvbkm,./']))
    keyboards.append(
        Keyboard('Colemak DHm', ['qwfpbjluyñ', 'arstgmneio', 'zxcdvkh,./']))
    keyboards.append(
        Keyboard('Workman',     ['qdrwbjfupñ', 'ashtgyneoi', 'zxmcvkl,./']))
    return keyboards


def visualize(keyboard):
    print(f'Keyboard: {keyboard.name}')
    keyboard.print_layout()
    print(f'\tEffort: {keyboard.statistics["total_effort"]:.2f}')
    print()


def swap_layout(layout, i, j):
    # layout is a str
    # return a new layout with the two letters swapped
    return layout[:i] + layout[j] + layout[i + 1:j] + layout[i] + layout[j + 1:]


# function that minimizes effort
def minimize_effort(layout):
    # layout is a str of 30 letters
    # l is a list of 3 rows of 10 letters
    new_layout = [layout[i:i + 10] for i in range(0, 30, 10)]
    # create keyboard
    keyboard = Keyboard('base_layout', new_layout)
    effort = keyboard.statistics['total_effort']
    visualize(keyboard)

    restart = True
    ite = 0
    while restart:
        for i in range(29):
            for j in range(i + 1, 30):
                ite += 1
                new_layout = swap_layout(layout, i, j)
                new_layout = [new_layout[i:i + 10] for i in range(0, 30, 10)]
                tmp_keyboard = Keyboard(f'min_effort_{ite}', new_layout)
                if tmp_keyboard.statistics['total_effort'] < effort:
                    effort = tmp_keyboard.statistics['total_effort']
                    keyboard = tmp_keyboard
                    visualize(keyboard)
                    layout = swap_layout(layout, i, j)
                    i = 0
                    break
            else:
                continue
            break
        else:
            restart = False

    return keyboard


def analize(text):
    valid_chars = "abcdefghijklmnñopqrstuvwxyz,./ "
    letter_freq = {}
    digram_freq = {}
    trigram_freq = {}

    with open(text, 'r') as f:
        text = f.read()
        text = text.lower()
        # remove accents
        text = text.replace('á', 'a')
        text = text.replace('é', 'e')
        text = text.replace('í', 'i')
        text = text.replace('ó', 'o')
        text = text.replace('ú', 'u')
        text = text.replace('ü', 'u')

        # read letter by letter and add to dictionary
        # store 3 letters in a list
        letters_3 = []

        for letter in text:
            if letter in letter_freq and letter in valid_chars:
                letter_freq[letter] += 1
            else:
                letter_freq[letter] = 1

            letters_3.append(letter)

            # bigrams
            if len(letters_3) >= 2:
                # check if valid char
                if letters_3[-2] in valid_chars and letters_3[-1] in valid_chars:
                    digram = letters_3[-2] + letters_3[-1]
                    if digram in digram_freq:
                        digram_freq[digram] += 1
                    else:
                        digram_freq[digram] = 1

            # trigrams
            if len(letters_3) >= 3:
                # check if valid char
                if letters_3[-3] in valid_chars and letters_3[-2] in valid_chars and letters_3[-1] in valid_chars:
                    trigram = letters_3[-3] + letters_3[-2] + letters_3[-1]
                    if trigram in trigram_freq:
                        trigram_freq[trigram] += 1
                    else:
                        trigram_freq[trigram] = 1

    # sort dictionary by value and print 10 most frequent letters ignoring ' '
    sorted_letters = sorted(letter_freq.items(), key=lambda x: x[1])
    # filter out ' '
    sorted_letters = [x[0] for x in sorted_letters if x[0] != ' ']
    sorted_letters.reverse()
    print("10 most frequent letters:")
    print(sorted_letters[:10])

    # sort dictionary by value and print 10 most frequent digrams
    sorted_digrams = sorted(digram_freq.items(), key=lambda x: x[1])
    sorted_digrams = [x[0] for x in sorted_digrams if ' ' not in x[0]]
    sorted_digrams.reverse()
    print("10 most frequent digrams:")
    print(sorted_digrams[:10])

    # sort dictionary by value and print 10 most frequent trigrams
    sorted_trigrams = sorted(trigram_freq.items(), key=lambda x: x[1])
    sorted_trigrams = [x[0] for x in sorted_trigrams if ' ' not in x[0]]
    sorted_trigrams.reverse()
    print("10 most frequent trigrams:")
    print(sorted_trigrams[:10])

    return letter_freq, digram_freq, trigram_freq


def main():
    global penalties
    global finger_effort
    global letter_freq
    global digram_freq
    global trigram_freq

    letter_freq, digram_freq, trigram_freq = analize(_text)

    finger_effort = {
            'pinky': 1.6,
            'ring': 1.3,
            'middle': 1.1,
            'index': 1,
            'thumb': 1}

    if len(sys.argv) > 2:
        penalties_list = sys.argv[2].split(',')
        penalties_list = [float(penalty) for penalty in penalties_list]
    else:
        penalties_list = [2, 3, 1]

    penalties = {
            'Same finger': penalties_list[0],
            'Swap hand': penalties_list[1],
            'Lateral movement': penalties_list[2],
            }

    # create keyboard
    keyboards = test_popular_keyboards()

    # keyboards.append(Keyboard('best_spanish', ['ñx.u/qdpgy', 'raeoilsntc', 'jwz,khmbvf']))
    # keyboards.append(Keyboard('best_english', ['qkui/vhcgb', 'ateo,lnsrd', 'zjy.ñfmpwx']))
    # keyboards += create_layout(1000)
    min_keyboard = minimize_effort('qwertyuiopasdfghjklñzxcvbnm,./')
    keyboards.append(min_keyboard)

    print_comparison(keyboards)


if __name__ == '__main__':
    # get python args to get text
    if len(sys.argv) > 1:
        _text = sys.argv[1]
    else:
        _text = 'en.txt'
    main()

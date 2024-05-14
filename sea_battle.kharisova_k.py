from random import randint

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'

    def __eq__(self, other):
        if isinstance(other, Dot):
            return self.x == other.x and self.y == other.y
        return False


class BoardException(Exception):
    pass

class OutOfBoardException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class DotIsBusyException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"

class WrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, start: Dot, end: Dot):
        self.start = start
        self.end = end
        self.lives = 0


    @property
    def dots(self):
        if self.start == self.end:
            return [self.start]
        elif self.start.x == self.end.x:
            dots_list_y = []
            y = min(self.start.y, self.end.y)
            y_max = max(self.start.y, self.end.y)
            x = self.start.x
            while y <= y_max:
                dot = Dot(x, y)
                dots_list_y.append(dot)
                y += 1
            return dots_list_y
        else:
            dots_list_x = []
            x = min(self.start.x, self.end.x)
            y = self.start.y
            x_max = max(self.start.x, self.end.x)
            while x <= x_max:
                dot = Dot(x, y)
                dots_list_x.append(dot)
                x += 1
            return dots_list_x

    def shooten(self, shot):
        return shot in self.dots



class Board:
    def __init__(self, size = 6, hid = False):
        self.size = size
        self.hid = hid
        self.ships = []
        self.count = 0
        self.busy = []
        self.field = [["."] * size for _ in range(size)]

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def is_out(self, d: Dot):
        return not((0<= d.x < self.size) and (0<= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 0), (0, 1),
                (1, -1), (1, 0), (1, 1)
            ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.is_out(cur)) and cur not in self.busy:
                    if verb:
                         self.field[cur.x][cur.y] = "0"
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.is_out(d) or d in self.busy:
                raise WrongShipException
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.is_out(d):
            raise OutOfBoardException()

        if d in self.busy:
            raise DotIsBusyException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "0"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите 2 координаты!")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def generate_board(self):
        count_ships = [3, 2, 2, 1, 1, 1,1]
        board = Board()
        attempts = 0
        for i in count_ships:
            while True:
                attempts += 1
                ship = Ship(Dot((randint(0,6)), (randint(0,6))), Dot((randint(0,6)), randint(0,6)))
                if attempts > 2000:
                    return None
                try:
                    board.add_ship(ship)
                    break
                except WrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.generate_board()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def play(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.play()

g = Game()
g.start()
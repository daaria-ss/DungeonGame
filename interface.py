from animator import Animator
import config
import sys
from functions import *
import pygame
from entity import Player


class Window:
    """Класс окна"""

    def __init__(self, name, objects, music_name='main'):
        self.name = name
        self.objects = objects
        self.music_name = music_name
        self.important_windows = ['menu', 'game', 'exit', 'lose']
        self.first_load = True

        self.fade_in_counter = 0
        self.fade_out_counter = 61
        self.fade_target = None

        self.fader = pygame.Surface(SIZE)
        self.fader.fill(BLACK)

    def get_event(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                for obj in self.objects:
                    obj.key_down(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for obj in self.objects:
                    target = obj.button_down(event.pos)
                    if target:
                        if target in self.important_windows \
                                and self.name in self.important_windows:
                            self.fade_target = target
                            self.fade_out_counter = 0
                        else:
                            return target
            elif event.type == pygame.MOUSEBUTTONUP:
                for obj in self.objects:
                    obj.button_up(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                for obj in self.objects:
                    obj.mouse_motion(event.pos)

        self.first_load = False
        return self.name

    def fade(self, surf, value):
        self.fader.set_alpha(int(value * 4.25))
        surf.blit(self.fader, (0, 0))

    def update(self, surf, events):
        if self.name == 'exit':
            pygame.quit()
            sys.exit(1)
        if config.LOSE:
            self.fade_out_counter = 0
            self.fade_target = 'lose'
            config.LOSE = False
        if self.first_load:
            if self.music_name != music.current_music:
                music.play_music(self.music_name)
            if self.name in self.important_windows:
                self.fade_in_counter = 60
            self.first_load = False

        for obj in self.objects:
            obj.show(surf)

        if self.fade_in_counter != 0:
            self.fade(surf, self.fade_in_counter)
            self.fade_in_counter -= 1
        elif self.fade_out_counter != 61:
            self.fade(surf, self.fade_out_counter)
            self.fade_out_counter += 1
            if self.fade_out_counter == 61:
                self.first_load = True
                if self.fade_target == 'lose' or self.fade_target == 'menu':
                    self.objects[0].new()  # обновляем подземелье
                return self.fade_target

        if self.fade_in_counter != 0 or self.fade_out_counter != 61:
            return self.name
        return self.get_event(events)


class Element:
    """Абстрактный класс элемента в окне"""

    def __init__(self):
        pass

    def button_down(self, mouse_pos):
        """Функция нажатия мыши"""
        pass

    def button_up(self, mouse_pos):
        """Функция отпускания мыши"""
        pass

    def mouse_motion(self, mouse_pos):
        """Функция движения мыши"""
        pass

    def key_down(self, button):
        """Функция нажатия на клавиатуру"""
        pass

    def show(self, surf):
        """Отображение на поверхность"""
        pass


class AnimatedElement(Element):
    """Класс анимированного элемента в окне"""

    def __init__(self, path, position, animator_options=None):
        super().__init__()
        self.animator = Animator(path, animator_options)  # создаем аниматор
        self.position = position  # позиция
        self.rect = self.animator.next_()[0].get_rect(
            topleft=position)  # определяем прямоугольник

    def show(self, surf):
        """Отображение на поверхности"""
        image, shift = self.animator.next_()
        surf.blit(image,
                  (self.position[0] + shift[0], self.position[1] + shift[1]))


class Button(AnimatedElement):
    """Класс кнопки"""

    def __init__(self, name, position, target, animator_options=None):
        super().__init__('Sprites/' + name, position, animator_options)
        self.target = target  # имя окна, в которое мы перейдем,
        # если нажмем на эту кнопку

    def button_down(self, mouse_pos):
        """Функция нажатия мыши"""
        if self.rect.collidepoint(mouse_pos):  # если нажали на кнопку
            music.play_sound('button_down')  # проигрываем звук нажатия
            self.animator.start('idle')
            return self.target  # возвращаем имя окна, в которое нужно перейти

    def mouse_motion(self, mouse_pos):
        """Функция движения мыши"""
        if self.rect.collidepoint(mouse_pos):  # если навели на кнопку
            if self.animator.animation == 'idle':
                self.animator.start('hover')  # включаем анимацию наведения
        else:
            self.animator.start('idle')  # иначе включаем анимацию покоя


class Image(AnimatedElement):
    """Класс изображения"""

    def __init__(self, name, position, animator_options=None):
        super().__init__('Sprites/' + name, position, animator_options)


class AntiButton(AnimatedElement):
    """Класс анти-кнопки"""

    def __init__(self, name, position, target):
        super().__init__('Sprites/' + name, position)
        self.target = target  # имя окна, в которое мы перейдем,
        # если нажмем на вне этой кнопки

    def button_down(self, mouse_pos):
        """Функция нажатия мыши"""
        if not self.rect.collidepoint(mouse_pos):  # если нажали не на кнопку
            return self.target  # возвращаем имя окна, в которое нужно перейти


class Slider(AnimatedElement):
    """Класс слайдера"""

    def __init__(self, name, position, borders, function):
        super().__init__('Sprites/' + name, position)
        self.capture = False  # нажат ли на слайдер
        self.borders = borders  # границы слайдера
        self.function = function  # функция, вызываемая при изменении значения

    def button_down(self, mouse_pos):
        """Функция нажатия мыши"""
        # проверяем нажали ли на слайдер
        if self.rect.collidepoint(mouse_pos):
            self.capture = True
        else:
            self.capture = False

    def button_up(self, mouse_pos):
        """Функция отпускания мыши"""
        self.capture = False

    def mouse_motion(self, mouse_pos):
        """Функция движения мыши"""
        if self.capture:  # если слайдер зажат
            # то двигаем его, не выходя за границы
            if self.borders[0] <= mouse_pos[0] <= self.borders[1]:
                x = mouse_pos[0]
            elif mouse_pos[0] < self.borders[0]:
                x = self.borders[0]
            elif mouse_pos[0] > self.borders[1]:
                x = self.borders[1]
            self.position = (x, self.position[1])  # меняем позицию
            self.rect = self.animator.next_()[0].get_rect(
                topleft=self.position)  # и прямоугольник
            # вызываем функцию, привязанную к изменению значения слайдера
            getattr(music, self.function)(
                (x - self.borders[0]) / (self.borders[1] - self.borders[0]))


class Text(Element):
    """Класс текста"""

    def __init__(self, position, color, target=None, attr_name=None,
                 text=None):
        super().__init__()
        self.position = position  # позиция
        self.color = color  # цвет
        self.target = target  # либо объект класса игрок
        self.attr_name = attr_name  # и имя атрибута, которе нужно отображать
        self.text = text  # либо статичный текст

        self.font = pygame.font.Font(None, 40)  # шрифт

    def show(self, surf):
        """Отображение на поверхности"""
        if self.target and self.attr_name:
            # если есть объект класса игрок и его атрибут
            value = getattr(self.target, self.attr_name)  # то отображаем его
            if isinstance(self.target, Player):
                surf.blit(
                    self.font.render(str(value[0]) + '/' + str(value[1]), True,
                                     self.color),
                    self.position)
            else:
                surf.blit(
                    self.font.render(value, True,
                                     self.color),
                    self.position)
        elif self.text:  # если есть статичный текст, то отбражаем его
            surf.blit(self.font.render(str(self.text), True, self.color),
                      self.position)
        else:  # иначе отображаем пустую строку
            surf.blit(self.font.render('', True, self.color), self.position)


class Panel(Element):
    """Класс панели"""

    def __init__(self, target, y_shift):
        super().__init__()
        self.background = Image('game/panel/background', (0, y_shift + 0))
        self.target = target
        self.y_shift = y_shift
        self.objects = [
            Image('game/panel/health', (50, y_shift + 10)),
            Text((90, y_shift + 13), HP_COLOR, target, 'hit_points'),
            Image('game/panel/damage', (170, y_shift + 10)),
            Text((210, y_shift + 13), DAMAGE_COLOR, target, 'damage'),
            Image('game/panel/action_points', (290, y_shift + 10)),
            Text((330, y_shift + 13), ACTION_POINTS_COLOR, target,
                 'action_points'),
        ]

    def show(self, surf):
        """Отображение на поверхности"""
        self.background.show(surf)
        self.target = self.target if self.target and self.target.alive \
            else None
        if self.target:
            for obj in self.objects:
                obj.show(surf)

    def change_target(self, new_target):
        self.target = new_target
        self.objects = [
            Image('game/panel/health', (50, self.y_shift + 10)),
            Text((90, self.y_shift + 13), HP_COLOR, new_target, 'hit_points'),
            Image('game/panel/damage', (170, self.y_shift + 10)),
            Text((210, self.y_shift + 13), DAMAGE_COLOR, new_target, 'damage'),
            Image('game/panel/action_points', (290, self.y_shift + 10)),
            Text((330, self.y_shift + 13), ACTION_POINTS_COLOR, new_target,
                 'action_points'),
        ]


class InventorySlot(Element):
    """Класс слота в инвентаре"""

    def __init__(self, position, image, description):
        super().__init__()
        self.position = position  # позиция
        self.base = load_image(
            'Sprites/inventory/slot.png')  # пустой слот инвентаря
        self.image = image  # содержимое слота
        self.rect = self.base.get_rect(topleft=position)  # прямоугольник
        self.description = Text(DESCRIPTION_POSITION, DESCRIPTION_COLOR,
                                text=description)  # описание

    def show(self, surf):
        """Отображение на поверхности"""
        surf.blit(self.base, self.position)  # отображаем пустой слот
        if self.image:  # если есть содержимое,
            surf.blit(self.image, self.position)  # то отображаем его

    def show_description(self, surf):
        """Отображение описания"""
        self.description.show(surf)

    def button_down(self, mouse_pos):
        """Функция нажатия мыши"""
        if self.rect.collidepoint(mouse_pos):  # нажали ли на слот
            return True


class Inventory(Element):
    """Класс инвентаря"""

    def __init__(self, target):
        super().__init__()
        self.base = AntiButton('game/inventory', (97, 97),
                               'game')  # изображения инвентаря

        # словарь вида {названия содержимого в инвентаре: [картинка, описание]}
        self.image_keys = {
            'red_key': (load_image('Sprites/inventory/red_key.png'),
                        'This key open red doors'),
            'green_key': (
                load_image('Sprites/inventory/green_key.png'),
                'This key open green doors'),
            'blue_key': (load_image('Sprites/inventory/blue_key.png'),
                         'This key open blue doors'),
            'health': (load_image('Sprites/inventory/green_potion.png'),
                       'This potion heals you')
        }

        self.target = target
        # в какое окно мы перейдем, при выходе из инвентаря
        self.slots = []  # слоты
        self.active_slot = None  # выбранный слот

    def update(self):
        """Обновление слотов"""
        self.slots = []  # опустошаем слоты
        counter = 0
        for i in range(4):
            self.slots.append([])
            for k in range(5):
                # определяем параметры для нового слота
                if counter < len(self.target.player.inventory):
                    # слот с содержимым согласно инвентарю игрока
                    params = self.image_keys[
                        self.target.player.inventory[counter]]
                else:
                    params = (None, '')
                self.slots[i].append(InventorySlot(
                    (100 + INVENTORY_INDENT + k * (
                            INVENTORY_IMAGE_SIZE[0] + INVENTORY_INDENT),
                     100 + INVENTORY_INDENT + i * (
                             INVENTORY_IMAGE_SIZE[1] + INVENTORY_INDENT)),
                    *params))
                counter += 1

    def show(self, surf):
        """Отображение на поверхности"""
        self.update()  # обновляем слоты
        self.base.show(surf)  # показываем картинку инвентаря
        for i in range(len(self.slots)):
            for k in range(len(self.slots[i])):
                self.slots[i][k].show(surf)  # показываем слоты
        if self.active_slot:  # если есть выбранный слот, то
            self.active_slot.show_description(surf)  # показываем его описание

    def button_down(self, mouse_pos):
        """Функция нажатия мыши"""
        res = self.base.button_down(mouse_pos)  # если нажали вне инвентаря
        if res:
            return res  # то переходим в игру
        for i in range(len(self.slots)):
            for k in range(len(self.slots[i])):  # если нажали на слот
                if self.slots[i][k].button_down(mouse_pos):
                    self.active_slot = self.slots[i][
                        k]  # то он становится активным
                    return
        self.active_slot = None  # опустошаем активный слот


class InputBox(AnimatedElement):
    def __init__(self, name, position, function):
        super().__init__('Sprites/' + name, position, function)
        self.input_ = Text((position[0] + 15, position[1] + 15),
                           DESCRIPTION_COLOR, text='')

    def key_down(self, key):
        if pygame.key.name(key) == 'backspace':
            self.input_.text = self.input_.text[:-1]
        elif len(pygame.key.name(key)) == 1 and pygame.key.name(key).isalnum():
            self.input_.text += pygame.key.name(key)
        config.INPUT_USER = self.input_.text

    def show(self, surf):
        super().show(surf)
        self.input_.show(surf)


class Arrow(Button):
    def __init__(self, name, position, function, animator_options=None):
        super().__init__(name, position, animator_options)
        self.function = function  # функция, которую надо выполнить при нажатии

    def button_down(self, mouse_pos):
        """Функция нажатия мыши"""
        if self.rect.collidepoint(mouse_pos):  # если нажали на кнопку
            music.play_sound('button_down')  # проигрываем звук нажатия
            config.N = (config.N + self.function) % config.MAX_N
            config.USER_NAME = config.USERS[config.N] if config.USERS else None


class SaveButton(Button):
    def __init__(self, name, position, target, obj, animator_options=None):
        super().__init__(name, position, target, animator_options)
        self.obj = obj  # объект подземелья
        self.target = target

    def button_down(self, mouse_pos):
        """Функция нажатия мыши"""
        if self.rect.collidepoint(mouse_pos):  # если нажали на кнопку
            if self.obj.user_name not in config.USERS:
                self.obj.save(config.INPUT_USER)
                return self.target


class LoadButton(Button):
    def __init__(self, name, position, target, obj, animator_options=None):
        super().__init__(name, position, target, animator_options)
        self.obj = obj  # объект подземелья
        self.target = target

    def button_down(self, mouse_pos):
        """Функция нажатия мыши"""
        if self.rect.collidepoint(mouse_pos):  # если нажали на кнопку
            if config.USER_NAME:
                self.obj.load(config.USER_NAME)
                return self.target
import pygame


# EDIT
# edit sounds and music files
class Music:

    def __init__(self):
        pygame.init()
        self.sounds = {
            'hit': pygame.mixer.Sound('Sounds/tuk.mp3'),
            'button_down': pygame.mixer.Sound('Sounds/tuk.mp3'),
        }
        self.musics = {
            'main': 'Sounds/menu_music.mp3',
            'game': 'Sounds/melody.mp3',
        }

    def play_sound(self, name):
        self.sounds[name].play()

    def play_music(self, name):
        pygame.mixer.music.load(self.musics[name])
        pygame.mixer.music.play()

    def set_music_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

    def set_sounds_volume(self, volume):
        for sound in self.sounds.values():
            sound.set_volume(volume)

import os, pygame
from pygame.locals import *
from pygame.compat import geterror
from random import randint

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

class FlySwatter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('fly-swatter.png', 
            convert_alpha=True)
        screen = pygame.display.get_surface()
        self.rect.midbottom = screen.get_rect().midbottom

        self.is_swatting = False

    def update(self):
        newpos = pygame.mouse.get_pos()
        if newpos != (0, 0):
            self.rect.center = pygame.mouse.get_pos()
        if self.is_swatting:
            self.rect.move_ip(-35, -35)

    def get_hitbox(self):
        return pygame.Rect((self.rect.x, self.rect.y), (73, 70))

    def swat(self, mosquito):
        self.is_swatting = True
        hitbox = self.get_hitbox()
        if hitbox.colliderect(mosquito.get_hitbox()):
            mosquito.squished()

    def unswat(self):
        self.is_swatting = False


class Mosquito(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('mosquito.png', convert_alpha=True)
        self.original_image = self.image.copy()
        self.squished_image, _ = load_image(
            'squished-mosquito-resized.png', convert_alpha=True)
        
        screen = pygame.display.get_surface()
        self.screen_area = screen.get_rect()
        
        self._set_initial_pos()
        
        self.delta_x = randint(1, 3)
        self.delta_y = randint(1, 3)
        self.CHANGE_DELTA_COUNT = 50
        self.change_delta_counter = self.CHANGE_DELTA_COUNT

        self.is_squished = False
        self.SQUISHED_TIME = 100
        self.time_spent_squished = self.SQUISHED_TIME

    def _set_initial_pos(self):
        self.rect.x = randint(0, self.screen_area.width)
        self.rect.top = 0

    def update(self):
        if self.is_squished:
            if self.time_spent_squished > 0:
                self.time_spent_squished -= 1
                return
            else:
                self._unsquish()
                self.time_spent_squished = self.SQUISHED_TIME
       
        self.change_delta_counter -= 1
        if self.change_delta_counter < 0:
            self.delta_x = randint(1, 3) if self.delta_x > 0 \
                    else -randint(1, 3)
            self.delta_y = randint(1, 3) if self.delta_y > 0 \
                    else -randint(1, 3)
            self.change_delta_counter = self.CHANGE_DELTA_COUNT
       
        self.rect.x += self.delta_x
        self.rect.y += self.delta_y
        if self.rect.top < 0 or self.rect.bottom > self.screen_area.bottom:
            self.delta_y = -self.delta_y
        if self.rect.left < 0 or self.rect.right > self.screen_area.right:
            self.delta_x = -self.delta_x

    # Best guess of a rect that fits around the core mosquito image.
    # Need to do a better job of cropping/centering images.
    def get_hitbox(self):
        return self.rect.inflate(-25, -14)

    def squished(self):
        self.image = self.squished_image
        self.is_squished = True

    def _unsquish(self):
        self.image = self.original_image
        self.is_squished = False
        self._set_initial_pos()


def load_image(filename, convert_alpha=False):
    filepath = os.path.join(data_dir, filename)
    try:
        image = pygame.image.load(filepath)
    except pygame.error:
        raise SystemExit(geterror())
    if convert_alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()
    return image, image.get_rect()


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Mosquito Hunter')
    pygame.mouse.set_visible(False)

    background = pygame.Surface(screen.get_size())
    background.fill((250, 250, 250))
    screen.blit(background, (0, 0))

    fly_swatter = FlySwatter()
    mosquito = Mosquito()
    allsprites = pygame.sprite.Group(mosquito, fly_swatter)

    clock = pygame.time.Clock()

    should_continue = True
    while should_continue:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                should_continue = False
            elif event.type == KEYDOWN and event.key == K_q:
                should_continue = False
            elif event.type == MOUSEBUTTONDOWN:
                fly_swatter.swat(mosquito)
            elif event.type == MOUSEBUTTONUP:
                fly_swatter.unswat()

        allsprites.update()

        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()

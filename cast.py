import pygame
from math import pi, cos, sin, atan2

pygame.mixer.init()
pygame.mixer.music.load('song.mp3')
pygame.mixer.music.play(loops=10, start=0.0)


wall1 = pygame.image.load('./Bricks.png')
wall2 = pygame.image.load('./Brickswdoor.png')
wall3 = pygame.image.load('./Brickswlight.png')
wall4 = pygame.image.load('./Brickswwindow.png')
wall5 = pygame.image.load('./Brickswputin.png')

textures = {
  "1": wall1,
  "2": wall2,
  "3": wall3,
  "4": wall4,
  "5": wall5,
}

hand = pygame.image.load('./handwflashlight.png')

enemies = [
  {
    "x": 100,
    "y": 200,
    "texture": pygame.image.load('./scooby.png')
  },
  {
    "x": 300,
    "y": 190,
    "texture": pygame.image.load('./shaggy.png')
  },
  {
    "x": 225,
    "y": 340,
    "texture": pygame.image.load('./esqueleto.png')
  }
]

class Raycaster(object):
  def __init__(self, screen):
    _, _, self.width, self.height = screen.get_rect()
    self.screen = screen
    self.blocksize = 50
    self.player = {
      "x": self.blocksize + 20,
      "y": self.blocksize + 20,
      "a": pi/3,
      "fov": pi/3
    }
    self.map = []
    self.zbuffer = [-float('inf') for z in range(0, self.width)]
    self.sprite_width = 160
    # self.clear()

  def clear(self):
    for x in range(self.width):
      for y in range(self.height):
        r = int((x/self.width)*255) if x/self.width < 1 else 1
        g = int((y/self.height)*255) if y/self.height < 1 else 1
        b = 0
        color = (r, g, b)
        self.point(x, y, color)

  def point(self, x, y, c = None):
    screen.set_at((x, y), c)

  def load_map(self, filename):
    with open(filename) as f:
      for line in f.readlines():
        self.map.append(list(line))

  def cast_ray(self, a):
    d = 0
    while True:
      x = self.player["x"] + d*cos(a)
      y = self.player["y"] + d*sin(a)

      i = int(x/50)
      j = int(y/50)

      if self.map[j][i] != ' ':
        hitx = x - i*50
        hity = y - j*50

        if 1 < hitx < 49:
          maxhit = hitx
        else:
          maxhit = hity

        tx = int(maxhit * 256 / 50)

        return d, self.map[j][i], tx

      d += 1

  def draw_stake(self, x, h, texture, tx):
    start = int((self.height/2) - h/2)
    end = int((self.height/2) + h/2)
    for y in range(start, end):
      ty = int(((y - start)*256)/(end - start))
      c = texture.get_at((tx, ty))
      self.point(x, y, c)

  def draw_sprite(self, sprite):
    sprite_a = atan2(sprite["y"] - self.player["y"], sprite["x"] - self.player["x"])

    sprite_d = ((self.player["x"] - sprite["x"])**2 + (self.player["y"] - sprite["y"])**2)**0.5
    sprite_size = (self.width/sprite_d) * 70

    sprite_x = (sprite_a - self.player["a"])*self.width/self.player["fov"] + int(self.height/2) - sprite_size/2
    sprite_y = int(self.height/2) - sprite_size/2

    sprite_x = int(sprite_x)
    sprite_y = int(sprite_y)
    sprite_size = int(sprite_size)

    for x in range(sprite_x, sprite_x + sprite_size):
      for y in range(sprite_y, sprite_y + sprite_size):
        if 0 < x < self.width and self.zbuffer[x - self.width] >= sprite_d:
          tx = int((x - sprite_x) * self.sprite_width/sprite_size)
          ty = int((y - sprite_y) * self.sprite_width/sprite_size)
          c = sprite["texture"].get_at((tx, ty))
          if c != (203, 40, 155, 255):
            self.point(x, y, c)
            self.zbuffer[x - self.width] = sprite_d

  def draw_player(self, xi, yi, w = 130, h = 130):
    for x in range(xi, xi + w):
      for y in range(yi, yi + h):
        tx = int((x - xi) * 65/w)
        ty = int((y - yi) * 65/h)
        c = hand.get_at((tx, ty))
        if c != (203, 40, 155, 255):
          self.point(x, y, c)

  def render(self):
    for i in range(0, self.width):
      a =  self.player["a"] - self.player["fov"]/2 + self.player["fov"]*i/self.width
      d, c, tx = self.cast_ray(a)
      x =  i
      h = self.width/(d*cos(a-self.player["a"])) * 70
      self.draw_stake(x, h, textures[c], tx)
      self.zbuffer[i] = d

    for enemy in enemies:
      self.point(enemy["x"], enemy["y"], (0, 0, 0))
      self.draw_sprite(enemy)

    self.draw_player(int(self.height/2) - int(130/2) + 25, self.width - 130)

pygame.init()
screen = pygame.display.set_mode((400, 400), pygame.DOUBLEBUF|pygame.HWACCEL|pygame.HWSURFACE)
screen.set_alpha(None)
r = Raycaster(screen)
r.load_map('./map.txt')

c = 0
while True:
  screen.fill((63, 72, 204))
  r.render()

  for e in pygame.event.get():
    if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
      exit(0)
    if e.type == pygame.KEYDOWN:
      if e.key == pygame.K_LEFT:
        r.player["a"] -= pi/10
      elif e.key == pygame.K_RIGHT:
        r.player["a"] += pi/10
      elif e.key == pygame.K_UP:
        r.player["x"] += cos(r.player["a"]) * 10
        r.player["y"] += sin(r.player["a"]) * 10
      elif e.key == pygame.K_DOWN:
        r.player["x"] -= cos(r.player["a"]) * 10
        r.player["y"] -= sin(r.player["a"]) * 10

  pygame.display.flip()

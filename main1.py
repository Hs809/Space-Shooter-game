import pygame
import os
import time
import random
# from pygame import mixer
pygame.font.init()

WIDTH, HEIGHT = 650, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) # Giving display 
pygame.display.set_caption("Space Shooter Tutorial")


# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Here we create a class of ship to make same attributes for player and enemy 
class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    # Drawing ship
    def draw(self, window):   
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    # Laser collision in the Player Ship
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

                

    # Cooldown meter for laser to shoot from the  ship
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs,objs2):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                for obj in objs2:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):  # we create two rectangel healthbar at same location and reducing the green bar if it hit's
        pygame.draw.rect(window, (255,0,0), (self.x, round(self.y + self.ship_img.get_height() + 10), round(self.ship_img.get_width()), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, round(self.y + self.ship_img.get_height() + 10), round(self.ship_img.get_width() * (self.health/self.max_health)), 10))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height): # laser should not be visible outside the screen
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)





class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER), # dictionary to choose random enemy ship 
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):  # putting laser in lasers 
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2): # checking the  collision between enemy and player ship
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def collide1(obj3, obj4): # checking the  collision between enemy and player ship
    offset_x = obj4.x - obj3.x
    offset_y = obj4.y - obj3.y
    return obj3.mask.overlap(obj4.mask, (offset_x, offset_y)) != None


# Main Loop
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5 #   enemy ships are their in per wave
    enemy_vel = 1

    player_vel = 5
    laser_vel = 10

    player = Player(300, 630)
    player2 = Player(500, 500)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    # Space shooting song
    # file = 's1.mp3'
    # mixer.init()
    # mixer.music.load(file)
    # mixer.music.play()

    def redraw_window(): # here we draw all the the things
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))



        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)
        player2.draw(WIN)

        # if lost:
        #     mixer.music.stop()
        #     lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
        #     WIN.blit(lost_label, (round(WIDTH/2 - lost_label.get_width()/2), 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0 or player2.health<= 0:
            lost = True
            lost_count += 1

        if lost: # to see if player is lost
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0: # if enemies list is over increase the level and waveleangth
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)# appending the enemy in enemies with random

        for event in pygame.event.get(): # to check if we click on cancel button
            if event.type == pygame.QUIT:
                quit()
        # pressing the key and implementing the operation
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and (player.x - player_vel > 0) and (player2.x - player_vel > 0): # left
            player.x -= player_vel
            player2.x -= player_vel
        if keys[pygame.K_RIGHT] and (player.x + player_vel + player2.get_width() < WIDTH) and (player2.x + player_vel + player2.get_width() < WIDTH): # right
            player.x += player_vel
            player2.x += player_vel
        if keys[pygame.K_UP] and (player.y - player_vel > 0) and (player2.y - player_vel > 0): # up
            player.y -= player_vel
            player2.y -= player_vel
        if keys[pygame.K_DOWN] and (player.y + player_vel + player.get_height() + 15 < HEIGHT)  and (player2.y + player_vel + player2.get_height() + 15 < HEIGHT): # down
            player.y += player_vel
            player2.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            player2.shoot()
        # Player 2 movements


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1: #it shoots
                enemy.shoot()

            if collide(enemy, player): # if it collide with player then reduce health
                player.health -= 10
                enemies.remove(enemy)
            if collide1(enemy, player2): # if it collide with player then reduce health
                player2.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT: # if it goes off screen then reduce the lives
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)
        player2.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (round(WIDTH/2 - title_label.get_width()/2), 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()

import pygame
from pygame.locals import *
import os
import cv2

# Game Initialization
pygame.init()
# Game Resolution
screen_width = 800
screen_height = 600
player_sprite_width = 50
player_sprite_height = 50
pygame.mixer.quit() 
FPS = 30
steps = 1
 
# Colors
white  = (255, 255, 255)
black  = (0, 0, 0)
gray   = (50, 50, 50)
red    = (255, 0, 0)
green  = (0, 255, 0)
blue   = (0, 0, 255)
yellow = (255, 255, 0)
ani    = 4 

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0
        self.movey = 0
        self.frame = 0
        self.images = []
        for i in range(1,5):
            img = pygame.image.load(os.path.join('assets/player', 'run-' + str(i) + '.png')).convert_alpha()
            self.images.append(img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

    def control(self,x,y):
        self.movex += x
        self.movey += y

    def update(self):

        # Check boundaries
        if self.rect.x+self.movex<=0:
            self.movex=0

        if self.rect.x+self.movex+player_sprite_width>=screen_width:
            self.movex=0

        if self.rect.y+self.movey<=0:
            self.movey=0

        if self.rect.y+self.movey+player_sprite_height>=screen_height:
            self.movey=0

        self.rect.x = self.rect.x + self.movex
        self.rect.y = self.rect.y + self.movey    

        if self.movex < 0:
            self.frame += 1
            if self.frame > 3*ani:
                self.frame = 0
            self.image = pygame.transform.flip(self.images[self.frame // ani], True, False)

        # moving right
        if self.movex > 0:
            self.frame += 1
            if self.frame > 3*ani:
                self.frame = 0
            self.image = self.images[self.frame//ani]

        if self.movey < 0:
            self.frame += 1
            if self.frame > 3*ani:
                self.frame = 0
            self.image = pygame.transform.flip(self.images[self.frame // ani], True, False)

        if self.movey > 0:
            self.frame += 1
            if self.frame > 3*ani:
                self.frame = 0
            self.image = self.images[self.frame//ani] 
        

class Button(object):
    def __init__(self, position, size, color, text):
        self.image = pygame.Surface(size)
        self.rect = pygame.Rect((0,0), size)
        font =  pygame.font.Font(None,32)
        text1 = font.render(text, True, white)
        text_rect = text1.get_rect()
        self.image.blit(text1, text_rect)
        self.rect.topleft = position

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self.rect.collidepoint(event.pos)

class Stage():
    def __init__ (self):
        self.level      = 0
        self.entries    = [(700,500),(50,350),(0,0)]
        self.exits      =   [   [(790,500,10,100,1)],
                                [(50,450,10,100,0),(790,500,10,100,2)],
                                [(790,500,10,100,3)]
                            ]
        self.current_exits = [x for x in self.exits[self.level] ]
        self.boundaries    =    [   [(475,350),(575,350),(500,550),(300,550),],
                                    [(0,0),(100,100),(200,200)],
                                    [(0,0),(100,100),(200,200)]
                                ]
          
        self.player = Player()  
        self.player.rect.x = 500
        self.player.rect.y = 300
        self.player_list = pygame.sprite.Group()
        self.player_list.add(self.player)
      
        self.images = []
        
        #80x60 screenwidth/10 x screenheight/10
        self.path_list = [[0]*80]*60

        for i in range(1,5):
            img = pygame.image.load(os.path.join('.//assets//stages//',  str(i) + '.png')).convert()
            img = pygame.transform.scale(img,((screen_width,screen_height)))
            self.images.append(img)
            self.image = self.images[self.level]
            self.rect = self.image.get_rect()

    def update_stage_level(self,level):
        self.level = level
        self.player.movex = 0
        self.player.movey = 0
        self.image = self.images[self.level]
        self.rect  = self.image.get_rect()
        self.player.rect.x = self.entries[self.level][0]
        self.player.rect.y = self.entries[self.level][1]
        self.current_exits = [x for x in self.exits[self.level] ]
          

    def draw(self,screen):
        screen.blit(self.image,self.rect)
        for x in self.current_exits:
            rect = Rect(x[0],x[1],x[2],x[3])
            pygame.draw.rect(screen,green,rect)
        
        pygame.draw.polygon(screen,red,self.boundaries[self.level])     
        self.player_list.draw(screen)

    def check_entrance_collision(self):
        for x in self.current_exits:
            rect = Rect(x[0],x[1],x[2],x[3])
            if rect.colliderect(self.player.rect):
                self.update_stage_level(x[4])
                return 
        

def display_stages(screen):
    stages  = Stage()
    clock   = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            keys = pygame.key.get_pressed()  # This will give us a dictonary where each key has a value of 1 or 0. Where 1 is pressed and 0 is not pressed.
            
            # Blocks double pressing for increased speed
            if keys[pygame.K_LEFT]: 
                if stages.player.movex >=0:
                    stages.player.control(-steps, 0)
            if keys[pygame.K_RIGHT]:
                if stages.player.movex <= 0:
                    stages.player.control(steps, 0)
            if keys[pygame.K_UP]:
                if stages.player.movey >= 0:
                    stages.player.control(0, -steps)
            if keys[pygame.K_DOWN]:
                if stages.player.movey <= 0:
                    stages.player.control(0, steps)


        screen.fill(white) 
        stages.check_entrance_collision()
        stages.player.update()        
        stages.draw(screen)   
        pygame.display.flip()
        clock.tick(FPS)

def start():
    
    screen  = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Legend of Dragoon")
    size    = (150,75)
    button1 = Button(((screen_width/2)-size[1], (screen_height/2)), size, black, "New Game")
    button2 = Button(((screen_width/2)-size[1], (screen_height/2)+size[0]/2), size, black, "EXIT")
    """     
    logo    = pygame.image.load(".//assets//LegendOfDragoonLogo.png").convert()
    logo.convert_alpha()  
    logo.set_colorkey(black)  
    logo    = pygame.transform.scale(logo,((screen_width),300)) 
    """
    clock   = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

            if button1.is_clicked(event):
                display_stages(screen)
            if button2.is_clicked(event):
                pygame.quit()
                exit()

        screen.fill(white)    
        #screen.blit(logo,(0,0))
        button1.draw(screen)
        button2.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__=="__main__":
    start()

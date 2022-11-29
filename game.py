import pygame
from pygame.locals import *
import os
import cv2
from ffpyplayer.player import MediaPlayer
from datetime import datetime
import random
from collections import OrderedDict
from math import cos, sin, pi

# Game Initialization
pygame.init()
pygame.mixer.init()
#pygame.mixer.quit() 

# Game Resolution
screen_width            = 800
screen_height           = 600
player_sprite_width     = 25
player_sprite_height    = 45
FPS                     = 30
steps                   = 1

# Colors
white  = (255, 255, 255)
black  = (0, 0, 0)
gray   = (50, 50, 50)
red    = (255, 0, 0)
green  = (0, 255, 0)
blue   = (0, 0, 255)
blueviolet = (138,43,226)
yellow = (255, 255, 0)
orange = (255,165,0)
dialog_background = (0, 0, 255, 200)

#name, level, hp, attack, weapon(row,col), addition index(Pass the same to Lavitz/Albert due to count)
base_stats = [('Dart',1,0,15,2,0,0,0),('Lavitz',None,1,17,3,1,0,1),('Shana',None,2,12,1,2,0,2)]
#
class Spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except:
            print ('Unable to load spritesheet image:')
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size,pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey ==-1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

class Chest(pygame.sprite.Sprite):
    def __init__(self,position,id,quantity,type_unlocked):
        pygame.sprite.Sprite.__init__(self)
        self.item_id = id
        self.quantity = quantity
        #What can I unlock from chest? item, armour, weapon(0,1,2)
        self.type_unlocked = type_unlocked
        self.all_spritesheets = Spritesheet(os.path.join('assets/sprites', 'sprites.png'))
        self.image = self.all_spritesheets.image_at((7.5+(1*15),42.5,15,20), colorkey=black)
        self.rect = self.image.get_rect()
        self.rect.topleft = position

    def draw(self,screen):
        screen.blit(self.image,self.rect)

class Npc(pygame.sprite.Sprite):
    def __init__(self,position,images,stats=None):
        #print(images)
        pygame.sprite.Sprite.__init__(self)
        if stats != None:
            self.name,self.level,self.hp,self.attack = stats
            self.current_hp = self.hp
        #print(images)
        self.images = images
        #0-IDLE, 1-DEAD
        self.state = 0
        self.frame = 0
       
        self.image = self.images[self.state][self.frame] 
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.font = pygame.font.Font(None,32)

        """
        There are 8 status ailments
        Poison, Stun, Arm-blocking,Confusion,Bewitchment, Fear, Despirit,Petrification, Can't Combat
        """
        self.status = [-1]*8

    def update(self):
        if self.state == 0:
            self.frame += 1
            if self.frame >= len(self.images[self.state]):
                self.frame = 0

        if self.state == 1:
            if self.frame < len(self.images[self.state])-1:
                self.frame += 1

        self.image = self.images[self.state][self.frame]

    def take_damage(self,damage):
        if damage < 0:
            self.current_hp=self.current_hp-damage if self.current_hp-damage<self.hp else self.hp
        else:
            if (self.current_hp-damage) > 0:
                self.current_hp-=damage 
            else:
                self.current_hp = 0
                self.state = 1
                self.frame = 0

    def draw(self,screen):
        screen.blit(self.image,self.rect)

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0
        self.movey = 0
        self.frames = [0]*12
        player_movement_spritesheets = Spritesheet(os.path.join('assets/player', 'movement.png'))
        self.sprites = []
        for i in range(4):
            for j in range(4):
                self.sprites.append((0, i*(5+player_sprite_height), (player_sprite_width+7)*(j+1), player_sprite_height))
        #print(self.sprites)
        self.images = player_movement_spritesheets.images_at(self.sprites, black)
        self.ani = 4
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = [x,y]

    def control(self,x,y):
        self.movex += x
        self.movey += y

    """
    Boundary is a 2d array where self.boundaries[self.level][0][self.boundary_index] returns which boundary it should stay in
    """
    def update(self,boundary):
        #Rework to use frames to go through a walking animation (ToDo)
        if self.movex > 0: 
            if self.movey > 0:
                self.image = self.images[8]
                self.image = pygame.transform.rotate(self.image, -23)
                self.image.set_colorkey(black)
            elif self.movey < 0:
                self.image = self.images[8]
                self.image = pygame.transform.rotate(self.image, 23)
                self.image.set_colorkey(black)
            else:
                self.image = self.images[8]
        elif self.movex < 0:
            if self.movey > 0:
                self.image = self.images[4]
                self.image = pygame.transform.rotate(self.image, 23)
                self.image.set_colorkey(black)
            elif self.movey < 0:
                self.image = self.images[4]
                self.image = pygame.transform.rotate(self.image, -23)
                self.image.set_colorkey(black)
            else:
                self.image = self.images[4]
        else:
            if self.movey > 0:
                self.image = self.images[0]
            elif self.movey < 0:
                self.image = self.images[12]
            else:
                self.image = self.images[0]

        cage_mask_image = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        pygame.draw.polygon(cage_mask_image, white, boundary)
        cage_mask = pygame.mask.from_surface(cage_mask_image)
        cage_rect = cage_mask.get_rect()
        player_mask = pygame.mask.from_surface(self.image)
        player_mask_count = player_mask.count() 
        #print(cage_mask.count())
        new_rect = self.rect.copy()
        new_rect.x += self.movex
        new_rect.y += self.movey
        offset_x = new_rect.x - cage_rect.x
        offset_y = new_rect.y - cage_rect.y
        overlap_count = cage_mask.overlap_area(player_mask, (offset_x, offset_y))
        if overlap_count == player_mask_count:
            self.rect = new_rect

class Cutscene():
    def __init__(self):
        self.level = 0
        self.next_state = [-1,-1,-1,0]
        #Unlocks each player or dragoon per cutscene
        self.unlock_players = [0, None, 1, 2]
        self.unlock_dragoons = [0, None, None, None]

        #Reworked to use dialogs per cutscene video with multiple dialogs in concession
        self.dialog = [['The Green Tusked Dragon, Feyrbrand.'],
                       ['Hmm, "Chance of war more likely".'],
                       ["I hope it's just a rumor."],
                       ['...']
                      ]
        self.dialog_pos = [[(100,100)],
                           [(100,300)],
                           [(100,300)],
                           [(100,300)],
                          ]
        self.dialog_sizes = [[(450,32)],
                             [(450,32)],
                             [(400,32)],
                             [(200,32)]
                            ] 
        self.filenames = []
        for i in range(1,5):
            self.filenames.append(os.path.join('.//assets//cutscenes//',  str(i) + '.mp4'))

class Dialog():
    #I need to change it so that when I update, the dialog, position and size change.
    #This needs to be Initialized once where cutscenes and npc dialogs work.
    def __init__(self,values):
        #print(values)
        self.positions,self.sizes,self.dialogs,self.is_cutscene = values
        self.index = 0
        if len(self.dialogs)!=0:
            self.size = self.sizes[self.index]
            self.position = self.positions[self.index]
            self.image = pygame.Surface(self.size, pygame.SRCALPHA)
            self.font = pygame.font.Font(None,32)
            self.rect = self.image.get_rect()
            self.rect.topleft = self.position
            self.dialog_text_offset = 5
            self.text_renders = [self.font.render(text, True, white) for text in self.dialogs]

    def update(self): 
        #print(self.index,len(self.dialogs))
        if len(self.dialogs)!=0 and self.index < len(self.dialogs):
            self.size = self.sizes[self.index]
            self.position = self.positions[self.index]
            self.rect.topleft = self.position
            self.index  += 1
        
    def draw(self,screen):
        if self.is_cutscene:
            try:
                last_screen = pygame.image.load(os.path.join('.//assets//screenshots//last_screen.png'))
                screen.blit(last_screen,(0,0))
            except Exception as e:
                print(str(e))
                pass
        if len(self.dialogs)!=0 and self.index < len(self.dialogs):
            #print(self.dialogs[self.index])
            self.image.blit(self.text_renders[self.index], (self.dialog_text_offset,self.dialog_text_offset))
            screen.blit(self.image, self.rect)  
            if self.is_cutscene: 
                pygame.draw.rect(self.image, dialog_background, self.image.get_rect())
                pygame.draw.rect(self.image, yellow, self.image.get_rect(),width=self.dialog_text_offset)

class Button(object):
    def __init__(self, x,y,width,height, color, text):
        self.font = pygame.font.Font(None,32)
        self.text = self.font.render(text, True, color)
        self.rect = self.text.get_rect(center=(x+(width/2), y+(height/2)))

    def draw(self, screen):
        screen.blit(self.text, self.rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self.rect.collidepoint(event.pos)

class Stage():
    def __init__ (self):
        self.level      = 0
        self.boundary_index = 0
        self.images = []

        for i in range(1,3):
            img = pygame.image.load(os.path.join('.//assets//stages//',  str(i) + '.png')).convert()
            img = pygame.transform.scale(img,((screen_width,screen_height)))
            self.images.append(img)

        self.image = self.images[self.level]
        self.rect = self.image.get_rect()
        # Exit dimension (x,y), width, height , level(-1=cutscene,-2=map,any=level), boundary, player (x,y)
        # Rework update to include the screen_width into the calculations
        self.exits      =   [   
                                [(0,500,10,50,1,0,740,500)],
                                [(790,500,10,50,0,1,50,500)],

                                """                                 
                                [(790,500,10,50,1,0,0,350)],
                                [(0,450,50,10,0,0,700,500),(790,500,10,100,2,0,0,0)],
                                [(790,500,10,100,3,0,0,0)] 
                                """
                            ]
        self.current_exits = [x for x in self.exits[self.level] ]
        # Boundaries (x,y)
        self.boundaries    =    [   [[(200,0),(400,0),(500,350),(300,350)],[(300,400),(360,400),(300,500),(500,500),(500,550),(0,550),(0,500)]],
                                    [[(475,350),(575,350),(575,500),(800,500),(800,550),(300,550),(300,500)]],
                                    """
                                    [[(475,350),(575,350),(575,500),(800,500),(800,550),(300,550),(300,500)]],
                                    [[(0,450),(50,450),(100,200),(0,200)]],
                                    [[(0,0),(100,100),(200,200)]],
                                    """
                                ]
        #Make sure the entrance exit is beyond the player sprite size
        #x, y, width, height, boundary_index exit x, y
        self.boundary_hopper =  [  [[300,340,25,10,1,290,410],[300,400,25,10,0,300,250]],
                                    [[]]

                                ]

        
        self.player = Player(300,50)  
        #Initial start position
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        #For a single level if there are multiple npcs x,y 
        self.npc_sprite_sheet = Spritesheet(os.path.join('assets/sprites', 'npc.png'))
        self.npc_images = [[[self.npc_sprite_sheet.image_at((135+(80*i),20,65,50), colorkey=black) for i in range(7)
                            ]]
                          ]
        
        self.npcs = [ [[450,500,0],[300,300,0]],
                      [[450,500,0],[300,300,0]],
                    ]  

        self.npc_dialogue = [[['Hi','Bye'],['Hi','Bye']],
                             [['Hi','Bye'],['Hi','Bye']],
                            ]           
        self.npc_dialogue_sizes = [[[(25,50),(25,50)],[(25,50),(25,50)]],
                                   [[(25,50),(25,50)],[(25,50),(25,50)]]
                                  ]
          
        self.npc_list = pygame.sprite.Group()
        for npc in self.npcs[self.level]:
            new_npc = Npc((npc[0],npc[1]),self.npc_images[npc[2]])
            self.npc_list.add(new_npc)
        
        self.battle_backgrounds = []
        #Position and a list for enemies id x,y,[ids]
        self.enemy_positions = [[[450,500,50,50,[0,1]]],
                                [[100,100,100,100,[0,1,0]]]
                               ]
        self.enemy_images = [[[self.npc_sprite_sheet.image_at((135+(80*i),20,65,50), colorkey=black) for i in range(7)],
                              [self.npc_sprite_sheet.image_at((135+(80*i),397,65,68), colorkey=black) for i in range(7)]],
                             [[self.npc_sprite_sheet.image_at((135+(80*i),20,65,50), colorkey=black) for i in range(7)]], 
                            ]
        self.enemy_base_stats = [['Knight',1,5,3],['Commander',1,15,5]]

        #This is for random battles
        self.enemies_by_level = [[0],[0],[0]]

        #Place an item with the id ,location, quantity, either item,armor,weapon
        self.chest_list = pygame.sprite.Group()
        self.chest_locations = [[[0,400,500,1,0]],
                                [[0,100,100,1,0]]
                            ]

        for item in self.chest_locations[self.level]:
            new_item = Chest((item[1],item[2]),item[0],item[3],item[4])
            self.chest_list.add(new_item)
        
    #Check if exit is a cutscene then proceed to change self.state to -1, or -2 to a map, 0 to normal. 
    def update_stage_level(self,level,index,x,y):
        self.boundary_index = index
        if level ==-1: 
            self.level += 1
            self.npc_list = pygame.sprite.Group()
            #x,y,size,path_list
            for npc in self.npcs[self.level]:
                new_npc = Npc((npc[0],npc[1]),self.npc_images[npc[2]])
                self.npc_list.add(new_npc)
            self.chest_list = pygame.sprite.Group()
            for item in self.chest_locations[self.level]:
                new_item = Chest((item[1],item[2]),item[0],item[3],item[4])
                self.chest_list.add(new_item)
        elif level == -2:
            pass
        else:
            self.level = level
            self.npc_list = pygame.sprite.Group()
            #x,y,size,path_list
            for npc in self.npcs[self.level]:
                new_npc = Npc((npc[0],npc[1]),self.npc_images[npc[2]])
                self.npc_list.add(new_npc)
            self.chest_list = pygame.sprite.Group()
            for item in self.chest_locations[self.level]:
                new_item = Chest((item[1],item[2]),item[0],item[3],item[4])
                self.chest_list.add(new_item)
        self.player.movex = 0
        self.player.movey = 0

        if self.level < len(self.exits):
            self.image = self.images[self.level]
            self.rect  = self.image.get_rect()
            self.player.rect.x = x
            self.player.rect.y = y
            self.current_exits = [x for x in self.exits[self.level] ]      

    def update_boundary_hop(self,x,y,index):
        self.player.movex=0
        self.player.movey=0
        self.player.rect.x=x
        self.player.rect.y=y
        self.boundary_index=index

    def draw(self,screen):
        if self.level < len(self.boundaries):
            screen.blit(self.image,self.rect)
            for hop in self.boundary_hopper[self.level]:
                if len(hop)!=0:
                    rect = Rect(hop[0],hop[1],hop[2],hop[3])
                    pygame.draw.rect(screen,green,rect)
            for x in self.current_exits:
                rect = Rect(x[0],x[1],x[2],x[3])
                pygame.draw.rect(screen,green,rect)
            for boundary in self.boundaries[self.level]:
                pygame.draw.polygon(screen,red,boundary,1) 
            for x in self.enemy_positions[self.level]:
                rect = Rect(x[0],x[1],x[2],x[3])
                pygame.draw.rect(screen,yellow,rect)
            self.all_sprites.draw(screen)  
            self.npc_list.draw(screen) 
            self.chest_list.draw(screen)

#Base level is always Dart's level, hp, attack dmg
class Character():
    #Calculate the other stats (ToDo) 
    def __init__(self,character_values):
        (name,level,d_index,hp,attack,row_id,col_id,addition_index) = character_values
        self.name = name
        self.level = level

        #First weapon to use
        self.weapon_row = row_id
        self.weapon_col = col_id

        #Which set of additions to use aka all of Dart's (0)
        self.addition_index = addition_index

        #Basically d_index corresponds to the dragoon you can use
        self.d_index = d_index
        self.d_level = 0

        self.current_sp  = 0
        self.sp = self.d_level*100
        self.mp = self.d_level*20
        self.current_mp = self.mp

        self.base_hp = hp    
        self.hp = self.base_hp+(self.level*15)
        self.current_hp = self.hp

        self.current_exp = 0
        self.exp = self.level*100

        self.base_attack = attack

        """
        There are 8 status ailments
        Poison, Stun, Arm-blocking, Confusion, Bewitchment, Fear, Despirit, Petrification, Can't Combat
        """
        self.status = [-1]*7
        self.is_defending = False
        self.in_dragoon = False

    def update_stats(self,inventory):
        self.d_level = inventory.d_level[self.d_index]
        self.sp = self.d_level*100
        self.current_sp = self.sp
        self.mp = self.d_level*20
        self.current_mp = self.mp

    def take_damage(self,damage):
        if damage < 0:
            self.current_hp=self.current_hp-damage if self.current_hp-damage<self.hp else self.hp
        else:
            self.current_hp=self.current_hp-damage if (self.current_hp-damage)>0 else 0


class Menu():
    def __init__(self):
        self.size = (screen_width,screen_height)
        self.image  = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = pygame.Rect((0,0), self.size)
        self.font   = pygame.font.Font(None,32)
        img = pygame.image.load(os.path.join('.//assets//menu//background.png')).convert()
        self.bg = pygame.transform.scale(img,((screen_width,screen_height)))
        #Which page of the menu and what selected everytime I move a page just make selected 0
        self.selected = 0
        self.index = 0
        self.options = ['Status','Item','Armed','Addition','Replace','Config','Save']

    def draw_main(self,screen,inventory,stages):
        offset = 30
        total_height = 0
        width = (screen_width/2)-(2*offset)
        """
        Title, Selections and Gold, Time and Dragoons
        """
        for i in range(3):
            pos = (offset,total_height+offset)
            if i == 0:
                stage_level = self.font.render(str(stages.level), True, white)
                self.image.blit(stage_level,((pos[0],pos[1])))
                total_height += ((screen_height-(2*offset))/4)
            elif i == 1:
                for j in range(len(self.options)):
                    if j == self.selected and self.index != 2:
                        color = red
                    else:
                        color = white
                    option = self.font.render(self.options[j], True, color)
                    rect = option.get_rect(center=(pos[0]+(width/4), pos[1]+((j+1)*offset)+(offset/2)))
                    self.image.blit(option,rect)
                    
                total_height += ((screen_height-(2*offset))/2)
            else:
                gold = self.font.render('GOLD '+str(inventory.gold), True, white)
                self.image.blit(gold,((pos[0],pos[1])))
                time = datetime.now()- inventory.start_time
                #print(time)
                total_time = self.font.render(str(time), True, white)
                self.image.blit(total_time,((pos[0]+100,pos[1])))
                for i in range(len(inventory.unlocked_dragoons)):
                    if inventory.d_usability[i] != None:
                        self.image.blit(inventory.dragoons[3+(4*i)],((pos[0]+(20*i),pos[1]+offset)))
                total_height += ((screen_height-(2*offset))/4)
        """
        Item List
        Grab a subsection of values from my dict
        self.selected -> Number of items
        """
        
        if self.index == 2:
            print('Display Item List')
            items = list(inventory.items.items())[self.selected:self.selected+5]
            print(items)
            for i in range(len(items)):
                pos = (offset+offset/2+screen_width/4,((screen_height-(2*offset))/4)+offset+((2)*offset)+(offset/2)+(i*30))
                print(pos)
                print(items[i])
                if i == self.selected:
                    color = red
                else:
                    color = white
                item = self.font.render(str(items[i]), True, color)
                rect = item.get_rect(center=(pos))
                self.image.blit(item,rect)
            
        """
        Character stats
        """
        height = ((screen_height-(2*offset))/3)
        for i in range(len(inventory.team)):
            pos = (((screen_width/2)+offset),((height*i)+offset))
            #Rework this (ToDo)
            avatar = pygame.transform.smoothscale(inventory.avatars[inventory.team[i]],((inventory.avatar_size,inventory.avatar_size)))
            self.image.blit(avatar,pos)
            name = self.font.render(str(inventory.unlocked_team[inventory.team[i]].name), True, black)
            self.image.blit(name,((pos[0]+inventory.avatar_size,pos[1])))
            level = self.font.render('LV '+str(inventory.unlocked_team[inventory.team[i]].level), True, white)
            self.image.blit(level,((pos[0]+100+inventory.avatar_size),pos[1]))
            dlevel = self.font.render("D'LV "+ str(inventory.unlocked_team[inventory.team[i]].d_level), True, white)
            self.image.blit(dlevel,((pos[0]+inventory.avatar_size),(pos[1]+offset)))
            sp = self.font.render('SP '+str(inventory.unlocked_team[inventory.team[i]].current_sp), True, white)
            self.image.blit(sp,((pos[0]+100+inventory.avatar_size),(pos[1]+offset)))
            hp = self.font.render('HP '+str(inventory.unlocked_team[inventory.team[i]].current_hp)+'/'+str(inventory.unlocked_team[inventory.team[i]].hp), True, white)
            self.image.blit(hp,((pos[0]+inventory.avatar_size),(pos[1]+(offset*2))))
            mp = self.font.render('MP '+str(inventory.unlocked_team[inventory.team[i]].current_mp)+'/'+str(inventory.unlocked_team[inventory.team[i]].mp), True, white)
            self.image.blit(mp,((pos[0]+inventory.avatar_size),(pos[1]+(offset*3))))
            exp = self.font.render('EXP '+str(inventory.unlocked_team[inventory.team[i]].current_exp)+'/'+str(inventory.unlocked_team[inventory.team[i]].exp), True, white)
            self.image.blit(exp,((pos[0]+inventory.avatar_size),(pos[1]+(offset*4))))

        screen.blit(self.image,self.rect)

        """
        Menu option outlines
        """
        total_height = 0
        for i in range(3):
            pos = (offset,total_height+offset)
            if i==1:
                for j in range(1,len(self.options)):
                    pygame.draw.line(screen, black, (pos[0],pos[1]+((j+1)*offset)),(pos[0]+width,pos[1]+((j+1)*offset)), 1) 
                height = ((screen_height-(2*offset))/2)
                points = [pos,(pos[0]+width,pos[1]),(pos[0]+width,pos[1]+height ),(pos[0],pos[1]+height)]
                pygame.draw.polygon(screen,black,points,1)
                total_height += height
            else:
                height=((screen_height-(2*offset))/4)
                points = [pos,(pos[0]+width,pos[1]),(pos[0]+width,pos[1]+height ),(pos[0],pos[1]+height)]
                pygame.draw.polygon(screen,black,points,1)
                total_height += height
        """
        Character box outline
        """
        for i in range(3):  
            height = ((screen_height-(2*offset))/3)
            pos = (((screen_width/2)+offset),((height*i)+offset))
            points = [pos,(pos[0]+width,pos[1]),(pos[0]+width,pos[1]+height),(pos[0],pos[1]+height)]
            pygame.draw.polygon(screen,black,points,1)
        return inventory

    def draw_replace(self,screen,inventory):
        for i in range(len(inventory.unlocked_team)):
            #print(inventory.unlocked_team[i] )
            if inventory.unlocked_team[i] != None and inventory.team_usability[i] != None  :
                avatar = pygame.transform.smoothscale(inventory.avatars[i],((screen_width//len(inventory.unlocked_team)),inventory.avatar_size))
                self.image.blit(avatar,((i*(screen_width//len(inventory.unlocked_team))),0))
        screen.blit(self.image,self.rect)
        return inventory

    def draw(self,screen,inventory,stages):
        """
        First start with background
        Then add all the menu options and images (selectively)
        Use enter to input new menu selection
        Also go display font using self.image.blit then pygame.draw for any shapes
        """
        self.image.blit(self.bg,self.rect)
        #If index is 0 or 1 draw main but with items opened else draw the rest
        if self.index == 0 or self.index == 2:
            inventory = self.draw_main(screen, inventory, stages)
        elif self.index == 5:
            inventory = self.draw_replace(screen,inventory)
        return inventory
             
class Inventory():
    def __init__(self):
        
        #Name, Attack Damage, Buy, Sell, Effect, Who uses it 
        #46 unique ones related to certain chars
        self.all_weapons = [[['Broad Sword',2,None,10,None,[0]],
                             ['Bastard Sword',7,60,30,None,[0]],
                             [],[],[],[],[],[]],
                            [['Spear',4,None,10,None,[1,7]],
                             [],[],[],[],[],[]],
                            [['Short Bow',3,None,10,None,[2,8]],
                             [],[],[],[],[],[]]
                            ]
        #Name, Type, Field, Is flat, amount, Targets(Multi), Alive(is targets alive), Targeting Players
        self.all_items = [['Health Potion','Recover','Hp',False,50,False,True, True]]
        self.items = OrderedDict()
        """
        Scroll Testing for items in menu
        for i in range(14):
            self.items[str(i)]=1
        """
        
        self.weapons = {}
        """
        Basically add the primary weapons on new game.
        """
        for primary in self.all_weapons:
            self.update_weapon(primary[0],1)

        #Name, sp, hits, level to obtain, time between attacks, damage modifiers
        self.all_additions = [[['Double Slash',[35]*5,2,0,[5,3],[150,157,165,187,202]],['Volcano',[20+(i*4) for i in range(5)],3,2,[5,4,3],[200,210,220,230,250]]],
                              [['Harpoon',[35,38,42,45,50],2,0,[5,3],[100,110,120,130,150]],['Spinning Cane',[35]*5,3,5,[5,4,3],[125+(25*i)for i in range(5)]]],
                              [['Shoot',[50]*5,1,0,[1],[100]*5]]
                            ]
                    
        self.addition_counts = [[0]*len(self.all_additions[i]) for i in range(len(self.all_additions))]
        self.selected_additions = [0]*9

        self.team = []
        self.unlocked_team = [None]*9
        self.team_usability = [None]*9
        self.unlocked_dragoons = [None]*8
        self.d_usability = [None]*8
        self.d_level = [1]*8
        self.d_exp = [0]*8
        self.d_levels = [100,2000,6000,20000]
        self.gold = 0
        self.stardust = 0
        """
        New game start time
        """
        self.total_time = 0
        self.start_time = datetime.now()
        """
        Start time - current time = total_time
        Save point: add to total, then change start time
        """
        self.avatars = []
        self.avatar_size = 150

        #Have to store unscaled versions and then scale within functions
        self.all_spritesheets = Spritesheet(os.path.join('assets/sprites', 'sprites.png'))
        for i in range(9):
            img = self.all_spritesheets.image_at(((3*(i+1))+(i*25), 166 ,25, 32), colorkey=black)
            #img = pygame.transform.smoothscale(img,((self.avatar_size,self.avatar_size)))
            self.avatars.append(img) 

        self.dragoons = []
        for i in range(8):
            for j in range(4):
                img = self.all_spritesheets.image_at((50+(20*j),5+(20*i),20,20), colorkey=black)
                self.dragoons.append(img)

        self.attack_sprites = []

        self.attack_sprite_locations=[[8,15,0,15,25],[7.5,15,25,15,15],[7.5,15,42.5,15,20],
                                      [7.5,15,62.5,15,20],[8,15,80.5,15,20],[7.5,15,100,15,18]
                                      ,[8,15,117.5,15,20],[7.5,15,140,15,2]]

        for location in self.attack_sprite_locations:
            #print(location)
            for i in range(3):
                img = self.all_spritesheets.image_at((location[0]+(i*location[1]),location[2],location[3],location[4]), colorkey=black)
                self.attack_sprites.append(img)
        
    def update_item(self,id,quantity):
        self.items[self.all_items[id][0]] = self.items.get(self.all_items[id][0],0) + quantity
        if self.items[self.all_items[id][0]]<=0:
            self.items.pop(self.all_items[id][0])

    def update_weapon(self,id,quantity):
        self.weapons[id[0]] = self.weapons.get(id[0],0) + quantity
            
class Game():
    def __init__(self):
        self.stages = Stage()
        self.cutscenes  = Cutscene()
        self.menu = Menu()
        self.inventory = Inventory()
        self.state =  -1
        
    def display_dialog(self,screen):
        clock = pygame.time.Clock()
        running = True

        dialog_positions = self.cutscenes.dialog_pos[self.cutscenes.level]
        dialogs          = self.cutscenes.dialog[self.cutscenes.level]
        #Restrict size to a certain size
        sizes            =  self.cutscenes.dialog_sizes[self.cutscenes.level]
        #print(sizes,dialog_positions,dialogs)
        cutscenes_dialog =  Dialog([dialog_positions,sizes,dialogs,True])  
        
        while running: 
            #print(cutscenes_dialog.index,len(cutscenes_dialog.sizes))
            if cutscenes_dialog.index >= len(cutscenes_dialog.dialogs):
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                keys = pygame.key.get_pressed()  # This will give us a dictonary where each key has a value of 1 or 0. Where 1 is pressed and 0 is not pressed.
                if keys[pygame.K_RETURN] and cutscenes_dialog.index <= len(cutscenes_dialog.dialogs)-1:
                    cutscenes_dialog.update()
            
            screen.fill(white) 
            #print(cutscenes_dialog.index)
            cutscenes_dialog.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)     

    def display_menu(self,screen):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                keys = pygame.key.get_pressed()  
                if keys[pygame.K_RETURN]:
                    print('Clicked on menu item') 
                    if self.menu.index == 0:
                        if self.menu.options[self.menu.selected] =='Item':
                            self.menu.selected = 0
                            self.menu.index = 2
                        if self.menu.options[self.menu.selected] =='Replace':
                            self.menu.selected = 0
                            self.menu.index = 5
                        
                if keys[pygame.K_LEFT]:
                    pass
                if keys[pygame.K_RIGHT]:
                    pass
                if keys[pygame.K_UP]:
                    if self.menu.index == 0:
                        if self.menu.selected > 0:
                            self.menu.selected -= 1 
                    if self.menu.index == 2:
                        if self.menu.selected > 0:
                            self.menu.selected -= 1 
                if keys[pygame.K_DOWN]:
                    if self.menu.index == 0:
                        if self.menu.selected < len(self.menu.options)-1:
                            self.menu.selected += 1 
                    if self.menu.index == 2:
                        if self.menu.selected < len(self.inventory.items)-1:
                            self.menu.selected += 1 
                    
                if keys[pygame.K_p]:
                    print("Menu has been closed")
                    return
            screen.fill(white) 
            self.inventory = self.menu.draw(screen,self.inventory,self.stages)
            pygame.display.flip()
            clock.tick(FPS)
    """
    Checks for boundary detection,a triggered npc fight, level/boundary hoppers, chest items
    and clamps movement to the screen.
    """
    def check_all_collisions(self,screen):
        boundary = self.stages.boundaries[self.stages.level][self.stages.boundary_index]
        self.stages.player.rect.clamp_ip(pygame.display.get_surface().get_rect())
        self.stages.player.update(boundary)    
        for npc in self.stages.npc_list:
            npc.update() 
        self.entrance_collision()
        self.boundary_hopper_collision()
        self.fight_collision(screen)
        self.chest_collision()

    """
    Checks if the player is within the range of an npc and uses enter to proceed with dialog
    """
    def check_triggered_dialog(self,screen,display_npc_dialogs,npc_index, previous_entry,space_released ):
        npc_index = self.npc_dialog()
        keys = pygame.key.get_pressed()
        #print(npc_index)
        if npc_index !=-1: 
            positions = self.stages.npcs[self.stages.level][npc_index]
            dialogs = self.stages.npc_dialogue[self.stages.level][npc_index]
            sizes = self.stages.npc_dialogue_sizes[self.stages.level][npc_index]
            #print(positions,dialogs,sizes)
            #position[(x,y)],size[],dialogs[,], is_cutscene
            if previous_entry==False:
                print('Reentered')
                #Reset to first dialog
                display_npc_dialogs = Dialog([ [(positions[0],positions[1])]*len(dialogs),sizes,dialogs,False])                 
                previous_entry = True
            if keys[pygame.K_RETURN] and space_released: 
                #Update a single npc list dialogue
                space_released = False
                print('Update')
                display_npc_dialogs.index = (display_npc_dialogs.index + 1)
            elif not keys[pygame.K_RETURN]:
                space_released = True
        else:
            previous_entry = False
            display_npc_dialogs = None
        if npc_index != -1 and display_npc_dialogs.index != len(display_npc_dialogs.dialogs):
            display_npc_dialogs.draw(screen)
        return display_npc_dialogs,npc_index, previous_entry,space_released 

    """
    Simply updates the player and stage level based off collisions.
    """
    def display_stage(self,screen):
        clock   = pygame.time.Clock()
        running = True

        #Break if exit goes into a cutscene maybe use -1 and then update the level.
        display_npc_dialogs = None
        npc_index = -1
        previous_entry = False
        space_released = False

        while running:
            if self.stages.level == len(self.stages.exits) or self.state != 0:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                keys = pygame.key.get_pressed()  # This will give us a dictonary where each key has a value of 1 or 0. Where 1 is pressed and 0 is not pressed.
                # Blocks double pressing for increased speed
                if keys[pygame.K_LEFT]: 
                    if self.stages.player.movex >=0:
                        self.stages.player.control(-steps, 0)
                if keys[pygame.K_RIGHT]:
                    if self.stages.player.movex <= 0:
                        self.stages.player.control(steps, 0)
                if keys[pygame.K_UP]:
                    if self.stages.player.movey >= 0:
                        self.stages.player.control(0, -steps)
                if keys[pygame.K_DOWN]:
                    if self.stages.player.movey <= 0:
                        self.stages.player.control(0, steps) 
                if keys[pygame.K_o]:
                    print("Menu open")
                    self.menu.index = 0
                    self.menu.selected = 0
                    self.display_menu(screen)
                
            screen.fill(white) 
            self.check_all_collisions(screen)
            self.stages.draw(screen) 
            display_npc_dialogs,npc_index, previous_entry,space_released =self.check_triggered_dialog(screen,display_npc_dialogs,npc_index, previous_entry,space_released )
            #print(display_npc_dialogs)
            pygame.display.flip()
            clock.tick(FPS)

    def entrance_collision(self):
        for x in self.stages.current_exits:
            rect = Rect(x[0],x[1],x[2],x[3])
            if rect.colliderect(self.stages.player.rect):
                self.stages.update_stage_level(x[4],x[5],x[6],x[7])
                if x[4]==-1 or x[4]==-2:
                    self.state = x[4]
                else:
                    self.state = 0
                break

    def boundary_hopper_collision(self):
        boundary = self.stages.boundary_hopper[self.stages.level][self.stages.boundary_index]
        #print(boundary)
        if len(boundary)!=0:
            rect = Rect(boundary[0],boundary[1],boundary[2],boundary[3])
            if rect.colliderect(self.stages.player.rect):
                print('Hit a level boundary')
                self.stages.update_boundary_hop(boundary[5],boundary[6],boundary[4])

    def draw_battle_menu(self,screen,image,player_index,index,offset,options,all_valid_menu,is_visible,team_box_size,team_font,team_font_size,
                  avatar_width,avatar_height,sp_box_size,sprite_size):

        """
        Calculate the size of the blue menu background using sprite_size(30) * the number of menu items
        """
        menu_background = pygame.Surface((sprite_size*len(all_valid_menu),sprite_size), pygame.SRCALPHA)  
        menu_background.set_colorkey(black)
        menu_background.fill((173,216,255,127))                        
        screen.blit(menu_background, ((screen_width/2)-((sprite_size*len(all_valid_menu))/2),460))

        start = 0
        for i in range(len(all_valid_menu)):
            if all_valid_menu[i] == 5:
                menu = pygame.transform.scale(self.inventory.dragoons[3+(4*self.inventory.team[player_index])],(sprite_size,sprite_size))
                menu.set_colorkey(black)
            else:
                menu = pygame.transform.scale(self.inventory.attack_sprites[(is_visible[all_valid_menu[i]]*3)+1],(sprite_size,sprite_size))
                menu.set_colorkey(black)
            text = team_font.render(options[all_valid_menu[i]], True, red)
            if i == index:
                image.blit(text,((screen_width/2)-((sprite_size*len(all_valid_menu))/2)+start,460-team_font_size))
            image.blit(menu,((screen_width/2)-((sprite_size*len(all_valid_menu))/2)+start,460))
            start+=sprite_size
                    
        for i in range(len(self.inventory.team)):
            #print(i,self.inventory.team[i])
            pos = (offset+((screen_width-(2*offset))//3)*i+5,500+team_box_size)
            avatar = pygame.transform.smoothscale(self.inventory.avatars[self.inventory.team[i]],((avatar_width,avatar_height)))
            avatar.set_colorkey(black)
            image.blit(avatar,pos)
            #Name, Hp, Mp, Sp (5 levels of color)
            name = team_font.render(str(self.inventory.unlocked_team[self.inventory.team[i]].name), True, white)
            image.blit(name,(pos[0]+avatar_width,pos[1])) 
            hp = team_font.render('HP '+str(self.inventory.unlocked_team[self.inventory.team[i]].current_hp)+'/'+str(self.inventory.unlocked_team[self.inventory.team[i]].hp), True, white)
            image.blit(hp,(pos[0]+avatar_width,pos[1]+team_font_size))
            mp = team_font.render('MP '+str(self.inventory.unlocked_team[self.inventory.team[i]].current_mp)+'/'+str(self.inventory.unlocked_team[self.inventory.team[i]].mp), True, white)
            image.blit(mp,(pos[0]+avatar_width,pos[1]+team_font_size*2))
            #This needs to get the SP level in integers 0-5 
            if self.inventory.unlocked_team[self.inventory.team[i]].sp>0 and self.inventory.d_usability[self.inventory.unlocked_team[self.inventory.team[i]].d_index]!=None:
                sp_filled = self.inventory.unlocked_team[self.inventory.team[i]].current_sp//self.inventory.unlocked_team[self.inventory.team[i]].sp
                if sp_filled != 0:
                    sp_text = team_font.render('SP', True, white)
                    image.blit(sp_text,(pos[0]+avatar_width,pos[1]+team_font_size*3)) 
                    sp_filled_amount = team_font.render(str(sp_filled), True, white)
                    image.blit(sp_filled_amount,(pos[0]+avatar_width+sp_box_size+team_font_size ,pos[1]+team_font_size*3)) 

        screen.blit(image,image.get_rect())

    def draw_sp_bars(self,screen,offset,player_index,team_box_size,team_font_size,sp_box_size,avatar_width,avatar_height):
        #Highlighting current players turn and drawing sp bars for all
        for i in range(len(self.inventory.team)):
            if player_index == i:
                avatar_pos = (offset+((screen_width-(2*offset))//3)*i+5,500+team_box_size)
                rect = pygame.Rect(avatar_pos[0],avatar_pos[1],avatar_width,avatar_height)
                pygame.draw.rect(screen,white,rect,width=5)
            if self.inventory.unlocked_dragoons[self.inventory.team[i]] !=None:
                pos = (offset+((screen_width-(2*offset))//3)*i+5,500+team_box_size)
                sp_bar = pygame.Rect(pos[0]+avatar_width+team_font_size,pos[1]+team_font_size*3,sp_box_size,10)
                pygame.draw.rect(screen,gray,sp_bar,width=1)
                sp_filled = self.inventory.unlocked_team[self.inventory.team[i]].current_sp//self.inventory.unlocked_team[self.inventory.team[i]].sp
                #Colors for dragoons 1-5
                colors = [blue,green,yellow,orange,red]
                if sp_filled != 0:
                    pygame.draw.rect(screen,colors[sp_filled-1],sp_bar)
                        
                sp_leftover = self.inventory.unlocked_team[self.inventory.team[i]].current_sp%self.inventory.unlocked_team[self.inventory.team[i]].sp
                sp_fill_size = sp_leftover*sp_box_size
                sp_fill_bar = pygame.Rect(pos[0]+avatar_width+team_font_size,pos[1]+team_font_size*3,sp_fill_size,10)
                if sp_filled == 0:
                    pygame.draw.rect(screen,blue,sp_fill_bar)
                if sp_filled == 5:
                    pass
                else:
                    pygame.draw.rect(screen,colors[sp_filled+1],sp_fill_bar)

    def display_d_attacking(self,screen,player_index,enemy_index,enemy_npcs):
        attacking = True
        hits = 1
        start_ticks = pygame.time.get_ticks()
        timing_between_attacks = 5
        center_x = 100
        center_y = 100

        while attacking:
            seconds = (pygame.time.get_ticks()-start_ticks)/1000
            if seconds >= timing_between_attacks:
                print('Failed attack')  
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()   
                if event.type == pygame.KEYDOWN:       
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_x]:
                        seconds = (pygame.time.get_ticks()-start_ticks)/1000
                        #print(seconds)

                        #Thresh hold for timing between hitting attacks
                        if (4 <= seconds <= timing_between_attacks):
                            print('Hit attack')
                            hits+=1
                            start_ticks = pygame.time.get_ticks()
            if hits >= 5: 
                print('Perfect Dragoon Attack')
                break
            screen.fill(white)
            #Screen width and some sort of size rad=15
            radius = 15
            pygame.draw.circle(screen,black,(center_x,center_y),radius,1)
            d_triangle=[(center_x+5,center_y-radius-15),(center_x,center_y-radius-10),(center_x-5,center_y-radius-15)]
            pygame.draw.polygon(screen,yellow,d_triangle)
            pygame.draw.polygon(screen,black,d_triangle,1)
       
            pygame.draw.rect(screen, yellow, pygame.Rect(center_x-5//2,center_y-radius-10, 5,15),0)
            pygame.draw.rect(screen, black, pygame.Rect(center_x-5//2,center_y-radius-10, 1,1),1)

            angle = seconds*(360/timing_between_attacks)*(pi/180)-90
    
            x = center_x + radius*cos(angle)
            y = center_y + radius*sin(angle)
            print(x,y)
            pygame.draw.circle(screen,blue,(x,y),5)

            pygame.display.flip()
        return enemy_npcs

    def display_attacking(self,screen,player_index,target_indexes,enemy_npcs):
        """
        Only display the first attack target even if multi
        """
        enemy_index = target_indexes[0]

        x=enemy_npcs.sprites()[enemy_index].rect.x
        y=enemy_npcs.sprites()[enemy_index].rect.y
        
        #Get image size (Todo)
        rect = pygame.Rect(x,y,50,50)
        new = screen.subsurface(rect)
        new = new.copy()
        
        offset_x = (screen_width/2)-x
        offset_y = (screen_height/2)-y
        #print(offset_x,offset_y)

        attack_box_size = 20
        max_attack_box_size = 50
        
        start_ticks = pygame.time.get_ticks()
        #Moves enemy to center
        while True:
            seconds = (pygame.time.get_ticks()-start_ticks)/1000
            if seconds >= 2:
                break
            screen.fill(white)
            if seconds > 0:
                screen.blit(new,((x+(offset_x*(seconds/2))),(y+(offset_y*(seconds/2)))))
                #print(seconds/2)
            pygame.display.flip()

        #Addition amount pass this in with the currently selected user
        hits = 0
        row = self.inventory.unlocked_team[self.inventory.team[player_index]].addition_index
        col = self.inventory.selected_additions[self.inventory.team[player_index]]
        #print(row,col)
        time_between_attacks = self.inventory.all_additions[row][col][4]
        total_hits = len(time_between_attacks)

        attack_box = pygame.Rect(screen_width/2,screen_height/2,attack_box_size,attack_box_size)  
        attacking = True
        start_ticks = pygame.time.get_ticks()
        while attacking:
            seconds = (pygame.time.get_ticks()-start_ticks)/1000
            if seconds > time_between_attacks[hits]:
                print('Failed attack')  
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()   
                if event.type == pygame.KEYDOWN:       
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_x]:
                        seconds = (pygame.time.get_ticks()-start_ticks)/1000
                        #print(seconds)

                        #Thresh hold for timing between hitting attacks
                        if (time_between_attacks[hits]//10)*9 <= seconds <= time_between_attacks[hits]:
                            print('Hit attack')
                            hits+=1
                            start_ticks = pygame.time.get_ticks()

            if hits >= total_hits-1:
                print('Successful addition')
                print('Play last hit')
                if total_hits == 1:
                    hits = 1
                break
            
            screen.fill(white)
            screen.blit(new,(screen_width/2,screen_height/2))

            value = max_attack_box_size-(max_attack_box_size-attack_box_size)*(seconds/time_between_attacks[hits])
            #print(value)
            rotating_box = pygame.Surface((value,value), pygame.SRCALPHA)
            rotating_box.fill(blue,rotating_box.get_rect())
            rotating_box.fill(white, rotating_box.get_rect().inflate(-2, -2))
            image = pygame.transform.rotate(rotating_box, (seconds/time_between_attacks[hits])*360)
            rect = image.get_rect()
            rect.center = attack_box.center
            screen.blit(image,rect)
            pygame.draw.rect(screen,blue,attack_box,1)
            pygame.display.flip()

        print(enemy_npcs.sprites()[enemy_index].hp)
        """
            Rework add damage modifiers so weapon and additions modifier % (Todo)
            (base_attack + weapon_damage )* (hits/totals_hit)/100 * addition%
            Then use self.inventory.selected_additions from inventory to change addition 
            % based on its amount completed %
            self.addition_counts[row][col]  -> row -> self.inventory.unlocked_team[self.inventory.team[player_index]].addition_index
                                                        -> col -> self.inventory.selected_additions[self.inventory.team[player_index]]

        """
        damage = (self.inventory.unlocked_team[self.inventory.team[player_index]].base_attack+self.inventory.all_weapons[self.inventory.unlocked_team[self.inventory.team[player_index]].weapon_row][self.inventory.unlocked_team[self.inventory.team[player_index]].weapon_col][1])*((hits/total_hits)/100)*( self.inventory.all_additions[row][col][5][(self.inventory.addition_counts[row][col]//20)])
        #print(damage)

        """
        Target all targets you can have
        """
        for target in target_indexes:
            enemy_npcs.sprites()[target].take_damage(damage)
       
        #print(enemy_npcs.sprites()[enemy_index].hp)
        return enemy_npcs

    def increment_player(self,player_index):
        while player_index < len(self.inventory.team):
            player_index+=1
            if player_index == len(self.inventory.team):
                break
            if self.inventory.unlocked_team[player_index].current_hp > 0:
                break
        return player_index

    def pick_targets(self,screen,enemy_npcs,is_multi,targeting_players):
        if targeting_players:
            valid_targets = [player_index for player_index in self.inventory.team if self.inventory.unlocked_team[player_index].current_hp > 0] 
        else:
            valid_targets = [i for i in range(len(enemy_npcs)) if enemy_npcs.sprites()[i].current_hp > 0] 

        if is_multi:
            return valid_targets

        clock = pygame.time.Clock()
        running = True
        target_index = 0
        while running:
            screen.fill(white)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()          
                keys = pygame.key.get_pressed()
                if event.type in [KEYDOWN, KEYUP]:
                    if keys[pygame.K_RETURN]:
                        running = False
                    if keys[pygame.K_LEFT]:
                        if target_index > 0:
                            target_index -=1
                    if keys[pygame.K_RIGHT]:
                        if target_index < len(valid_targets)-1:
                            target_index +=1
                    if keys[pygame.K_BACKSPACE]:
                        running = False
                        target_index = -1

            if targeting_players:
                x = 300+(target_index*100)
                y = 300
                pygame.draw.circle(screen,red,(x,y),15,1)
            else:
                x = enemy_npcs.sprites()[valid_targets[target_index]].rect.x
                y = enemy_npcs.sprites()[valid_targets[target_index]].rect.y
                pygame.draw.circle(screen,red,(x,y),15,1)

            for i in range(len(enemy_npcs)):
                enemy_npcs.sprites()[i].update()
                enemy_npcs.sprites()[i].draw(screen)
               
            pygame.display.flip()
            clock.tick(FPS)
        return [valid_targets[target_index]]

    def display_battle(self,screen,enemy_npcs,can_run): 
        clock = pygame.time.Clock()
        running = True

        """
        Set the initial to be first alive player also menu index
        """
        index = 0

        player_index = None
        for player in self.inventory.team:
            if self.inventory.unlocked_team[player].hp > 0:
                player_index = player
                break
            
        offset = 30
        sprite_size = 30
        avatar_width = 40
        avatar_height = 60
        sp_box_size = 70
        team_font_size = 16
        team_font = pygame.font.Font(None,team_font_size)
        team_box = pygame.Rect(offset,500,screen_width-(2*offset),screen_height-500-offset)
        team_box_size = 5

        attack_selection = False
        item_selection = False
        item_index = 0
        target_indexes = 0

        """     
        #Make these into animated sprites that when selected go through frames
        all_menu_sprites = pygame.sprite.Group()    
        start = 0
        for i in range(len(is_visible)):
            if is_visible[i]!=-1:
                start+=30
                new_images = []
                for x in self.inventory.attack_sprites[i*3:(i*3)+2]:
                    img = pygame.transform.scale(x,(30,30))
                    img.set_colorkey(black) 
                    new_images.append(img)
                new_menu = Npc((start,0),new_images)
                all_menu_sprites.add(new_menu) 
        """

        while running:
            valid_enemy_targets = [i for i in range(len(enemy_npcs)) if enemy_npcs.sprites()[i].current_hp > 0] 
            if len(valid_enemy_targets) == 0:
                print('All enemies have died')
                return
            
            """
            Set options and run to see if it's a boss battle or normal
            also if the player is in dragoon change options to only attack and magic.
            """
            if player_index < len(self.inventory.team)-1:
                if self.inventory.unlocked_team[self.inventory.team[player_index]].in_dragoon:
                    options = ['D_Attack','D_Magic']
                    is_visible = [6,7] 
                else:
                    options = ['Attack','Defend','Items','Run','No Run','Dragoon','All Dragoons']
                    is_visible = [0,1,2,-1,-1,-1,-1] 
                    if can_run:
                        is_visible[3] = 3
                    else:
                        is_visible[4] = 4  
                    # Checks current player and all players can turn into dragoons
                    is_visible[5] = 0 if self.inventory.unlocked_team[self.inventory.team[player_index]].current_sp >= 100 else -1
                    is_visible[6] = (-1,5) [all(self.inventory.unlocked_team[i].current_sp >= 100 for i in self.inventory.team)] 
                
            if player_index < len(self.inventory.team):
                #print('PLAYER TURN')
                all_valid_menu = [i for i in range(len(options))if is_visible[i] >= 0]
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()          
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_RETURN]:
                        #print(all_valid_menu[index])
                        if options[all_valid_menu[index]] == "Attack":
                            is_multi = False
                            targeting_players = False
                            target_indexes = self.pick_targets(screen,enemy_npcs,is_multi,targeting_players )
                            print(target_indexes)
                            if target_indexes != -1:
                                enemy_npcs = self.display_attacking(screen,player_index,target_indexes,enemy_npcs)
                                valid_enemy_targets = [i for i in range(len(enemy_npcs)) if enemy_npcs.sprites()[i].current_hp>0]
                                if len(valid_enemy_targets) == 0:
                                    print('Killed Targets')
                                    return
                                else:
                                    player_index = self.increment_player(player_index)
                                    index = 0
                        if options[all_valid_menu[index]] == "Defend":
                            #Increase hp by 10% and then cap it off to max hp
                            #current_hp = current_hp+hp_healed if (current_hp+hp_healed)<total_hp else total_hp
                            hp_heal = self.inventory.unlocked_team[self.inventory.team[player_index]].hp//10
                            #print(hp_heal)
                            self.inventory.unlocked_team[self.inventory.team[player_index]].take_damage(-hp_heal)
                            self.inventory.unlocked_team[self.inventory.team[player_index]].is_defending = True
                            player_index = self.increment_player(player_index)
                            index = 0

                        if options[all_valid_menu[index]] == "Items":
                            if item_selection:
                                items = list(self.inventory.items.items())
                                if len(items)!=0:
                                    #Name, Type, Field, Is flat, Amount, Targets(Multi), Alive(is targets alive), targeting_players
                                    print(items[item_index][0])
                                    item_id = -1
                                    for i in range(len(self.inventory.all_items)):
                                        if self.inventory.all_items[i][0] == items[item_index][0]:
                                            item_id = i
                                            break

                                    is_multi = self.inventory.all_items[item_id][5]
                                    targeting_players = self.inventory.all_items[item_id][7]
                                    target_indexes = self.pick_targets(screen,enemy_npcs,is_multi,targeting_players)
                                    if target_indexes  != -1:
                                        for target in target_indexes:
                                            if self.inventory.all_items[item_id][1]=='Recover':
                                                #3 types of recovery hp,mp,sp then amount healed
                                                if self.inventory.all_items[item_id][3]:
                                                    heal_amount = self.inventory.all_items[item_id][4]
                                                else:
                                                    heal_amount = (self.inventory.unlocked_team[target].hp/100)*self.inventory.all_items[item_id][4]
                                                print(heal_amount)
                                                self.inventory.unlocked_team[target].take_damage(-heal_amount)

                                        #Remove 1 quantity from item
                                        self.inventory.update_item(item_id,-1)
                                        item_selection = False
                                        player_index = self.increment_player(player_index)
                                        index = 0
                                    
                            else:
                                item_selection = True
                                print('Open Items')

                        if options[all_valid_menu[index]] == "Dragoon":
                            self.inventory.unlocked_team[self.inventory.team[player_index]].in_dragoon = True
                            player_index = self.increment_player(player_index)
                            index = 0

                        if options[all_valid_menu[index]] == "D_Attack":
                            is_multi = False
                            targeting_players = False
                            target_indexes = self.pick_targets(screen,enemy_npcs,is_multi,targeting_players )
                            print(target_indexes)
                            if target_indexes != -1:
                                enemy_npcs = self.display_d_attacking(screen,player_index,target_indexes,enemy_npcs)
                                valid_enemy_targets = [i for i in range(len(enemy_npcs)) if enemy_npcs.sprites()[i].current_hp>0]
                                if len(valid_enemy_targets) == 0:
                                    print('Killed Targets')
                                    return
                                else:
                                    player_index = self.increment_player(player_index)
                                    index = 0
                            

                    if keys[pygame.K_LEFT]:
                        if item_selection:
                            pass
                        else:
                            if index > 0:
                                index-=1

                    if keys[pygame.K_RIGHT]:
                        if item_selection:
                            pass
                        else:
                            if index < len(all_valid_menu)-1:
                                index+=1

                    if keys[pygame.K_DOWN]:
                        if item_selection:
                            if item_index < len(list(self.inventory.items.items()))-1:
                                item_index+=1
                    if keys[pygame.K_UP]:
                        if item_selection:
                            if item_index > 0:
                                item_index-=1

                    if keys[pygame.K_BACKSPACE]:
                        item_selection = False
                        item_index = 0
                        target_indexes = 0

                screen.fill(white)
                #Battle selection options text, sprites, etc
                if player_index < len(self.inventory.team):
                    image = pygame.Surface((screen_width,screen_height),pygame.SRCALPHA)
                    #image.set_colorkey(black)
                    team_box_background = pygame.Surface(team_box.size, pygame.SRCALPHA)   
                    #team_box_background.set_colorkey(black)
                    team_box_background.fill(dialog_background)                         
                    screen.blit(team_box_background, (team_box.x,team_box.y))
                    menu_select = pygame.Surface((sprite_size,sprite_size), pygame.SRCALPHA)   
                    #menu_select.set_colorkey(black)
                    menu_select.fill(red)                         
                    screen.blit(menu_select, ((screen_width/2)+(sprite_size*index)-((sprite_size*len(all_valid_menu))/2),460))
                    self.draw_battle_menu(screen,image,player_index,index,offset,options,all_valid_menu,is_visible,
                    team_box_size,team_font,team_font_size,avatar_width,avatar_height,sp_box_size,sprite_size)
                    pygame.draw.rect(screen,yellow,team_box,width=team_box_size)
                    self.draw_sp_bars(screen,offset,player_index,team_box_size,team_font_size,sp_box_size,avatar_width,avatar_height)

                    if item_selection:
                        #Rework use screen_width and screen_height (Todo)
                        items = list(self.inventory.items.items())[item_index:item_index+5]
                        item_box_background = pygame.Surface((500,270), pygame.SRCALPHA)   
                        #item_box_background.set_colorkey(black)
                        item_box_background.fill(dialog_background)                         
                        #print('Display Item List')
                        #print(items)
                        for i in range(len(items)):
                            pos = (500//2,0+(i*30)+15)
                            print(pos)
                            print(items[i])
                            if i == item_index:
                                color = red
                            else:
                                color = white
                            item = pygame.font.Font(None,16).render(str(items[i]), True, color)
                            rect = item.get_rect(center=pos)
                            item_box_background.blit(item,rect)
                        item_background_rect = item_box_background.get_rect(center=((screen_width/2), (screen_height/2))) 
                        screen.blit(item_box_background, item_background_rect)

                    """
                    Overrides the draw function which is needed to print out the enemy dying and also update the frames
                    """
                    for i in range(len(enemy_npcs)):
                        #screen.fill(white)
                        if i == target_indexes:
                            enemy_npcs.sprites()[i].update()
                            enemy_npcs.sprites()[i].draw(screen)
                            frames = len(enemy_npcs.sprites()[i].images[enemy_npcs.sprites()[i].state])-1
                            #print(frames)
                            if enemy_npcs.sprites()[i].frame < frames and enemy_npcs.sprites()[i].state == 1:
                                pygame.time.delay(100)     
                        else:
                            enemy_npcs.sprites()[i].update()
                            enemy_npcs.sprites()[i].draw(screen)
               
                """
                #Should update menu based off index selected             
                for menu in all_menu_sprites:
                    menu.update()
                all_menu_sprites.draw(screen)
                """ 
                pygame.display.flip()
                clock.tick(FPS)
                
            else:
                #print('NPC TURN')
                for i in range(len(enemy_npcs)):
                    damage = enemy_npcs.sprites()[i].attack
                    #print(damage)
                    valid_player_targets = [player_index for player_index in self.inventory.team if self.inventory.unlocked_team[player_index].current_hp > 0]
                    #print(valid_player_targets) 
                    generate_random_player_target = random.choice(valid_player_targets)
                    #print(generate_random_player_target)
                    self.inventory.unlocked_team[generate_random_player_target].take_damage(damage)
                    players_dead = all(self.inventory.unlocked_team[player_index].current_hp<=0 for player_index in self.inventory.team)
                    #print(players_dead)
                    if players_dead:
                        print('All players have died')
                        pygame.quit()
                        exit()  
                valid_player_targets = [player_index for player_index in self.inventory.team if self.inventory.unlocked_team[player_index].current_hp > 0]
                player_index = valid_player_targets[0]

    def fight_collision(self,screen):
        for i,x in enumerate(self.stages.enemy_positions[self.stages.level]):
            rect = Rect(x[0],x[1],x[2],x[3])
            if rect.colliderect(self.stages.player.rect):
                print('Hit enemy')
                enemy_npcs = pygame.sprite.Group()
                enemy_list = x[4]
                for j in range(len(enemy_list)):
                    print(j,enemy_list)
                    #print(self.stages.enemy_images[j])
                    #print(self.stages.enemy_base_stats[j])
                    new_npc = Npc((100+(j*100),100),self.stages.enemy_images[enemy_list[j]],self.stages.enemy_base_stats[enemy_list[j]])
                    enemy_npcs.add(new_npc)
                self.display_battle(screen,enemy_npcs,False)
                """
                Do a battle sequence if false exit game
                When leveling skip the master one only update it when leveling moves
                Up to len(self.inventory.all_additions[index])
                """
                print(self.stages.enemy_positions[self.stages.level][i])
                del self.stages.enemy_positions[self.stages.level][i]
                break

    def chest_collision(self):
        removed_chest = pygame.sprite.Group()     
        for i in range(len(self.stages.chest_list)):
            rect = self.stages.chest_list.sprites()[i].rect
            if rect.colliderect(self.stages.player.rect):
                
                if self.stages.chest_list.sprites()[i].type_unlocked==0:
                    self.inventory.update_item(self.stages.chest_list.sprites()[i].item_id,self.stages.chest_list.sprites()[i].quantity)
                    print('I hit a item chest')
                        
                elif self.stages.chest_list.sprites()[i].type_unlocked==1:
                    print('I hit a armour chest')
                else:
                    print('I hit a weapon chest') 
                del self.stages.chest_locations[self.stages.level][i]
            else:
                removed_chest.add(self.stages.chest_list.sprites()[i])
        
        self.stages.chest_list = removed_chest
        
    #You can inflate_ip and check direction (ToDo)
    def npc_dialog(self):
        for i, npc in enumerate(self.stages.npc_list):
            gets_hit = npc.rect.colliderect(self.stages.player.rect)
            if gets_hit:
                return i
        return -1

    def display_video(self,screen):
        clock   = pygame.time.Clock()
        running = True

        movie   = cv2.VideoCapture(self.cutscenes.filenames[self.cutscenes.level])
        audio   = MediaPlayer(self.cutscenes.filenames[self.cutscenes.level])
        fps     = movie.get(cv2.CAP_PROP_FPS)    
        
        while running:
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if keys[pygame.K_RETURN]:
                    print('Clicked passed video')
                    movie.set(cv2.CAP_PROP_POS_FRAMES, movie.get(cv2.CAP_PROP_FRAME_COUNT) - 1)
                    ret, frame = movie.read()
                    if ret: 
                        frame = cv2.resize(frame, (screen_width, screen_height))
                        image = pygame.image.frombuffer(frame.tobytes(),frame.shape[1::-1], "BGR")
                        screen.blit(image, (0,0))
                        pygame.display.flip()
                        clock.tick(fps)
                    pygame.image.save(screen,os.path.join(".//assets//screenshots/last_screen.png"))
                    running = False
            
            ret, frame = movie.read()
            audio_frame, val = audio.get_frame()

            if ret: 
                frame = cv2.resize(frame, (screen_width, screen_height))
                image = pygame.image.frombuffer(frame.tobytes(),frame.shape[1::-1], "BGR")
                screen.blit(image, (0,0))
                pygame.display.flip()
                clock.tick(fps)
                
            else:
                pygame.image.save(screen,os.path.join(".//assets//screenshots/last_screen.png"))
                clock.tick(fps)
                break
            
        movie.release()
        cv2.destroyAllWindows()

    def update_dragoons(self,index):
        if index >= 0:
            if self.inventory.unlocked_dragoons[index] == None:
                self.inventory.unlocked_dragoons[index] = 0
            self.inventory.d_usability[index]=0
            
            for player in self.inventory.unlocked_team:
                if player != None:
                    if player.d_index == index:
                        player.update_stats(self.inventory)
        else:
            pass

    def add_char(self,index):
        # Copy dart's level and then set it to the new player
        
        if index !=0:
            char = Character((base_stats[index][0],self.inventory.unlocked_team[0].level,base_stats[index][2],
            base_stats[index][3],base_stats[index][4],base_stats[index][5],base_stats[index][6],base_stats[index][7]))
            
        else:
            char = Character(base_stats[index])
            
        self.inventory.unlocked_team[index] = char
        self.inventory.team_usability[index] = 0

        if len(self.inventory.team) < 3:
            self.inventory.team.append(index)

    def display_cutscene(self,screen):
        self.display_video(screen)
        if self.cutscenes.level < len(self.cutscenes.dialog):
            self.display_dialog(screen)

        if self.cutscenes.unlock_players[self.cutscenes.level] !=None:
            self.add_char(self.cutscenes.unlock_players[self.cutscenes.level])
        if self.cutscenes.unlock_dragoons[self.cutscenes.level] !=None:
            self.update_dragoons(self.cutscenes.unlock_dragoons[self.cutscenes.level])
        self.state = self.cutscenes.next_state[self.cutscenes.level]
        self.cutscenes.level+=1

    def run(self,screen):
        while True:
            if self.stages.level >= len(self.stages.exits):
                break
            if self.state == -1:
                if self.cutscenes.level < len(self.cutscenes.filenames):
                    self.display_cutscene(screen)
                else:
                    self.state = 0
            else:
                self.display_stage(screen)

def new_game(screen):
    game = Game()
    game.run(screen)
    pygame.quit()
    exit()

def start():
    screen  = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Legend of Dragoon")
    width, height    = 75,150
    logo    = pygame.image.load(".//assets//images/start_menu.png").convert_alpha()  
    logo    = pygame.transform.scale(logo,((screen_width,screen_height)))
    clock   = pygame.time.Clock()
    running = True
    index = 0

    while running:
        if index == 0:
            button1 = Button(((screen_width/2)-width), ((screen_height/2)+(height/6)), width, height, red, "New Game")
            button2 = Button(((screen_width/2)-width), ((screen_height/2)+(height/2)), width, height, white, "Exit")
        else:
            button1 = Button(((screen_width/2)-width), ((screen_height/2)+(height/6)), width, height, white, "New Game")
            button2 = Button(((screen_width/2)-width), ((screen_height/2)+(height/2)), width, height, red, "Exit")
 
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                exit()   
            if keys[pygame.K_ESCAPE]:
                pygame.mixer.music.stop()
                pygame.quit()
                exit()
            if keys[pygame.K_UP]:
                if index > 0:
                    index-=1
            if keys[pygame.K_DOWN]:
                if index == 0:
                    index+=1
            if keys[pygame.K_RETURN]:
                if index == 0:
                    pygame.mixer.music.stop()
                    new_game(screen)
                else:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    exit()
            if button1.is_clicked(event):
                pygame.mixer.music.stop()
                new_game(screen)
            if button2.is_clicked(event):
                pygame.mixer.music.stop()
                pygame.quit()
                exit()

        screen.fill(white)    
        screen.blit(logo,(0,0))
        button1.draw(screen)
        button2.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__=="__main__":
    start()

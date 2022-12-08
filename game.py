import copy
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
menu_background = (185,155,90)

#name, level, hp, attack, weapon(row,col), addition index(Pass the same to Lavitz/Albert due to count)
#base_stats = [('Dart',1,0,15,2,0,0,0),('Lavitz',None,1,17,3,1,0,1),('Shana',None,2,12,1,2,0,2)]
base_stats = [{'Name':'Dart','Level':1,'D_index':0,'Addition_index':0,'Type':'Fire',
                'Base_Hp':15,'Base_Attack':2,'Base_Defense':0,'Base_Matk':0,'Base_Mdef':0},
              {'Name':'Lavitz','Level':1,'D_index':1,'Addition_index':1,'Type':'Wind',
                'Base_Hp':17,'Base_Attack':3,'Base_Defense':0,'Base_Matk':0,'Base_Mdef':0},
              {'Name':'Shana','Level':1,'D_index':2,'Addition_index':2,'Type':None,
                'Base_Hp':12,'Base_Attack':2,'Base_Defense':0,'Base_Matk':0,'Base_Mdef':0}]

def fill_box_with_outline(image,pos,color,color2,width,height,border_size=1):
        background_box = pygame.Surface((width,height), pygame.SRCALPHA)
        if color2 != None:
            background_box.fill(color2)
        background_box.fill(color, background_box.get_rect().inflate(-(border_size+1), -(border_size+1)))
        image.blit(background_box,pos)
        return image

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
        #What can I unlock from chest? item, weapon, armour(0,1,2)
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
            self.stats = stats
            self.stats['Current_Hp'] = self.stats['Hp']
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
        Poison, Stun, Arm-blocking, Confusion, Bewitchment, Fear, Despirit, Petrification, Can't Combat
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

    def update_field(self,damage,key):
        print(key)
        self.stats['Current_'+key]-=damage 
        if self.stats['Current_'+key] > self.stats[key]:
            self.stats['Current_'+key] = self.stats[key]
        if self.stats['Current_'+key] <= 0:
            self.stats['Current_'+key] = 0
            if key == 'Hp':
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
        self.unlock_players = [0, 1, 2, None]
        self.unlock_dragoons = [0, None, None, None]
        #Type(Item, Weapon, Armour), id(y,x), to equip(if not none equip to unlocked_team), quantity(normally 1)
        self.unlock_inventory = [[1,[0,0],0,1],[1,[1,0],1,1],[1,[2,0],2,1],[1,[0,1],None,20]]

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
        self.level = 0
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
        self.exits = [   
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
        self.enemy_base_stats = [ {'Name':'Knight','Level':1,'D_index':None,'Type':None,'Hp':5,'Attack':3,'Defense':0,'Matk':0,'Mdef':0},{'Name':'Commander','Level':1,'D_index':None,'Type':None,'Hp':15,'Attack':5,'Defense':0,'Matk':0,'Mdef':0}]
        #This is for random battles
        self.enemies_by_level = [[0],[0],[0]]

        #Place an item with the location, id, quantity, either item, armor, weapon
        self.chest_list = pygame.sprite.Group()
        self.chest_locations = [[[400,500,0,1,0]],
                                [[100,100,0,1,0]]
                            ]

        for item in self.chest_locations[self.level]:
            new_item = Chest((item[0],item[1]),item[2],item[3],item[4])
            self.chest_list.add(new_item)
        
    #Check if exit is a cutscene then proceed to change self.state to -1, or -2 to a map, 0 to normal. 
    def update_stage_level(self,level,index,x,y):
        self.boundary_index = index
        if level ==-1: 
            self.level += 1
            self.npc_list = pygame.sprite.Group()
            #x,y,size
            for npc in self.npcs[self.level]:
                new_npc = Npc((npc[0],npc[1]),self.npc_images[npc[2]])
                self.npc_list.add(new_npc)
            self.chest_list = pygame.sprite.Group()
            for item in self.chest_locations[self.level]:
                new_item = Chest((item[0],item[1]),item[2],item[3],item[4])
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
                new_item = Chest((item[0],item[1]),item[2],item[3],item[4])
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
                if len(hop) != 0:
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
    def __init__(self,stats):
        self.stats = stats
        self.stats['D_level'] = 0
        self.stats['Current_Sp'] = 0
        self.stats['Sp'] = self.stats['D_level']*100
        self.stats['Mp'] = self.stats['D_level']*20
        self.stats['Current_Mp'] = self.stats['Mp']

        self.stats['Hp'] = self.stats['Base_Hp']+(self.stats['Level']*15)
        self.stats['Current_Hp'] = self.stats['Hp']

        self.stats['Current_Exp'] = 0
        self.stats['Exp'] = self.stats['Level']*100

        self.stats['Attack'] = self.stats['Level']*self.stats['Base_Attack']
        self.stats['Defense'] = self.stats['Level']*self.stats['Base_Defense']
        self.stats['Matk'] = self.stats['Level']*self.stats['Base_Matk']
        self.stats['Mdef'] = self.stats['Level']*self.stats['Base_Mdef']
        
        """
        There are 8 status ailments
        Poison, Stun, Arm-blocking, Confusion, Bewitchment, Fear, Despirit, Petrification, Can't Combat
        """
        self.status = [-1] * 7

        self.slots = [None] * 5
        self.is_defending = False
        self.in_dragoon = False

    def equip(self,slot,equipment):
        self.slots[slot] = equipment

    def equipment_total_stats(self,equipment=None):  
        copy = self.slots.copy()
        if equipment != None:
            copy[equipment.stats['Slot']] = equipment
        total = OrderedDict({'Attack':0,'Defense':0,'Matk':0,'Mdef':0})
        for i in range(len(copy)):
            if copy[i] is not None:
                for key in copy[i].stats:
                    #print(key)
                    if key in total:
                        total[key] += copy[i].stats[key]
        return total

    def update_stats(self,inventory):
        self.stats['D_level'] = inventory.d_level[self.stats['D_index']]
        self.stats['Sp'] = self.stats['D_level']*100
        self.stats['Current_Sp'] = self.stats['Sp']
        self.stats['Mp'] = self.stats['D_level']*20
        self.stats['Current_Mp'] = self.stats['Mp']

    def update_field(self,damage,key):
        self.stats['Current_'+key]-=damage 
        if self.stats['Current_'+key] > self.stats[key]:
            self.stats['Current_'+key] = self.stats[key]
        if self.stats['Current_'+key] <= 0:
            self.stats['Current_'+key] = 0

class Menu():
    def __init__(self):
        self.size = (screen_width,screen_height)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = pygame.Rect((0,0), self.size)
        self.font = pygame.font.Font(None,32)
        img = pygame.image.load(os.path.join('.//assets//menu//background.png')).convert()
        self.bg = pygame.transform.scale(img,((screen_width,screen_height)))
        #Which page of the menu and what selected everytime I move a page just make selected 0
        self.equipment_index = 0
        self.all_unlocked_team = None
        self.valid_equipment = None
        self.selected = 0
        self.index = 0
        self.options = ['Status','Item','Armed','Addition','Replace','Config','Save']


    def draw_character_box(self,inventory,pos,offset,width,i):
        height = (screen_height-(2*offset)-(2*offset))//3
        self.image = fill_box_with_outline(self.image,pos,menu_background,black,width,height)
        
        if inventory.team[i] != None:
            avatar = pygame.transform.smoothscale(inventory.avatars[inventory.team[i]],((inventory.avatar_size,inventory.avatar_size)))
            self.image.blit(avatar,(pos[0]+10,pos[1]+offset))
            pos=(pos[0]+10,pos[1])
            name = self.font.render(str(inventory.unlocked_team[inventory.team[i]].stats['Name']), True, black)
            self.image.blit(name,((pos[0]+inventory.avatar_size,pos[1])))
            level = self.font.render('LV '+str(inventory.unlocked_team[inventory.team[i]].stats['Level']), True, white)
            self.image.blit(level,((pos[0]+100+inventory.avatar_size),pos[1]))
            dlevel = self.font.render("D'LV "+ str(inventory.unlocked_team[inventory.team[i]].stats['D_level']), True, white)
            self.image.blit(dlevel,((pos[0]+inventory.avatar_size),(pos[1]+offset)))
            sp = self.font.render('SP '+str(inventory.unlocked_team[inventory.team[i]].stats['Current_Sp']), True, white)
            self.image.blit(sp,((pos[0]+100+inventory.avatar_size),(pos[1]+offset)))
            hp = self.font.render('HP '+str(inventory.unlocked_team[inventory.team[i]].stats['Current_Hp'])+'/'+str(inventory.unlocked_team[inventory.team[i]].stats['Hp']), True, white)
            self.image.blit(hp,((pos[0]+inventory.avatar_size),(pos[1]+(offset*2))))
            mp = self.font.render('MP '+str(inventory.unlocked_team[inventory.team[i]].stats['Current_Mp'])+'/'+str(inventory.unlocked_team[inventory.team[i]].stats['Mp']), True, white)
            self.image.blit(mp,((pos[0]+inventory.avatar_size),(pos[1]+(offset*3))))
            exp = self.font.render('EXP '+str(inventory.unlocked_team[inventory.team[i]].stats['Current_Exp'])+'/'+str(inventory.unlocked_team[inventory.team[i]].stats['Exp']), True, white)
            self.image.blit(exp,((pos[0]+inventory.avatar_size),(pos[1]+(offset*4))))

    """
    Item List
    Grab a subsection of values from my dict
    self.selected -> Number of items
    """
    def draw_items(self,inventory,offset):
        items = list(inventory.items.items())[self.selected:self.selected+5]
        #print(items)
        for i in range(len(items)):
            pos = (offset+offset/2+screen_width/4,((screen_height-(2*offset))/4)+offset+((2)*offset)+(offset/2)+(i*30))
            #print(pos)
            #print(items[i])
            if i == self.selected:
                color = red
            else:
                color = white
            item = self.font.render(str(items[i]), True, color)
            rect = item.get_rect(center=(pos))
            self.image.blit(item,rect)

    def draw_title(self,stages,offset,width,total_height):
        pos = (offset,total_height)
        height = (screen_height-(2*offset)-(2*offset))//4
        self.image = fill_box_with_outline(self.image,pos,menu_background,black,width,height)
        stage_level = self.font.render(str(stages.level), True, white)
        self.image.blit(stage_level,((pos[0],pos[1])))

    def draw_selections(self,offset,width,total_height):
        pos = (offset,total_height)
        #print(pos)
        height = (screen_height-(2*offset)-(2*offset))//2
        self.image = fill_box_with_outline(self.image,pos,menu_background,black,width,height)

        for j in range(len(self.options)):
            if j == self.selected and self.index != 2:
                color = red
            else:
                color = white
            option = self.font.render(self.options[j], True, color)
            rect = option.get_rect(center=(pos[0]+(width/4), pos[1]+((j+1)*offset)+(offset/2)))
            self.image.blit(option,rect)

    def draw_time(self,inventory,offset,width,total_height):
        pos = (offset,total_height)
        height = (screen_height-(2*offset)-(2*offset)-(2*offset)-(offset/2))//4 
        self.image = fill_box_with_outline(self.image,pos,menu_background,black,width,height)

        gold = self.font.render('GOLD '+str(inventory.gold), True, white)
        self.image.blit(gold,((pos[0],pos[1])))
        time = datetime.now()- inventory.start_time
        #print(time)
        total_time = self.font.render(str(time), True, white)
        self.image.blit(total_time,((pos[0]+100,pos[1])))

        for i in range(len(inventory.unlocked_dragoons)):
            pos = (offset,total_height+offset)
            if inventory.d_usability[i] != None:
                self.image.blit(inventory.dragoons[3+(4*i)],((pos[0]+(20*i),pos[1]+offset)))
            #total_height += ((screen_height-(2*offset))/4)

    def draw_main(self,screen,inventory,stages,offset):
        total_height = offset
        width = (screen_width-(3*offset))//2

        """
        Title, Selections and Gold, Time and Dragoons
        """
        self.draw_title(stages,offset,width,total_height)
        total_height += (screen_height-(2*offset)-(2*offset))//4 + offset
        self.draw_selections(offset,width,total_height)
        total_height += (screen_height-(2*offset)-(2*offset))//2 + offset
        self.draw_time(inventory,offset,width,total_height)
        
        if self.index == 2:
            self.draw_items(inventory,offset)

        height = ((screen_height-(2*offset))//3)
        for i in range(3):
            pos = (((screen_width/2)+(offset/2)),((height*i)+offset))
            self.draw_character_box(inventory,pos,offset,width,i)
           
        screen.blit(self.image,self.rect)

        """
        Menu option outlines
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
                height = ((screen_height-(2*offset))/4)
                points = [pos,(pos[0]+width,pos[1]),(pos[0]+width,pos[1]+height ),(pos[0],pos[1]+height)]
                pygame.draw.polygon(screen,black,points,1)
                total_height += height
        """

        """
        Character box outline
        for i in range(3):  
            height = ((screen_height-(2*offset))//3)
            pos = (((screen_width/2)+offset),((height*i)+(offset*i)))
            points = [pos,(pos[0]+width,pos[1]),(pos[0]+width,pos[1]+height),(pos[0],pos[1]+height)]
            pygame.draw.polygon(screen,black,points,1)
        """
        return inventory

    def draw_replace(self,screen,inventory):
        for i in range(len(inventory.unlocked_team)):
            #print(inventory.unlocked_team[i] )
            if inventory.unlocked_team[i] != None and inventory.team_usability[i] != None  :
                avatar = pygame.transform.smoothscale(inventory.avatars[i],((screen_width//len(inventory.unlocked_team)),inventory.avatar_size))
                self.image.blit(avatar,((i*(screen_width//len(inventory.unlocked_team))),0))
        screen.blit(self.image,self.rect)
        return inventory

    def draw_armed(self,screen,inventory,offset):
        #self.all_unlocked_team = [i for i in range(len(inventory.unlocked_team)) if inventory.unlocked_team[i] != None and inventory.team_usability[i] != None]
        #Display all weapons that can be used by this character 
        #self.valid_equipment = [i for i in range(len(inventory.equipment)) if inventory.equipment[i].stats['Equip'] is None and self.all_unlocked_team[self.selected] in inventory.equipment[i].stats['Usage']]
        #print(len(self.valid_equipment))
        #print(all_unlocked_team)
        pos = (offset,offset)
        width = (screen_width-(3*offset))//2
        self.draw_character_box(inventory,pos,offset,width,self.all_unlocked_team[self.selected])

        height = (screen_height-(2*offset)-(2*offset))//3
        pos = (((screen_width/2)+(offset/2)),(offset))
        self.image = fill_box_with_outline(self.image,pos,menu_background,black,width,height)
        slots = inventory.unlocked_team[self.all_unlocked_team[self.selected]].slots
        for i in range(len(slots)):
            pos = (((screen_width/2)+(offset/2)),(offset+(i*offset)))
            img = pygame.transform.smoothscale(inventory.equipment_sprites[i],((50,30)))
            img.set_colorkey(white)
            self.image.blit(img,pos)
            if slots[i] != None:
                name = self.font.render(str(slots[i].stats['Equipment_Name']), True, white)
                self.image.blit(name,(pos[0]+50,pos[1]))

        height = (screen_height-(2*offset)-(2*offset))//3
        pos = (offset,offset+height+offset)
        s_height = screen_height-(3*offset)-height
        #print(s_height)
        self.image = fill_box_with_outline(self.image,pos,menu_background,black,width,s_height)

        equipment_stats = inventory.unlocked_team[self.all_unlocked_team[self.selected]].equipment_total_stats()
        if len(self.valid_equipment) != 0:
            equipment_changed_stats = inventory.unlocked_team[self.all_unlocked_team[self.selected]].equipment_total_stats(inventory.equipment[self.valid_equipment[self.equipment_index]])
        else:
            equipment_changed_stats = equipment_stats.copy()

        table_row_names = ['Body','Equipment','Total','Dragoon']

        for i, row in enumerate(table_row_names):
            header = self.font.render(str(row), True, white)
            rect = header.get_rect(center=(pos[0]+(i*90)+offset,pos[1]+(offset)))
            self.image.blit(header,rect)
        
        for i, (key, value) in enumerate(equipment_changed_stats.items()):
            #print(i,key,value)
            body_value = inventory.unlocked_team[self.all_unlocked_team[self.selected]].stats[key]
            body_field = self.font.render(str(body_value), True, white)
            rect = body_field.get_rect(center=(pos[0]+(0)+offset,pos[1]+(offset*(i+2))))
            self.image.blit(body_field,rect)
            #print(equipment_stats[key],value)
            if len(self.valid_equipment) != 0:
                if equipment_stats[key] > value:
                    color = red
                elif equipment_stats[key] < value:
                    color = blue
                else:
                    color = white
            else:
                color = white

            equip_field = self.font.render(str(value), True, color)
            rect = equip_field.get_rect(center=(pos[0]+(90)+offset,pos[1]+(offset*(i+2))))
            self.image.blit(equip_field,rect)

            total_value = body_value + value
            total_field = self.font.render(str(total_value), True, color)
            rect = total_field.get_rect(center=(pos[0]+(180)+offset,pos[1]+(offset*(i+2))))
            self.image.blit(total_field,rect)

        pos = (((screen_width/2)+(offset/2)),height+(2*offset))
        self.image = fill_box_with_outline(self.image,pos,menu_background,black,width,s_height)
     
        for i,val in enumerate(self.valid_equipment[self.equipment_index:self.equipment_index+4]):
            if i == 0:
                self.image = fill_box_with_outline(self.image,(pos[0],pos[1]+(offset*i)),yellow,black,width,30)
                color = black
            else:
                color = white
            img = pygame.transform.smoothscale(inventory.equipment_sprites[inventory.equipment[val].stats['Slot']],((50,30)))
            img.set_colorkey(white)
            self.image.blit(img,(pos[0],pos[1]+(offset*i)))
            name = self.font.render(str(inventory.equipment[val].stats['Equipment_Name']), True, color)
            self.image.blit(name,(pos[0]+50,pos[1]+(offset*i)))

        screen.blit(self.image,self.rect)
        return inventory

    """
        First start with background
        Then add all the menu options and images (selectively)
        Use enter to input new menu selection
        Also go display font using self.image.blit then pygame.draw for any shapes
    """
    def draw(self,screen,inventory,stages,offset):
        self.image.blit(self.bg,self.rect)
        #If index is 0 or 1 draw main but with items opened else draw the rest
        if self.index == 0 or self.index == 2:
            inventory = self.draw_main(screen, inventory, stages,offset)
        elif self.index == 3:
            inventory = self.draw_armed(screen, inventory,offset)
        elif self.index == 5:
            inventory = self.draw_replace(screen,inventory)
        return inventory

class Equipment():
    def __init__(self, values):
        self.stats = values

class Inventory():
    def __init__(self):
        #Have to store unscaled versions and then scale within functions
        self.all_spritesheets = Spritesheet(os.path.join('assets/sprites', 'sprites.png'))

        #Name, Attack Damage, Buy, Sell, Effect, 
        #46 unique ones related to certain chars
        self.all_weapons = [[{'Equipment_Name':'Broad Sword','Description':'Initial Weapon','Effect':None,'Buy':None,'Sell':10,'Equip':None,'Slot':0,'Attack':2,'Usage':[0]},
                             {'Equipment_Name':'Bastard Sword','Description':'Initial Weapon','Effect':None,'Buy':None,'Sell':10,'Equip':None,'Slot':0,'Attack':7,'Usage':[0]}]
                            ,[{'Equipment_Name':'Spear','Description':'Initial Weapon','Effect':None,'Buy':None,'Sell':10,'Equip':None,'Slot':0,'Attack':4,'Usage':[1]}],
                            [{'Equipment_Name':'Short Bow','Description':'Initial Weapon','Effect':None,'Buy':None,'Sell':10,'Equip':None,'Slot':0,'Attack':3,'Usage':[2]}]
                           ]
        """
        self.all_weapons = [[['Broad Sword',2,None,10,None],
                             ['Bastard Sword',7,60,30,None],
                             [],[],[],[],[],[]],
                            [['Spear',4,None,10,None],
                             [],[],[],[],[],[]],
                            [['Short Bow',3,None,10,None],
                             [],[],[],[],[],[]]
                            ]
        """
        self.equipment = []

        #Name, Type, Field, Is flat, amount, Targets(Multi), Alive(is targets alive), Targeting Players
        self.all_items = [['Health Potion','Recover', 'Hp', False, 50, False, True, True]]
        self.items = OrderedDict()
        """
        Scroll Testing for items in menu
        for i in range(14):
            self.items[str(i)]=1
        """
        
        #Name, Sp, Hits, Level to obtain, Time between attacks, Damage modifiers
        self.all_additions = [[['Double Slash',[35]*5,2,0,[5,3],[150,157,165,187,202]],['Volcano',[20+(i*4) for i in range(5)],3,2,[5,4,3],[200,210,220,230,250]]],
                              [['Harpoon',[35,38,42,45,50],2,0,[5,3],[100,110,120,130,150]],['Spinning Cane',[35]*5,3,5,[5,4,3],[125+(25*i)for i in range(5)]]],
                              [['Shoot',[50]*5,1,0,[1],[100]*5]]
                            ]
                    
        self.addition_counts = [[0]*len(self.all_additions[i]) for i in range(len(self.all_additions))]
        self.selected_additions = [0]*9

        self.team = [None]*3
        self.unlocked_team = [None]*9
        self.team_usability = [None]*9
        self.unlocked_dragoons = [None]*8
        self.d_usability = [None]*8
        self.d_level = [1]*8
        self.d_exp = [0]*8
        self.d_levels = [100,2000,6000,20000]
        self.gold = 0
        self.stardust = 0

        self.total_time = None
        self.start_time = None
        """
        Start time - current time = total_time
        Save point: add to total, then change start time
        """
        self.equipment_sprites = []
        for i in range(9):
            img = self.all_spritesheets.image_at((170, 77+(i*17) ,20, 17), colorkey=black)
            self.equipment_sprites.append(img) 

        self.avatars = []
        self.avatar_size = 100

        for i in range(9):
            img = self.all_spritesheets.image_at((4+(i*28), 166 ,24, 32), colorkey=black)
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

    def update_equipment(self,new_eq,quantity):
        for i in range(quantity):
            #print((new_eq.stats['Equip']==None))
            self.equipment.append(copy.deepcopy(new_eq))
        #print(self.equipment)
            
class Game():
    def __init__(self):
        self.stages = Stage()
        self.cutscenes  = Cutscene()
        self.menu = Menu()
        self.inventory = Inventory()
        self.state =  -1
        self.offset = 30
        
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
        item_selected = False
        self.menu.equipment_index = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                keys = pygame.key.get_pressed()  
                if keys[pygame.K_RETURN]:
                    print('Clicked on menu item') 
                    if self.menu.index == 0:
                        if self.menu.options[self.menu.selected] == 'Item':
                            items = list(self.inventory.items.items())[0:5]
                            if len(items) != 0:
                                self.menu.selected = 0
                                self.menu.index = 2
                                item_selected = False
                        elif self.menu.options[self.menu.selected] == 'Armed':
                            self.menu.selected = 0
                            self.menu.index = 3
                            item_selected = False
                            all_unlocked_team = [i for i in range(len(self.inventory.unlocked_team)) if self.inventory.unlocked_team[i] != None and self.inventory.team_usability[i] != None]
                            valid_equipment = [i for i in range(len(self.inventory.equipment)) if self.inventory.equipment[i].stats['Equip'] is None and all_unlocked_team[self.menu.selected] in self.inventory.equipment[i].stats['Usage']]
                            #print(all_unlocked_team,valid_equipment)
                            self.menu.all_unlocked_team = all_unlocked_team
                            self.menu.valid_equipment = valid_equipment
                        elif self.menu.options[self.menu.selected] == 'Replace':
                            self.menu.selected = 0
                            self.menu.index = 5
                            item_selected = False
                    elif self.menu.index == 2:
                        if item_selected:
                            print(self.menu.selected)
                            item_selected = False
                        else:
                            item_selected = True
                    elif self.menu.index == 3:
                        player=self.menu.all_unlocked_team[self.menu.selected]
                        weapon_to_equip = self.inventory.equipment[self.menu.valid_equipment[self.menu.equipment_index]]
                        #print(weapon_to_equip.stats['Equip'],weapon_to_equip.stats['Slot'])
                        weapon_to_equip.stats['Equip'] = player
                        for x in self.inventory.equipment:
                            if x.stats['Equip'] == player and x.stats['Slot'] == weapon_to_equip.stats['Slot']:
                                x.stats['Equip'] = None
                                print(x.stats['Equip'],x.stats['Slot'])
                                break
                        player_to_equip = self.inventory.unlocked_team[player]
                        player_to_equip.equip(weapon_to_equip.stats['Slot'],weapon_to_equip)
                        all_unlocked_team = [i for i in range(len(self.inventory.unlocked_team)) if self.inventory.unlocked_team[i] != None and self.inventory.team_usability[i] != None]
                        valid_equipment = [i for i in range(len(self.inventory.equipment)) if self.inventory.equipment[i].stats['Equip'] is None and all_unlocked_team[self.menu.selected] in self.inventory.equipment[i].stats['Usage']]
                        #print(all_unlocked_team,valid_equipment)
                        self.menu.all_unlocked_team = all_unlocked_team
                        self.menu.valid_equipment = valid_equipment
                              
                if keys[pygame.K_LEFT]:
                    if self.menu.index == 3:
                        if self.menu.selected > 0:
                            self.menu.selected -= 1
                            self.menu.equipment_index = 0
                if keys[pygame.K_RIGHT]:
                    if self.menu.index == 3:
                        if self.menu.selected < len(self.menu.all_unlocked_team)-1:
                            self.menu.selected += 1
                            self.menu.equipment_index = 0

                if keys[pygame.K_UP]:
                    if self.menu.index == 0:
                        if self.menu.selected > 0:
                            self.menu.selected -= 1 
                    if item_selected:
                        pass
                    elif self.menu.index == 3:
                        if self.menu.equipment_index > 0:
                            self.menu.equipment_index-=1
                        print(self.menu.equipment_index)
                    else:
                        if self.menu.index == 2:
                            if self.menu.selected > 0:
                                self.menu.selected -= 1 
                        
                if keys[pygame.K_DOWN]:
                    if self.menu.index == 0:
                        if self.menu.selected < len(self.menu.options)-1:
                            self.menu.selected += 1 
                    if item_selected:
                        pass
                    elif self.menu.index == 3:
                        if self.menu.equipment_index < len(self.menu.valid_equipment)-1:
                            self.menu.equipment_index+=1
                    else:
                        if self.menu.index == 2:
                            if self.menu.selected < len(self.inventory.items)-1:
                                self.menu.selected += 1 
                if keys[pygame.K_BACKSPACE]:
                    if self.menu.index == 2:
                        if item_selected:
                            item_selected = False
                        else:
                            self.menu.index = 0
                            self.menu.selected = 1 
                    elif self.menu.index == 3:
                        self.menu.index = 0
                        self.menu.selected = 2 
                    elif self.menu.index == 5:
                        self.menu.index = 0
                        self.menu.selected = 4
                    else:
                        pass

                if keys[pygame.K_p]:
                    print("Menu has been closed")
                    return
            screen.fill(white) 
            self.inventory = self.menu.draw(screen,self.inventory,self.stages,self.offset)
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
        clock = pygame.time.Clock()
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
        """
            #Should update menu based off index selected             
            for menu in all_menu_sprites:
                menu.update()
            all_menu_sprites.draw(screen)
        """ 
        """
        Calculate the size of the blue menu background using sprite_size(30) * the number of menu items
        """
        width=sprite_size*len(all_valid_menu)
        pos=((screen_width/2)-((sprite_size*len(all_valid_menu))/2),460)
        image = fill_box_with_outline(image,pos,(173,216,255,127),None,width,sprite_size)
        
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
            if self.inventory.team[i] != None:
                pos = (offset+((screen_width-(2*offset))//3)*i+5,500+team_box_size)
                avatar = pygame.transform.smoothscale(self.inventory.avatars[self.inventory.team[i]],((avatar_width,avatar_height)))
                avatar.set_colorkey(black)
                image.blit(avatar,pos)
                #Name, Hp, Mp, Sp (5 levels of color)
                #Also the 5 is just padding for the highlighted player white box
                name = team_font.render(str(self.inventory.unlocked_team[self.inventory.team[i]].stats['Name']), True, white)
                image.blit(name,(pos[0]+avatar_width+5,pos[1])) 
                hp = team_font.render('HP '+str(self.inventory.unlocked_team[self.inventory.team[i]].stats['Current_Hp'])+'/'+str(self.inventory.unlocked_team[self.inventory.team[i]].stats['Hp']), True, white)
                image.blit(hp,(pos[0]+avatar_width+5,pos[1]+team_font_size))
                mp = team_font.render('MP '+str(self.inventory.unlocked_team[self.inventory.team[i]].stats['Current_Mp'])+'/'+str(self.inventory.unlocked_team[self.inventory.team[i]].stats['Mp']), True, white)
                image.blit(mp,(pos[0]+avatar_width+5,pos[1]+team_font_size*2))
                #This needs to get the SP level in integers 0-5 
                if self.inventory.unlocked_team[self.inventory.team[i]].stats['Sp']>0 and self.inventory.d_usability[self.inventory.unlocked_team[self.inventory.team[i]].stats['D_index']]!=None:
                    sp_filled = self.inventory.unlocked_team[self.inventory.team[i]].stats['Current_Sp']//self.inventory.unlocked_team[self.inventory.team[i]].stats['Sp']
                    if sp_filled != 0:
                        sp_text = team_font.render('SP', True, white)
                        image.blit(sp_text,(pos[0]+avatar_width+5,pos[1]+team_font_size*3)) 
                        sp_filled_amount = team_font.render(str(sp_filled), True, white)
                        image.blit(sp_filled_amount,(pos[0]+avatar_width+sp_box_size+team_font_size+5,pos[1]+team_font_size*3)) 

        screen.blit(image,image.get_rect())

    def draw_sp_bars(self,screen,offset,player_index,team_box_size,team_font_size,sp_box_size,avatar_width,avatar_height):
        #Highlighting current players turn and drawing sp bars for all
        for i in range(len(self.inventory.team)):
            if self.inventory.team[i] != None:
                if self.inventory.unlocked_dragoons[self.inventory.team[i]] != None:
                    pos = ((offset+((screen_width-(2*offset))//3)*i+(2*5)),500+team_box_size)
                    sp_bar = pygame.Rect(pos[0]+avatar_width+team_font_size,pos[1]+team_font_size*3,sp_box_size,10)
                    pygame.draw.rect(screen,gray,sp_bar,width=1)
                    sp_filled = self.inventory.unlocked_team[self.inventory.team[i]].stats['Current_Sp']//self.inventory.unlocked_team[self.inventory.team[i]].stats['Sp']
                    #Colors for dragoons 1-5
                    colors = [blue,green,yellow,orange,red]
                    if sp_filled != 0:
                        pygame.draw.rect(screen,colors[sp_filled-1],sp_bar)
                            
                    sp_leftover = self.inventory.unlocked_team[self.inventory.team[i]].stats['Current_Sp']%self.inventory.unlocked_team[self.inventory.team[i]].stats['Sp']
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
            d_triangle = [(center_x+5,center_y-radius-15),(center_x,center_y-radius-10),(center_x-5,center_y-radius-15)]
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
        x = enemy_npcs.sprites()[enemy_index].rect.x
        y = enemy_npcs.sprites()[enemy_index].rect.y
        
        offset_x = (screen_width/2)-x
        offset_y = (screen_height/2)-y
        #print(offset_x,offset_y)

        attack_box_size = 20
        max_attack_box_size = 50
        
        start_ticks = pygame.time.get_ticks()
        clock = pygame.time.Clock()
        #Moves enemy to center
        while True:
            seconds = (pygame.time.get_ticks()-start_ticks)/1000
            if seconds >= 2:
                break
            screen.fill(white)
            if seconds > 0:
                enemy_npcs.sprites()[enemy_index].rect.topleft=((x+(offset_x*(seconds/2))),(y+(offset_y*(seconds/2))))
                enemy_npcs.sprites()[enemy_index].update()
                enemy_npcs.sprites()[enemy_index].draw(screen)
            pygame.display.flip()
            clock.tick(FPS)

        #Addition amount pass this in with the currently selected user
        hits = 0
        row = self.inventory.unlocked_team[self.inventory.team[player_index]].stats['Addition_index']
        col = self.inventory.selected_additions[self.inventory.team[player_index]]
        #print(row,col)
        time_between_attacks = self.inventory.all_additions[row][col][4]
        total_hits = len(time_between_attacks)

        attack_box = pygame.Rect(screen_width/2,screen_height/2,attack_box_size,attack_box_size)  
        attacking = True
        start_ticks = pygame.time.get_ticks()
        enemy_npcs.sprites()[enemy_index].rect.topleft=(screen_width/2,screen_height/2)

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
                if total_hits == 1:
                    hits = 1
                else:
                    hits+=1
                break
            
            screen.fill(white)
            enemy_npcs.sprites()[enemy_index].update()
            enemy_npcs.sprites()[enemy_index].draw(screen)

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
            clock.tick(FPS)

        """
            Rework add damage modifiers so weapon and additions modifier % (Todo)
            (base_attack + weapon_damage )* (hits/totals_hit)/100 * addition%
            Then use self.inventory.selected_additions from inventory to change addition 
            % based on its amount completed %
            self.addition_counts[row][col]  -> row -> self.inventory.unlocked_team[self.inventory.team[player_index]].addition_index
                                            -> col -> self.inventory.selected_additions[self.inventory.team[player_index]]

        """
        body_total = self.inventory.unlocked_team[self.inventory.team[player_index]].stats
        equipment_total = self.inventory.unlocked_team[self.inventory.team[player_index]].equipment_total_stats()
        for key,value in equipment_total.items():
            if key in body_total:
                equipment_total[key] += body_total[key]

        damage = equipment_total['Attack']*(((hits/total_hits)/100)*(self.inventory.all_additions[row][col][5][self.inventory.addition_counts[row][col]//20]))
        print('I did ',damage,equipment_total['Attack'],hits,((hits/total_hits)/100))
        
        #print(enemy_npcs.sprites()[enemy_index].stats['Hp'])
        """
        Target all targets you can have
        """
        for target in target_indexes:
            enemy_npcs.sprites()[target].update_field(damage,'Hp')
       
        #print(enemy_npcs.sprites()[enemy_index].hp)
        enemy_npcs.sprites()[enemy_index].rect.topleft = (x,y)
        return enemy_npcs

    def increment_player(self,player_index):
        while player_index < len(self.inventory.team):
            player_index+=1
            if player_index == len(self.inventory.team):
                break
            if self.inventory.unlocked_team[player_index] != None:
                if self.inventory.unlocked_team[player_index].stats['Current_Hp'] > 0:
                    return player_index
        return player_index

    def pick_targets(self,screen,enemy_npcs,is_multi,targeting_players):
        valid_targets = []
        if targeting_players:
            for player in self.inventory.team:
                if player != None: 
                    if self.inventory.unlocked_team[player].stats['Current_Hp'] > 0:
                        valid_targets.append(player) 
        else:
            valid_targets = [i for i in range(len(enemy_npcs)) if enemy_npcs.sprites()[i].stats['Current_Hp'] > 0] 

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
            if player is not None and self.inventory.unlocked_team[player].stats['Current_Hp'] > 0:
                player_index = player
                break
            
        sprite_size = 30
        avatar_width = 40
        avatar_height = 60
        sp_box_size = 70
        team_font_size = 16
        team_font = pygame.font.Font(None,team_font_size)
        team_box = pygame.Rect(self.offset,500,screen_width-(2*self.offset),screen_height-500-self.offset)
        team_box_border_size = 5

        item_selection = False
        item_index = 0
        target_indexes = [0]

        while running:
            valid_enemy_targets = [i for i in range(len(enemy_npcs)) if enemy_npcs.sprites()[i].stats['Current_Hp'] > 0] 
            if len(valid_enemy_targets) == 0:
                print('All enemies have died')
                return
            
            """
            Set options and run to see if it's a boss battle or normal
            also if the player is in dragoon change options to only attack and magic.
            """
            if player_index < len(self.inventory.team):
                if self.inventory.team[player_index] is None:
                    player_index = self.increment_player(player_index)
                else:
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
                        is_visible[5] = 0 if self.inventory.unlocked_team[self.inventory.team[player_index]].stats['Current_Sp'] >= 100 else -1
                        is_visible[6] = 5
                        for i in self.inventory.team:
                            if i != None:
                                if self.inventory.unlocked_team[i].stats['Current_Sp'] >= 100:
                                    pass
                                else:
                                    is_visible[6]=-1
                                    break
                        #is_visible[6] = (-1,5) [all( self.inventory.unlocked_team[i].stats['Current_Sp'] >= 100 for i in self.inventory.team)] 
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
                                target_indexes = self.pick_targets(screen,enemy_npcs,is_multi,targeting_players)
                                print(target_indexes)
                                if target_indexes != -1:
                                    enemy_npcs = self.display_attacking(screen,player_index,target_indexes,enemy_npcs)
                                    valid_enemy_targets = [i for i in range(len(enemy_npcs)) if enemy_npcs.sprites()[i].stats['Current_Hp']>0]
                                    if len(valid_enemy_targets) == 0:
                                        print('Killed Targets')
                                        return
                                    else:
                                        player_index = self.increment_player(player_index)
                                        index = 0
                            if options[all_valid_menu[index]] == "Defend":
                                #Increase hp by 10% and then cap it off to max hp
                                hp_heal = self.inventory.unlocked_team[self.inventory.team[player_index]].stats['Hp']//10
                                #print(hp_heal)
                                self.inventory.unlocked_team[self.inventory.team[player_index]].update_field(-hp_heal,'Hp')
                                self.inventory.unlocked_team[self.inventory.team[player_index]].is_defending = True
                                player_index = self.increment_player(player_index)
                                index = 0

                            if options[all_valid_menu[index]] == "Items":
                                if item_selection:
                                    items = list(self.inventory.items.items())
                                    if len(items) != 0:
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
                                        if target_indexes != -1:
                                            for target in target_indexes:
                                                if self.inventory.all_items[item_id][1] == 'Recover':
                                                    #3 types of recovery hp,mp,sp then amount healed
                                                    if self.inventory.all_items[item_id][3]:
                                                        heal_amount = self.inventory.all_items[item_id][4]
                                                    else:
                                                        heal_amount = int((self.inventory.unlocked_team[target].stats[[item_id][2]]/100)*self.inventory.all_items[item_id][4])
                                                    print(heal_amount)
                                                    self.inventory.unlocked_team[target].update_field(-heal_amount,[item_id][2])

                                            self.inventory.update_item(item_id,-1)
                                            item_selection = False
                                            player_index = self.increment_player(player_index)
                                            index = 0  
                                else:
                                    item_selection = True
                                    print('Open Items')

                            if options[all_valid_menu[index]] == "Dragoon":
                                self.inventory.unlocked_team[self.inventory.team[player_index]].in_dragoon = True
                                #player_index = self.increment_player(player_index)
                                index = 0

                            if options[all_valid_menu[index]] == "D_Attack":
                                is_multi = False
                                targeting_players = False
                                target_indexes = self.pick_targets(screen,enemy_npcs,is_multi,targeting_players)
                                if target_indexes != -1:
                                    enemy_npcs = self.display_d_attacking(screen,player_index,target_indexes,enemy_npcs)
                                    valid_enemy_targets = [i for i in range(len(enemy_npcs)) if enemy_npcs.sprites()[i].stats['Current_Hp']>0]
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
                            target_indexes = [0]

                    screen.fill(white)
                    #Battle selection options text, sprites, etc
                    if player_index < len(self.inventory.team) and self.inventory.team[player_index] != None:
                        image = pygame.Surface((screen_width,screen_height),pygame.SRCALPHA)
                        #image.set_colorkey(black)
                        image = fill_box_with_outline(image,(team_box.x,team_box.y),dialog_background,yellow,team_box.width,team_box.height,team_box_border_size)
                        image = fill_box_with_outline(image,(((screen_width/2)+(sprite_size*index)-((sprite_size*len(all_valid_menu))/2)),460),red,None,sprite_size,sprite_size)
                        avatar_pos = (self.offset+(((screen_width-(2*self.offset))//3)*player_index),500+team_box_border_size-(5))
                        print(avatar_pos,avatar_width,avatar_height)
                        image = fill_box_with_outline(image,avatar_pos,white,None,avatar_width+(2*5),avatar_height+(2*5),5)

                        self.draw_battle_menu(screen,image,player_index,index,self.offset,options,all_valid_menu,is_visible,
                        team_box_border_size,team_font,team_font_size,avatar_width,avatar_height,sp_box_size,sprite_size)
                        #pygame.draw.rect(screen,yellow,team_box,width=team_box_size)
                        
                        self.draw_sp_bars(screen,self.offset,player_index,team_box_border_size,team_font_size,sp_box_size,avatar_width,avatar_height)

                        if item_selection:
                            #Rework use screen_width and screen_height (Todo)
                            items = list(self.inventory.items.items())[item_index:item_index+5]
                            item_box_background = pygame.Surface((500,270), pygame.SRCALPHA)   
                            #item_box_background.set_colorkey(black)
                            item_box_background.fill(dialog_background)                         
                            #print(items)
                            for i in range(len(items)):
                                pos = (500//2,0+(i*30)+15)
                                #print(pos)
                                #print(items[i])
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
                            if i in target_indexes:
                                enemy_npcs.sprites()[i].update()
                                enemy_npcs.sprites()[i].draw(screen)
                                frames = len(enemy_npcs.sprites()[i].images[enemy_npcs.sprites()[i].state])-1
                                if enemy_npcs.sprites()[i].frame < frames and enemy_npcs.sprites()[i].state == 1:
                                    pygame.time.delay(200)     
                            else:
                                enemy_npcs.sprites()[i].update()
                                enemy_npcs.sprites()[i].draw(screen)
                
                    pygame.display.flip()
                    clock.tick(FPS)
            else:
                #print('NPC TURN')
                for i in range(len(enemy_npcs)):
                    if enemy_npcs.sprites()[i].stats['Current_Hp']>0:
                        damage = enemy_npcs.sprites()[i].stats['Attack']
                        print(damage)
                        valid_player_targets = []
                        for player in self.inventory.team:
                            if player != None:
                                if self.inventory.unlocked_team[player].stats['Current_Hp'] > 0:
                                    valid_player_targets.append(player)

                        #print(valid_player_targets) 
                        generate_random_player_target = random.choice(valid_player_targets)
                        #print(generate_random_player_target)
                        self.inventory.unlocked_team[generate_random_player_target].update_field(damage,'Hp')
                        
                        #all(self.inventory.unlocked_team[player_index].stats['Current_hp']<=0 for player_index in self.inventory.team)
                        players_dead = True
                        for player in self.inventory.team:
                            if player != None:
                                if self.inventory.unlocked_team[player].stats['Current_Hp']>0:
                                    players_dead = False
                                    break

                        #print(players_dead)
                        if players_dead:
                            print('All players have died')
                            pygame.quit()
                            exit()  

                valid_player_targets = []
                for player in self.inventory.team:
                    if player != None:
                        if self.inventory.unlocked_team[player].stats['Current_Hp'] > 0:
                            valid_player_targets.append(player)
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
                if self.stages.chest_list.sprites()[i].type_unlocked == 0:
                    print('I hit a item chest')
                    self.inventory.update_item(self.stages.chest_list.sprites()[i].item_id,self.stages.chest_list.sprites()[i].quantity)
                elif self.stages.chest_list.sprites()[i].type_unlocked == 1:
                    print('I hit a weapon chest')
                else:
                    print('I hit a armour chest') 
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
                    if player.stats['D_index'] == index:
                        player.update_stats(self.inventory)
        else:
            pass

    def update_char(self,index):
        """
        Copy dart's level and then set it to the new player maybe rework to median all unlocked team
        """
        if index != 0:
            new_char = base_stats[index]
            new_char['Level'] = self.inventory.unlocked_team[0].stats['Level']
            char = Character(new_char)
        else:
            char = Character(base_stats[index])
            
        self.inventory.unlocked_team[index] = char
        self.inventory.team_usability[index] = 0

        for i in range(len(self.inventory.team)):
            if self.inventory.team[i] == None:
                self.inventory.team[i] = index
                #print(self.inventory.team[i])
                break

    """
    Check type of inventory added then either equip to player always false for item[0]==0 , 
    and set equipped item to player index, then set old equipment to false. (Todo)
    """
    def update_inventory(self,item):
        #print(item)
        if item[0]==1:
            #print(self.inventory.all_weapons[item[1][0]][item[1][1]])
            new_eq = Equipment(self.inventory.all_weapons[item[1][0]][item[1][1]])
            self.inventory.update_equipment(new_eq,item[3])
            print(item[2])
            if item[2] != None:
                self.inventory.equipment[-1].stats['Equip'] = item[2]
                self.inventory.unlocked_team[item[2]].equip(self.inventory.equipment[-1].stats['Slot'],self.inventory.equipment[-1])
            print(self.inventory.equipment[-1].stats['Equip'])
        elif item[0]==2:
            pass
        else:
            self.inventory.update_item(item[1][0],item[3])   

    def display_cutscene(self,screen):
        self.display_video(screen)
        if self.cutscenes.level < len(self.cutscenes.dialog):
            self.display_dialog(screen)
            if self.cutscenes.unlock_players[self.cutscenes.level] != None:
                self.update_char(self.cutscenes.unlock_players[self.cutscenes.level])
            if self.cutscenes.unlock_dragoons[self.cutscenes.level] != None:
                self.update_dragoons(self.cutscenes.unlock_dragoons[self.cutscenes.level])
            if self.cutscenes.unlock_inventory[self.cutscenes.level] != None:
                self.update_inventory(self.cutscenes.unlock_inventory[self.cutscenes.level])
           
        self.state = self.cutscenes.next_state[self.cutscenes.level]
        self.cutscenes.level += 1

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
    game.inventory.total_time = 0
    game.inventory.start_time = datetime.now()
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

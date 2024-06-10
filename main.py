from scene import *
import sound
import random
import math
import time
import datetime
A = Action

SCREEN_WIDTH, SCREEN_HEIGHT = get_screen_size()

PLAY_WIDTH, PLAY_HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT

GRAVITY = -5

jumping_textures = [
    'shp:Flash00',
    'shp:Flash01',
    'shp:Flash02',
    'shp:Flash03',
    'shp:Flash04',
    'shp:Flash05',
    ]

walk_textures = [
    Texture('plf:AlienBlue_walk1'), Texture('plf:AlienBlue_walk2')
    ]
    
class Player(SpriteNode):
    def __init__(self, x, y, *args, **kwargs):
        SpriteNode.__init__('plf:AlienBlue_front', position=(x, y))

class MyScene (Scene):
    def setup(self):
        self.physics_objects = []
        self.ground = Node(parent=self)
        self.background_color = 'cyan'
        for i in range(0, int(PLAY_WIDTH + 64), 64):
            tile = SpriteNode('plf:Ground_StoneCenter', position = (i, SCREEN_HEIGHT // 3), anchor_point=(0, 0)) 
            self.ground.add_child(tile)
            self.physics_objects.append(tile)
            
        
        self.platforms = Node(parent=self)
        for i in range(0, 256, 64):
            tile = SpriteNode('plf:Ground_Grass', position=(100 + i, 500), anchor_point=(0,0))
            self.platforms.add_child(tile)
            self.physics_objects.append(tile)
            
            
        self.player = SpriteNode('plf:AlienBlue_front')
        self.add_child(self.player)
        self.player.anchor_point = (0.5,0)
        self.player.position = (PLAY_WIDTH // 2, SCREEN_HEIGHT // 3 + PLAY_HEIGHT // 3)
        self.player.z_position = 0
        
        self.player_box = ShapeNode(ui.Path.rect(0, 0, 64, 80),  position = (self.player.position), anchor_point=(0.5,0), fill_color = 'clear', stroke_color='red')
        self.add_child(self.player_box)
        
        self.count = 0
        self.index = 0
        self.walk_count = 0
        self.walk_idx = 0
        #for t in jumping_textures:
            #t.parent=self.player
        
        self.left_button = SpriteNode('iow:arrow_left_b_256', anchor_point = (0,0), position = (-75,0))
        self.left_button.bbox
        self.add_child(self.left_button)
        print(self.left_button.frame)
        
        self.lb_box = ShapeNode(ui.Path.rect(0.00, 0.00, 115.00, 170.00), anchor_point=(0,0), position=(0,40), fill_color = 'clear', stroke_color='green', parent=self)
        print(self.lb_box.frame)
        
        self.right_button = SpriteNode('iow:arrow_right_b_256', position = (175,125))
        self.add_child(self.right_button)
        
        self.rb_box = ShapeNode(ui.Path.rect(0.00, 0.00, 115.00, 170.00), anchor_point=(0,0), position=(120,40), fill_color = 'clear', stroke_color='green', parent=self)
        print(self.lb_box.frame)
        
        self.jump_button = SpriteNode('iow:ios7_circle_filled_256', position=(310, 125), scale=.5)
        self.add_child(self.jump_button)
        
        
        self.jumping = False
        self.on_ground = False
        self.accel = [0, 0]
        self.delta = [0, 0]
        self.jumping_n = 0
        
        self.move_touch = None
        
        print(type(self.delta[0]))
    
    def did_change_size(self):
        pass
    
    def update(self):
        # collision detection
        # move and check in horizontal then vertical to avoid weird behavior
        # frame indices are 0: x pos, 1: y pos, 2: width, 3: height
        self.player_box.position = self.player.position
        #self.player.anchor_point = (0, 0)
        self.player.position += self.delta[0], 0
        self.player_box.position = self.player.position
        for obj in self.physics_objects:
            if self.player_box.frame.intersects(obj.frame):
                
                if self.delta[0] < 0:
                    self.player.position = obj.frame.max_x , self.player.position[1]
                    
                if self.delta[0] > 0:
                    self.player.position = obj.frame.x - self.player.frame.w + (self.player.frame.w/2) - 2, self.player.position[1]
        

        self.player.position += 0, self.delta[1]
        self.player_box.position = self.player.position
        for obj in self.physics_objects:
            if self.player_box.frame.intersects(obj.frame):
                if self.delta[1] < 0:
                    self.player.position = self.player.position[0], obj.frame.max_y
                    self.on_ground = True
                    self.jumping = False
                    self.delta[1] = 0
                    print('frame: ',obj.frame)
                    print('player: ', self.player.frame)
                   
                if self.delta[1] > 0:
                    self.player.position = self.player.position[0], obj.frame.y - self.player_box.frame.h
                    self.delta[1] = 0
        self.player.anchor_point = (0.5, 0)
        
        self.delta[1] = max(GRAVITY, self.delta[1] - 0.5)
        
        
        #self.delta[0] += self.accel[0] 
        if self.delta[0] > 5:
            self.delta[0] = 5
        elif self.delta[0] < -5:
            self.delta[0] = -5
            
        #flips sprite on x axis if moving to the left (sprite faces right normally)
        #this is why we need to use 0.5, 5 for our anchor point
        if self.delta[0] < 0:
            self.player.x_scale = -1
        else:
            self.player.x_scale = 1
        
        if not self.move_touch or not self.touches:
            if self.delta[0] > 0:
                self.delta[0] += self.accel[0]
                if self.delta[0] < 0:
                    self.delta[0] = 0
                    self.accel[0] = 0
            elif self.delta[0] < 0:
                self.delta[0] += self.accel[0]
                if self.delta[0] > 0:
                    self.delta[0] = 0
                    self.accel[0] = 0
        else:
            self.delta[0] += self.accel[0]
        
        if self.on_ground and abs(self.delta[0]) > 0:
            print('true')
            print(self.walk_idx)
            self.walk_count += 1
            self.player.texture = walk_textures[self.walk_idx]
            
            if self.walk_count > 3:
                self.walk_idx += 1
                self.walk_count = 0
            if self.walk_idx > 1:
                self.walk_idx = 0
                
             
        
        elif self.jumping == True:
            e = SpriteNode(jumping_textures[self.jumping_n], z_position= -1, scale=.4, anchor_point=(0.5,0), parent=self, position=(self.player.position.x , self.player.position.y))
            e.blend_mode = BLEND_ADD
            e.color = '#ff3e3e'
            e.run_action(A.sequence(A.fade_to(0, 0.2), A.remove()))
            # put somethint that counts time
            # to slow animation framerate
            self.count += 1
            print(self.count)
            
            if self.count > 3:
                self.jumping_n += 1
                self.count = 0
                print('yes')
            if self.jumping_n > 5:
                self.jumping_n = 0
                
            self.player.texture = Texture('plf:AlienBlue_jump')
                    
        else:
            self.player.texture = Texture('plf:AlienBlue_front')
            
        
            
        print('delta:', self.delta)
        print('accel:', self.accel)
    
    def touch_began(self, touch):
        self.jump_touch = None
        self.move_touch = None
        self.first_touch = touch.location
        if self.first_touch in self.lb_box.frame:
            self.accel[0] = -.25
            self.move_touch = touch.touch_id
        elif self.first_touch in self.rb_box.frame:
            self.accel[0] = .25
            self.move_touch = touch.touch_id
        if self.first_touch in self.jump_button.frame and self.on_ground:
            self.jump_touch = touch.touch_id
            self.delta[1] = 15
            self.on_ground = False
            self.jumping = True
        print(touch.location)
        print(self.touches)
    
    def touch_moved(self, touch):
        pass
    
    def touch_ended(self, touch):
        if touch.touch_id == self.jump_touch:
            pass
        if touch.touch_id == self.move_touch or not self.touches:
            self.accel[0] *= -1
            self.move_touch = None
        

if __name__ == '__main__':
    run(MyScene(), show_fps=False)
    

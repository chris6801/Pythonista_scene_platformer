from scene import *
import sound
import random
import math
import time
import datetime
A = Action

SCREEN_WIDTH, SCREEN_HEIGHT = get_screen_size()

PLAY_WIDTH, PLAY_HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT

TILE_SIZE = 64

GRAVITY = -5

LEVEL_ONE = [
    '000000000000000000000000000000',
    '000000000000000000000000110000',
    '000001001100110010001000000000',
    '000000000000011110000110000000',
    '000000000000000000000000000000',
    '000011100000001110000000111000',
    '002111110000011111000001111100',
    '111111111111111111110011111111'
    ]

LEVEL_ONE = list(reversed(LEVEL_ONE))
            
MAP_KEY = {'0': 'air',
           '1': 'ground',
           '2': 'player'}

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
    
def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))
    
class Button(SpriteNode):
    def __init__(self, texture, x_pos, y_pos, hit_width, hit_height, *args, **kwargs):
        SpriteNode.__init__(self, texture, x, y, *args, **kwargs)
        
        self.pressed = False
        
        self.hit_box = ShapeNode(ui.Path.rect(self, 0, 0, self.frame.w, self.frame.h))

class PhysicsEntity(SpriteNode):
    def __init__(self, texture, x, y, *args, **kwargs):
        SpriteNode.__init__(self, texture, position=(x, y), *args, **kwargs)
        self.vel = Vector2(0, 0)
        self.accel = Vector2(0, 0)
        self.anchor_point = (0.5, 0)
       
        self.hit_box = ShapeNode(ui.Path.rect(0, 0, self.frame.w, self.frame.h), position=(0, 50), anchor_point=(0.5,0), fill_color = 'clear', stroke_color='red')
   
        print('frame: ', self.frame)
        print('box frame: ', self.hit_box.frame)
    
    def update(self, colliders):
        #collision detection
        self.position += self.vel.x, 0
        self.hit_box.position = self.position
        for obj in colliders:
            if self.hit_box.frame.intersects(obj.frame) and obj != self.hit_box:
                
                if self.vel.x < 0:
                    self.position = obj.frame.max_x + (self.frame.w / 2), self.position.y
                    
                if self.vel.x > 0:
                    self.position = obj.frame.x - self.frame.w + (self.frame.w/2) - 2, self.position.y
        
        self.position += 0, self.vel.y
        self.hit_box.position = self.position
        for obj in colliders:
            if self.hit_box.frame.intersects(obj.frame) and obj != self.hit_box:
                if self.vel.y < 0:
                    self.position = self.position.x, obj.frame.max_y
                    self.on_ground = True
                    self.jumping = False
                   
                if self.vel.y > 0:
                    self.position = self.position.x, obj.frame.y - self.hit_box.frame.h
                    self.vel.y = 0
                    
        #gravity
        self.vel.y = max(GRAVITY, self.vel.y - 0.5)
        
    
class Player(PhysicsEntity):
    def __init__(self, texture, x, y, *args, **kwargs):
        super().__init__(texture, x, y)
        
        self.anchor_point = (0.5, 0)
        
        self.hit_box = ShapeNode(ui.Path.rect(0, 0, 60, 80), anchor_point=(0.5,0), fill_color = 'clear', stroke_color='red')
        
        self.jumping = False
        self.on_ground = False
        self.jumping_n = 0
        self.move_touch = None
        self.jump_touch = None
    
    def update(self, colliders):
        print('velocity: ', self.vel)
        print('acceleration: ', self.accel)
         
        PhysicsEntity.update(self, colliders)
        
        print('move, jump: ', self.move_touch, self.jump_touch)
        
        if not self.move_touch or self.jump_touch:
            #print('condition met')
            
            if self.vel.x > 0:
                self.vel.x += self.accel.x
                if self.vel.x < 0:
                    self.vel.x = 0
                    self.accel.x = 0
                
            elif self.vel.x < 0:
                self.vel.x += self.accel.x
                if self.vel.x > 0:
                    self.vel.x = 0
                    self.accel.x = 0
                    
        else:
            self.vel.x += self.accel.x
                
        
class Enemy(PhysicsEntity):
    def __init__(self, texture, x, y, *args, **kwargs):
        super().__init__(texture, x, y)
        self.state = 'idle'
        self.old_state = None
        self.state_time = 0
        self.vel.x = 1
        
        self.hit_box = ShapeNode(ui.Path.rect(0, 0, 64, 64), anchor_point=(0.5, 0), fill_color = 'clear', stroke_color='red')
        
        #self.hit_box = self.frame
        
    def set_state(self, player):
        dist = math.sqrt(((self.position.x - player.position.x) ** 2) + (self.position.y - player.position.y) ** 2)
        if dist < 100:
            self.state = 'attack'
        elif dist > 100:
            self.state = 'idle'
        
    def update(self, player, colliders):
        PhysicsEntity.update(self, colliders)
        
        self.set_state(player)
        if self.state == self.old_state:
            self.state_time += 1
        else:
            self.state_time = 0
            
        match self.state:
            case 'idle':
                self.vel.y = 0
                if self.state_time < 120:
                    self.state_time += 1
                else:
                    self.vel.x *= -1
                    self.state_time = 0
            case 'attack':
                dist = math.sqrt((self.position.x - player.position.x) ** 2 + (self.position.y - player.position.y) ** 2)
                self.vel.x = ((self.position.x - player.position.x) * -1) / dist
                self.vel.y = ((self.position.y - player.position.y) * -1) / dist
        
        #self.position += self.vel
        self.old_state = self.state
        #self.vel = Vector2(random.randint(-5, 5) , 0)
        
    
class MyScene (Scene):
    
    def handle_input(self, player, buttons):
        pass
    
    def load_map(self, map_data):
        for j, row in enumerate(map_data):
            for i, col in enumerate(row):
                if MAP_KEY[col] == 'ground':     
                    tile = SpriteNode('plf:Ground_Grass', position = (i * TILE_SIZE, j * TILE_SIZE), anchor_point=(0, 0)) 
                    self.ground.add_child(tile)
                    self.physics_objects.append(tile)
                    
                if MAP_KEY[col] == 'player':
                    initial_player_pos = i, j
    
    def setup(self):
        initial_player_pos = 200, 500
        self.physics_objects = []
        self.ground = Node(parent=self)
        self.background_color = 'cyan'
        self.offset = [0, 0]
            
        self.load_map(LEVEL_ONE)
        
        self.player = Player('plf:AlienBlue_front', 200, 500)
        self.add_child(self.player)
        self.add_child(self.player.hit_box)
        #self.physics_objects.append(self.player.hit_box)
        
        self.enemies = Node(parent=self)
        
        self.enemy_a = Enemy('plf:Enemy_Fly', 100, 200)
        self.enemies.add_child(self.enemy_a)
        
        self.enemy_b = Enemy('plf:Enemy_Fly', 300, 200)
        self.enemies.add_child(self.enemy_b)
        self.add_child(self.enemy_b.hit_box)
        
        self.count = 0
        self.index = 0
        self.walk_count = 0
        self.walk_idx = 0
        
        self.inputs = []
        
        self.right_button = SpriteNode('iow:arrow_left_b_256', position = (65,125))
        self.add_child(self.right_button)

        
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
        self.vel = [0, 0]
        
        self.jumping_n = 0
        
        self.move_touch = None
        self.jump_touch = None
        #print(type(self.vel[0]))
    
    def did_change_size(self):
        pass
    
    def update(self):
        #self.player.anchor_point = (0.5, 0)
        #print(self.physics_objects)
        self.player.update(self.physics_objects)
        
        self.player.vel.y = max(GRAVITY, self.player.vel.y - 0.5)
        
        #self.vel[0] += self.accel[0] 
        if self.player.vel.x > 5:
            self.player.vel.x = 5
        elif self.player.vel.x < -5:
            self.player.vel.x = -5
            
        #flips sprite on x axis if moving to the left (sprite faces right normally)
        #this is why we need to use 0.5, 5 for our anchor point
        if self.player.vel.x < 0:
            self.player.x_scale = -1
        else:
            self.player.x_scale = 1
        
        
        if self.player.on_ground and abs(self.player.vel.x) > 0:
            print('true')
            print(self.walk_idx)
            self.walk_count += 1
            self.player.texture = walk_textures[self.walk_idx]
            
            if self.walk_count > 3:
                self.walk_idx += 1
                self.walk_count = 0
            if self.walk_idx > 1:
                self.walk_idx = 0
                
             
        
        elif self.player.jumping == True:
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
            
        #update enemy entities
        for enemy in self.enemies.children:
            enemy.update(self.player, self.physics_objects)
                
            
        #scrolling background logic
        if self.player.position.x >= SCREEN_WIDTH - (SCREEN_WIDTH / 4) and self.player.vel.x > 0:
            self.offset[0] = self.player.vel.x        
        elif self.player.position.x <= SCREEN_WIDTH / 4 and self.player.vel.x < 0:
            self.offset[0] = self.player.vel.x
        else:
            self.offset[0] = 0
            
            
        for child in self.ground.children:
            child.position -= self.offset
            
        self.player.position -= self.offset
        for child in self.enemies.children:
            child.position -= self.offset
        self.enemy_a.position -= self.offset
        
        #reset touches
        if self.move_touch == None:
            self.player.move_touch = None
        if self.jump_touch == None:
            self.player.jump_touch = None
    
    def touch_began(self, touch):
         
        self.jump_touch = None
        self.move_touch = None
        self.first_touch = touch.location
        if self.first_touch in self.lb_box.frame:
            self.player.accel.x = -.25
            self.move_touch = touch.touch_id
            self.player.move_touch = touch.touch_id
            self.inputs.append(self.move_touch)
        elif self.first_touch in self.rb_box.frame:
            self.player.accel.x = .25
            self.move_touch = touch.touch_id
            self.player.move_touch = touch.touch_id
            self.inputs.append(self.move_touch)
        elif self.first_touch in self.jump_button.frame and self.player.on_ground:
            self.player.jump_touch = touch.touch_id
            self.jump_touch = touch.touch_id
            self.player.vel.y = 25
            self.player.on_ground = False
            self.player.jumping = True
            self.inputs.append(self.jump_touch)
        print(touch.location)
        print(self.touches)
    
    def touch_moved(self, touch):
        pass
    
    def touch_ended(self, touch):
        if touch.touch_id == self.jump_touch:
            pass
        if self.move_touch or not self.touches:
            if self.player.vel.x > 0:
                self.player.accel.x = -0.25
            elif self.player.vel.x < 0:
                self.player.accel.x = 0.25
            elif self.player.vel.x == 0:
                self.player.accel.x = 0
            print('accel: ', self.accel[0])
            self.move_touch = None
        

if __name__ == '__main__':
    run(MyScene(), show_fps=False)
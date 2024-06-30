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

class Aura(SpriteNode):
    def __init__(self, entity, *args, **kwargs):
        SpriteNode.__init__(self, *args, **kwargs)
        self.position = entity.position
        self.z_position = -1
        self.scale = .6
        self.count = 0
        self.anim_idx = 0
        self.textures = [
            'shp:Flash00',
            'shp:Flash01',
            'shp:Flash02',
            'shp:Flash03',
            'shp:Flash04',
            'shp:Flash05',
            ]
            
        self.texture = Texture(self.textures[0])
        #self.effect = SpriteNode(self.textures[self.anim_idx])
        
        self.blend_mode = BLEND_ADD
        self.color = '#ff9e9e'
        
    def run_effect(self, entity):
        self.position = entity.position.x, entity.position.y + 25
        self.texture = Texture(self.textures[self.anim_idx])
        
        self.count += 1
        
        if self.count > 3:
            self.anim_idx += 1
            self.count = 0
            print('yes')
        if self.anim_idx > 5:
            self.anim_idx = 0
            
        print('texture: ', self.texture)
        
class Button(SpriteNode):
    def __init__(self, texture, x_pos, y_pos, hit_width, hit_height, offset=(0,0), *args, **kwargs):
        SpriteNode.__init__(self, texture, position=(x_pos, y_pos), anchor_point=(0,0), *args, **kwargs)
        
        self.pressed = False
        
        self.hit_box = ShapeNode(ui.Path.rect(0, 0, hit_width, hit_height), anchor_point=(0,0), fill_color='clear', stroke_color='green',
        position=offset)

class PhysicsEntity(SpriteNode):
    def __init__(self, texture, x, y, *args, **kwargs):
        SpriteNode.__init__(self, texture, position=(x, y), *args, **kwargs)
        self.vel = Vector2(0, 0)
        self.accel = Vector2(0, 0)
        self.anchor_point = (0.5, 0)
        self.collision = False, None, None
        self.state = 'idle'
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.collided_object = None
       
        self.hit_box = ShapeNode(ui.Path.rect(0, 0, self.frame.w, self.frame.h), position=(0, 50), anchor_point=(0.5,0), fill_color = 'clear', stroke_color='red')
   
        print('frame: ', self.frame)
        print('box frame: ', self.hit_box.frame)
        centerx = self.anchor_point.x
        
    def set_state(self):
        if self.state == self.old_state:
            self.state_time += 1
        else:
            self.state_time = 0
            self.anim_idx = 0
        
    
    def update(self, colliders):
        #collision detection
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.collided_object = None
        correction = 0
        self.position += self.vel.x, 0
        self.hit_box.position = self.position
        for obj in colliders:
            if self.hit_box.frame.intersects(obj.frame) and obj != self:
                self.collided_object = obj
                
                if self.vel.x < 0:
                    self.position = obj.frame.max_x + (self.frame.width/2) + correction, self.position.y
                    self.collisions['left'] = True
                    
                    
                elif self.vel.x > 0:
                    self.position = obj.frame.x - (self.frame.width/2) - correction, self.position.y
                    self.collisions['right'] = True
                    
                else:
                    self.collision = False, None, None
        
        self.position += 0, self.vel.y
        self.hit_box.position = self.position
        for obj in colliders:
            if self.hit_box.frame.intersects(obj.frame) and obj != self:
                self.collided_object = obj
                if self.vel.y < 0:
                    self.position = self.position.x, obj.frame.max_y + correction
                    self.on_ground = True
                    self.jumping = False
                    self.collisions['down'] = True
                   
                elif self.vel.y > 0:
                    self.position = self.position.x, obj.frame.y - self.hit_box.frame.h - correction
                    self.collisions['up'] = True
                    
                else:
                    self.collision = False, None, None
        if self.collided_object:
            print('entity: ', self,' collision: ' , self.collisions, ' with: ', self.collided_object)        
                                   
        #gravity
        self.vel.y = max(GRAVITY, self.vel.y - 0.5)
        
        if self.collisions['up'] or self.collisions['down']:
            self.vel.y = 0
        
    
class Player(PhysicsEntity):
    def __init__(self, texture, x, y, *args, **kwargs):
        super().__init__(texture, x, y)
        
        self.anchor_point = (0.5, 0)
        
        self.hit_box = ShapeNode(ui.Path.rect(0, 0, 60, 80), anchor_point=(0.5,0), fill_color = 'clear', stroke_color='red', z_position=1)
        
        self.jumping = False
        self.on_ground = False
        self.jumping_n = 0
        self.move_touch = None
        self.jump_touch = None
        
        self.state = 'idle'
        self.old_state = None
        
        self.state_time = 0
        self.anim_idx = 0
        
        self.effect = None
        self.aura = None
        
        self.textures = { 
            'idle': [
                'plf:AlienBlue_front',
                'plf:AlienBlue_stand'
                ],
            'fall': [
                'plf:AlienBlue_jump'
                ],
            'walk': [
                'plf:AlienBlue_walk1',                 'plf:AlienBlue_walk2'
                ],
            'jump': [
                'shp:Flash00',
                'shp:Flash01',
                'shp:Flash02',
                'shp:Flash03',
                'shp:Flash04',
                'shp:Flash05',
                ]
                }
    
    def set_state(self, colliders):
        if self.on_ground and abs(self.vel.x) > 0:
            self.state = 'walk'
        #elif not self.on_ground and self.vel.y < 0:
            #self.state = 'fall'
        elif self.on_ground and self.vel.x == 0:
            self.state = 'idle'
            
        elif self.jumping and self.vel.y > 0:
            self.state = 'jump'
        
        #getting hit
        print(type(self.collided_object))
        if (self.collisions['up'] or self.collisions['left'] or self.collisions['right']) and type(self.collided_object) == Enemy:
            self.state = 'hit'
            print('hit')
    
            
        #print(self.collision)
            
        if self.state == self.old_state:
            self.state_time += 1
        else:
            self.state_time = 0
            self.anim_idx = 0
            
        if self.state != self.old_state:
            if self.old_state == 'jump':
                self.aura.remove_from_parent()
                self.aura = None
        
    def update(self, colliders):
        print('velocity: ', self.vel)
        print('acceleration: ', self.accel)
         
        PhysicsEntity.update(self, colliders)
        
        print('move, jump: ', self.move_touch, self.jump_touch)
        
        self.set_state(colliders)
        print('player state: ', self.state)
        match self.state:
            case 'idle':
                self.state_time += 1
                self.texture = Texture(self.textures['idle'][self.anim_idx])
                
                if self.state_time > 20:
                    self.anim_idx += 1
                    self.state_time = 0
                if self.anim_idx > 1:
                    self.anim_idx = 0
            case 'fall':
                self.texture = Texture(self.textures['fall'][self.anim_idx])
            case 'walk':
                self.state_time += 1
                self.texture = Texture(self.textures['walk'][self.anim_idx])
                
                if self.state_time > 10:
                    self.anim_idx += 1
                    self.state_time = 0
                if self.anim_idx > 1:
                    self.anim_idx = 0
                
            case 'jump':
                if self.state != self.old_state:
                    self.aura = Aura(self)
                    #self.aura.anchor_point = (0.5,0.5)
                    self.parent.add_child(self.aura)
                    
                self.aura.run_effect(self)
            
                self.texture = Texture('plf:AlienBlue_jump')
                
                #print('aura animation index: ', aura.anim_idx)
            case 'hit':
                #self.state_time +=1
                self.texture = Texture('plf:AlienBeige_hit')
                
                
                if self.state_time > 300:
                    self.state = 'idle'
                    
        self.old_state = self.state
        
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
            
        #getting hit
        print('player type: ', type(self.collided_object))
        a = self.collisions['up'] == True
        b = player.collisions['down'] == True
        c = player.collided_object == self
        d = type(self.collided_object) == Player
        if (a or (b and c)) and d:
            self.state = 'hit'
            print('hit')
        
    def update(self, player, colliders):
        PhysicsEntity.update(self, colliders)
        
        if self.state == self.old_state:
            self.state_time += 1
        else:
            self.state_time = 0
        
        self.set_state(player)
        print('enemy state: ', self.state)
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
            case 'hit':
                colliders.remove(self)
                self.remove_from_parent()
        
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
        
        self.effect_node = EffectNode(parent=self)
        self.game_node = Node(parent=self.effect_node)
            
        self.load_map(LEVEL_ONE)
        
        self.entities = Node(parent=self)
        
        self.player = Player('plf:AlienBlue_front', 200, 500)
        self.entities.add_child(self.player)
        self.add_child(self.player.hit_box)
        self.physics_objects.append(self.player)
        
        self.enemies = Node(parent=self)
        
        self.enemy_a = Enemy('plf:Enemy_Fly', 100, 200)
        self.enemies.add_child(self.enemy_a)
        
        self.enemy_b = Enemy('plf:Enemy_Fly', 300, 200)
        self.enemies.add_child(self.enemy_b)
        #self.add_child(self.enemy_b.hit_box)
        self.physics_objects.append(self.enemy_a)
        self.physics_objects.append(self.enemy_b)
        
        self.count = 0
        self.index = 0
        self.walk_count = 0
        self.walk_idx = 0
        
        self.inputs = []
        
        self.left_button = Button('iow:arrow_left_b_256', -65, 0, 115, 170, offset=(0,40))
        self.add_child(self.left_button)
        self.add_child(self.left_button.hit_box)
        
        self.right_button = SpriteNode('iow:arrow_right_b_256', position = (175,125))
        self.add_child(self.right_button)
        
        self.rb_box = ShapeNode(ui.Path.rect(0.00, 0.00, 115.00, 170.00), anchor_point=(0,0), position=(120,40), fill_color = 'clear', stroke_color='green', parent=self)
        #print(self.lb_box.frame)
        
        self.jump_button = SpriteNode('iow:ios7_circle_filled_256', position=(310, 125), scale=.5)
        self.add_child(self.jump_button)
        
        
        self.jumping = False
        self.on_ground = False
        self.accel = [0, 0]
        #self.vel = [0, 0]
        
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
        
        #self.player.vel.y = max(GRAVITY, self.player.vel.y - 0.5)
        
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
                    
        #else:
            #self.player.texture = Texture('plf:AlienBlue_front')
            
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
        if self.first_touch in self.left_button.hit_box.frame:
            self.left_button.pressed = True
            self.left_button.texture = Texture('iob:arrow_left_b_256')
            self.player.accel.x = -.25
            self.move_touch = touch.touch_id, 'left'
            self.player.move_touch = touch.touch_id
            self.inputs.append(self.move_touch)
        elif self.first_touch in self.rb_box.frame:
            self.player.accel.x = .25
            self.move_touch = touch.touch_id, 'right'
            self.player.move_touch = touch.touch_id
            self.inputs.append(self.move_touch)
        elif self.first_touch in self.jump_button.frame and self.player.on_ground:
            self.player.jump_touch = touch.touch_id
            self.jump_touch = touch.touch_id
            self.player.vel.y = 15
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
            if self.move_touch and self.move_touch[1] == 'left':
                self.left_button.texture = Texture('iow:arrow_left_b_256')
            if self.player.vel.x > 0:
                self.player.accel.x = -0.25
            elif self.player.vel.x < 0:
                self.player.accel.x = 0.25
            elif self.player.vel.x == 0:
                self.player.accel.x = 0
            #print('accel: ', self.accel[0])
            self.move_touch = None
        

if __name__ == '__main__':
    run(MyScene(), show_fps=False)
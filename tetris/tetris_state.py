import pygame
import tetris_shapes
import random
import operator
import tetris_palette

WHITE = (255, 255, 255)

class State:
    def __init__(self):

        self.random_shape = 0  # debug

        self.level=0
        self.lines_completed=0
        self.seed=0
        self.acc_time=0
        self.speed=0.05 #0.01px/ms

        # game size data
        self.width_column=12 #nb_blocks
        self.height_column=18 #nb_blocks

        # rendering data
        self.blocksize_px = 30 #pixels
        self.width_px = self.width_column*self.blocksize_px
        self.height_px = self.height_column*self.blocksize_px
        self.offset_x_left_px = 2 # clearance on left of game rectangle
        self.offset_x_right_px = 2 # clearance on right of game rectangle
        self.offset_y_bottom_px = 2 # clearance at bottom of game rectangle

        self.shape=None #shape going down
        self.nextShape=None #shape going down
        self.blocks=[[0 for i in range(self.height_column)] for j in range(self.width_column)] #individual static blocks

        self.cb_invalidateBackground = None
        self.cb_invalidateStats = None

    def reset_game(self):
        self.level = 0
        self.lines_completed = 0
        self.seed = 0
        self.acc_time = 0
        self.speed = 0.05  # 0.01px/ms

        self.shape = None  # shape going down
        self.nextShape = None  # shape going down
        self.blocks = [[0 for i in range(self.height_column)] for j in
                       range(self.width_column)]  # individual static blocks
        self.cb_invalidateBackground = None
        self.cb_invalidateStats = None

    def gravity_moveShape(self):
        float_pos = self.shape.acc_forced_gravity + \
                    (self.acc_time - self.shape.creation_time)*self.speed/self.blocksize_px #gravity over time
        nb_blocks = int(float_pos)

        #print ("Moving shape down : "+str(nb_blocks)+" vs "+str(self.shape.y))
        if nb_blocks > self.shape.y:
            return self.shape.tryNewPos(self.shape.x, nb_blocks, self.shape.rotation,
                                        (self.width_column, self.height_column),
                                        self.blocks)
        return True

    def user_action_moveShape(self, shift_pos_x, shift_pos_y, rot):
        if self.shape:
            new_pos_x = self.shape.x + shift_pos_x
            new_pos_y = self.shape.y + shift_pos_y
            new_rot = (self.shape.rotation + rot) %4
            if not self.shape.tryNewPos(new_pos_x, new_pos_y, new_rot,
                                 (self.width_column, self.height_column),
                                 self.blocks) and shift_pos_y != 0: # only freeze when going down
                self.freezeShape()
            else: #user has moved the shape at a valid position
                self.shape.acc_forced_gravity = self.shape.acc_forced_gravity + shift_pos_y

    def nextFrame(self, addedTime):
        self.acc_time = self.acc_time + addedTime
        if not self.shape:
            if not self.nextShape:
                self.nextShape = self.newShape(-1)
            self.shape = self.nextShape
            self.shape.creation_time = self.acc_time
            self.nextShape = self.newShape(self.acc_time)
            print ("NEW SHAPE CREATED")
            if not self.shape.tryNewPos(self.shape.x, self.shape.y, self.shape.rotation,
                                        (self.width_column, self.height_column),
                                        self.blocks):
                # shape is created and is already touching something
                print("Game Over with "+str(self.lines_completed)+ " lines completed.")
                return False

        else:
            #compute new position of current shape
            if not self.gravity_moveShape(): # shape is blocked by something
                self.freezeShape()
        return True

    def newShape(self, creation_time):
        size = len(tetris_shapes.basic_shapes)
        chosen = random.randint(0, size-1)
        # chosen = self.random_shape
        # self.random_shape = (self.random_shape + 1 )%size
        created_shape = tetris_shapes.Shape((len(tetris_shapes.basic_shapes[chosen]), len(tetris_shapes.basic_shapes[chosen][0])), self.blocksize_px, creation_time)# should be random among tetris 8 shapes
        created_shape.x = int((self.width_column-created_shape.size[0])/2)
        created_shape.color = tetris_palette.SHAPES_COLORS[chosen]
        created_shape.blocks = tetris_shapes.basic_shapes[chosen]
        return created_shape

    def freezeShape(self):
        print("Storing shape blocks as background")
        modified_rows = []
        for (pos_x, pos_y) in self.shape.it_blocks().iter_on_blocks():
            self.blocks[pos_x][pos_y] = 1
            if not pos_y in modified_rows:
                modified_rows.append(pos_y)
        # search completed lines
        completed_rows=[]
        for y in modified_rows:
            all_blocks_so_far=True
            for i in range(self.width_column):
                if not self.blocks[i][y]:
                    all_blocks_so_far = False
                    break
            if all_blocks_so_far:
                completed_rows.append(y)
        for j in completed_rows:
            for i in range(self.width_column):
                self.blocks[i][j] = 0
        # tass
        completed_rows.sort()
        completed_rows.reverse()
        for j in completed_rows:
            print("Removing row "+str(j))
        for j in completed_rows:
            for column in self.blocks:
                column.pop(j)
        for j in completed_rows:
            for column in self.blocks:
                column.insert(0, 0)

        #        self.blocks[i][j] = 0
        if not self.cb_invalidateBackground is None:
            self.cb_invalidateBackground.invalidateBackground()
        self.shape = None

        # update score
        if len(completed_rows):
            self.lines_completed = self.lines_completed + len(completed_rows)
            new_level = int(self.lines_completed / 10)
            if new_level > self.level:
                self.speed =self.speed * 1.2
                self.level = new_level
            self.cb_invalidateStats.invalidateStats()
            print (str(len(completed_rows))+ " lines completed (total: "+str(self.lines_completed)+")")

    def compute_Background_Screen(self):
        SIZE_RECT = (self.width_px + self.offset_x_left_px + self.offset_x_right_px,  # +4 for the borders
                     self.height_px + self.offset_y_bottom_px)  # +2 for the bottom border
        # print ("height of game: "+str(SIZE_RECT[1]))
        background = pygame.Surface(SIZE_RECT)  # The tuple represent size.
        background.fill(tetris_palette.GAME_BACKGROUND)
        #left border: 0-1
        pygame.draw.line(background, tetris_palette.BACK_COLORS[3], (0,0), (0,self.height_px),2)
        #right border: width_px+1 - width_px+3
        pygame.draw.line(background, tetris_palette.BACK_COLORS[3], (self.width_px+self.offset_x_left_px,0), (self.width_px+self.offset_x_left_px,self.height_px),2)
        #bottom border
        pygame.draw.line(background, tetris_palette.BACK_COLORS[3], (0,self.height_px), (self.width_px+self.offset_x_left_px, self.height_px), 2)

        #add all blocks here
        one_block_surf = pygame.Surface((self.blocksize_px, self.blocksize_px))
        one_block_surf.fill(tetris_palette.BACK_COLORS[3])
        pygame.draw.rect(one_block_surf, tetris_palette.BACK_COLORS[0], [0, 0, self.blocksize_px, self.blocksize_px], 1)

        for (i,j) in self.blocks_iter():
            background.blit(one_block_surf, (i*self.blocksize_px+self.offset_x_left_px, j*self.blocksize_px))
        return background

    def compute_Stats_Screen(self, font):
        message = "lignes : "+str(self.lines_completed)
        status_lines_surf, size_lines_surf = font.render(message, fgcolor=WHITE)

        level = "niveau : "+str(self.level)
        status_level_surf, size_level_surf = font.render(level, fgcolor=WHITE)

        text_spacing = 10
        surf_stats = pygame.Surface((size_lines_surf[2] + size_level_surf[2], size_lines_surf[3] + size_level_surf[3] + text_spacing), pygame.SRCALPHA)
        surf_stats.blit(status_lines_surf,(0,0))
        surf_stats.blit(status_level_surf, (0,status_lines_surf.get_size()[1] + text_spacing))
        return surf_stats

    def blocks_iter(self):
        for i in range (self.width_column):
            for j in range (self.height_column):
                if self.blocks[i][j]:
                    yield (i,j)

    def computeShapePosPx(self):
        if self.shape:
            pos_shape = self.shape.computePosPx()
            return (pos_shape[0]+2, pos_shape[1])
        return (0,0)
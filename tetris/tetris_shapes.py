import pygame
import tetris_palette



class Block:
    """Block is the elementary constituent of shapes in Tetris.
    Each shape will compose multiple blocks."""
    def __init__(self, size):
        self.size = size # nb pixels width

class ShapeBlocksIter:
    """Iterator for the blocks of a Shape.
     Iteration yields to coordinates of each block in absolute position."""
    def __init__(self, shape):
        self.rotation = shape.rotation
        self.blocks = shape.blocks.copy()
        self.size = shape.size
        self.x = shape.x
        self.y = shape.y
        self.i = 0
        self.j = 0

    def overwrite (self, overX, overY, overRot):
        self.rotation = overRot
        self.x = overX
        self.y = overY

    def iter_on_blocks(self):
        size_x = self.size[0]
        size_y = self.size[1]
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.blocks[i][j]:
                    if self.rotation==0:
                        yield (int(self.x + i), int(self.y+j))
                    elif self.rotation==1:
                        yield (int(self.x + j ), int( self.y + size_x -i -1) )
                    elif self.rotation == 2:
                        yield (int(self.x+ size_x-i-1), int(self.y + size_y -j -1))
                    elif self.rotation ==3:
                        yield (int(self.x+ size_y-j-1), int(self.y + i))



class Shape:
    def __init__(self, size, block_size, creation_time):
        assert (len(size)==2)
        self.size = size #tuple (w, h)
        self.block_size=block_size
        self.blocks = [[0 for i in range(size[1])] for j in range(size[0])]
        self.rotation = 0 #0, 1, 2, or 3
        self.y = 0 # 0 is topmost position
        self.x = 0 # leftmost position
        self.creation_time = creation_time
        self.acc_forced_gravity = 0 # count nb of times shape is dragged down by player
        self.float_pos_y = 0.0
        self.image = None
        self.color = (255,0,0)


    def computeImage(self):
        if self.image:
            return self.image
        self.image = pygame.Surface((self.size[0]*self.block_size, self.size[1]*self.block_size), flags = pygame.SRCALPHA)
        self.image.fill((0,0,0,0))
        size_rect = (self.block_size, self.block_size)
        rect = pygame.Rect((0,0), size_rect)
        imageRect = pygame.Surface(size_rect)
        imageRect.fill(self.color)
        for j in range(self.size[1]):
            for i in range(self.size[0]):
                if self.blocks[i][j]:
                    self.image.blit(imageRect, (i*self.block_size, j*self.block_size))
        self.image = pygame.transform.rotate(self.image, self.rotation * 90)
        return self.image

    def computePosPx(self):
        return (self.x * self.block_size, self.y*self.block_size)

    def it_blocks(self):
        return ShapeBlocksIter(self)

    def tryNewPos(self, new_pos_x, new_pos_y, new_rot, bounds, static_blocks):
        """Checks whether a new position for the shape is valid or not.
        new_pos_x, new_pos_y, new_rot are the inputs for the new position.
        bounds are corresponding to the size of the game rectangle.
        static_blocks are corresponding to blocks already frozen in the game.
        tryNewPos will return False if Shape should freeze, True otherwise"""
        size_rotation = self.size
        rotated_blocks = self.blocks
        if new_rot == 1 or new_rot == 3:
            size_rotation = (self.size[1], self.size[0])

        # check for clashes with bounds
        if new_pos_x <0 or new_pos_x+size_rotation[0] > bounds[0]:
            print ("Clash with side")
            return True
        if new_pos_y <0 or new_pos_y + size_rotation[1] > bounds[1]:
            print ("Clash with bottom at pos ("+str(new_pos_x)+", "+str(new_pos_y)+")")
            return False

        iter_blocks = self.it_blocks()
        iter_blocks.overwrite(new_pos_x, new_pos_y, new_rot)
        for (pos_x, pos_y) in iter_blocks.iter_on_blocks():
            if static_blocks[pos_x][pos_y]:
                print ("clash at pos ("+str(new_pos_x)+", "+str(new_pos_y)+")with existing block ("+str(pos_x)+", "+str(pos_y)+")")
                return False

        # if no clash, move the shape
        if self.x != new_pos_x or self.y != new_pos_y:
            #print("Changing shape position to ("+str(new_pos_x)+", "+str(new_pos_y)+")")
            self.x = new_pos_x
            self.y = new_pos_y
        if new_rot != self.rotation:
            self.rotation = new_rot
            self.image = None # necessary to invalidate Shape display after a rotation
        return True

basic_shapes=[]
T_shape=[[1,1,1],[0,1,0]]
L_shape=[[1,0], [1,0], [1,1]]
L_shape_2 = [[0,1], [0,1], [1,1]]
I_shape=[[1],[1],[1],[1]]
S_shape=[[0,1], [1,1], [1,0]]
S_shape_2 = [[1,0], [1,1], [0,1]]
Square_shape = [[1,1],[1,1]]
basic_shapes.extend((L_shape, S_shape, I_shape, T_shape, Square_shape, S_shape_2, L_shape_2))
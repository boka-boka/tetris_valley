import tetris_state
import pygame
import pygame.freetype
import tetris_palette

def createSeparator(width, height, color):
   pass

class Render:
   def __init__(self, t_state, screen):
      self.t_state = t_state
      self.screen = screen
      self.background = None
      self.stats = None
      self.stats_size = None
      t_state.cb_invalidateBackground = self
      t_state.cb_invalidateStats = self

      pygame.freetype.init()
      self.tetris_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 20)

      # colors
      self.BACKGROUND_COLOR = tetris_palette.BACK_COLORS[0]
      self.screen.fill(self.BACKGROUND_COLOR)
      # offsets
      self.clearance = 20
      self.separator = createSeparator(0, self.clearance, tetris_palette.BACK_COLORS[3])

   def drawBackground (self):
      if not self.background:
         self.background = self.t_state.compute_Background_Screen()
         self.screen.blit(self.background, (0,0))
      #clean old shape position
      if self.t_state.shape:
         shapeRectCopy = self.t_state.shape.computeImage().get_rect().copy()
         shapeRectCopy.move_ip(self.t_state.computeShapePosPx())
         self.screen.blit(self.background, shapeRectCopy, shapeRectCopy )

   def drawStats (self):

      if not self.stats:
         if self.stats_size:
            offset_stats_surf = (self.t_state.width_px + self.clearance,
                                 self.clearance)
            rect_to_blank = offset_stats_surf + self.stats_size
            self.screen.fill(self.BACKGROUND_COLOR, rect_to_blank)
         self.stats = self.t_state.compute_Stats_Screen(self.tetris_font)
         self.stats_size = self.stats.get_size()

         self.screen.blit(self.stats, (self.t_state.width_px + self.clearance,
                                       self.clearance))

   def drawShape(self):
      if self.t_state.shape:
         imShape = self.t_state.shape.computeImage()
         self.screen.blit(imShape, self.t_state.computeShapePosPx())

      # next shape frame on the right of the screen
      if self.t_state.nextShape and self.stats_size:
         imNextShape = self.t_state.nextShape.computeImage()
         rect_frame = (self.t_state.blocksize_px*5, self.t_state.blocksize_px*5)
         frame = pygame.Surface(rect_frame, pygame.SRCALPHA)
         pygame.draw.rect(frame, tetris_palette.GAME_BACKGROUND, (0,0)+rect_frame, 0, int(self.t_state.blocksize_px/2))
         pygame.draw.rect(frame, tetris_palette.BACK_COLORS[3], (0,0)+rect_frame, 2, int(self.t_state.blocksize_px/2))
         frame.blit(imNextShape, ((5-self.t_state.nextShape.size[0])*self.t_state.blocksize_px/2,
                                  (5-self.t_state.nextShape.size[1])*self.t_state.blocksize_px/2))
         self.screen.blit(frame, ((self.t_state.width_px + self.screen.get_size()[0]-frame.get_size()[0])/2,
                          self.stats_size[1] + self.clearance*2))

   def invalidateBackground(self):
      self.background = None

   def invalidateStats(self):
      self.stats = None
import pygame
import tetris_state
import tetris_render

# workflow of the game is the following
# main menu : start, high score, quit, settings
#    start -> main loop
#        pause
#           abandon
#           continue
#           load_blocks (debug)
#           save_blocks (debug)
#        end game
#           save result
#           restart (goto start)
#    high score : show best scores
#    settings : ...
class GameControler:
    def __init__(self):
        self.game_render = None
        self.state = None
        self.screen = None
        self.clock = None

        self.move = (0, 0)
        self.rot = 0

    def initialize(self, clock, state, screen):
        self.state = state
        self.screen = screen
        self.clock = clock
        self.game_render = tetris_render.Render(state, screen)

    def on_loop_begin(self):
        self.move = (0, 0)
        self.rot = 0

    def on_user_event(self, event):
        if event is None:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.move = (0, 1)
            elif event.key == pygame.K_LEFT:
                self.move = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.move = (1, 0)
            if event.unicode == "w":
                self.rot = 1
            elif event.unicode == "x":
                self.rot = -1

    def on_loop_end(self):
        self.game_render.drawBackground()
        self.state.user_action_moveShape(self.move[0], self.move[1], self.rot)
        if self.state.nextFrame(self.clock.get_time()): #nextFrame returns True until game is over
            self.game_render.drawShape()
        else:
            quit()
        self.game_render.drawStats()

class MainControler:
    def __init__(self, state):
        self.gc = GameControler()
        self.stack_controlers = None

    def initialize(self, clock, state, screen):
        if self.stack_controlers:
            self.stack_controlers.push(self.gc)
            self.gc.initialize(clock, state, screen)

    def on_loop_begin(self):
        self.gc.on_loop_begin()

    def on_user_event(self, event):
        self.gc.on_user_event(event)

    def on_loop_end(self):
        self.gc.on_loop_end()

class ControlerStack:
    def __init__(self):
        self.stack = []

    def push(self, controler):
        self.stack.append(controler)
        controler.stack_controlers = self

    def on_loop_begin(self):
        if len(self.stack):
            self.stack[-1].on_loop_begin()

    def on_user_event(self, event):
        if len(self.stack):
            self.stack[-1].on_user_event(event)

    def on_loop_end(self):
        if len(self.stack):
            self.stack[-1].on_loop_end()

class TetrisGame:
    def __init__(self):
        FPS = 60  # This variable will define how many frames we update per second.
        KEY_REPEAT = (400, 30)
        WINDOW_SIZE = (600, 542)

        successes, failures = pygame.init()
        print("{0} successes and {1} failures".format(successes, failures))
        pygame.key.set_repeat(KEY_REPEAT[0], KEY_REPEAT[1])



        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption('Tetris v0.1 by Erwan')

        game_state = tetris_state.State()
        stack_controlers = ControlerStack()
        main_controler = MainControler(game_state)
        stack_controlers.push(main_controler)
        clock = pygame.time.Clock()
        main_controler.initialize(clock, game_state, screen)
        game_running = True
        while game_running:
            clock.tick(FPS)

            stack_controlers.on_loop_begin()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                stack_controlers.on_user_event(event)
            stack_controlers.on_loop_end()

            pygame.display.update()  # Or 'pygame.display.flip()'.

        quit()

TetrisGame()
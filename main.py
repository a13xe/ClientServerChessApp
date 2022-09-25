####################################################################################################
#                                                                                                  #
#    ##########################################################################################    #
#    #                                                                                        #    #
#    #    Программный модуль инициализации приложения и построения графического интерфейса    #    #
#    #                                                                                        #    #
#    ##########################################################################################    #
#                                                                                                  #
####################################################################################################

import os
import sys
import copy
import time
import queue
import pygame
import tkinter
import itertools
import threading
import subprocess
import customtkinter
import tkinter.messagebox
import platform
if platform.system == "Windows":
    os.environ['SDL_VIDEODRIVER'] = 'windib'

import chessBoard
import chessEngine

customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

###################################
#                                 #
#    Параметры шахматной доски    #
#                                 #
###################################
B_WIDTH = B_HEIGHT = 480            # width and height of the chess board
DIMENSION = 8                       # the dimensions of the chess board
SQ_SIZE = B_HEIGHT // DIMENSION     # the size of each of the squares in the board
IMAGES = {}                         # images for the chess pieces
MAX_FPS = 60                        # FPS for animations
pieceDir = "Assets/Pieces/"         # Стандартная папка для изображений фигур

def loadImages():
    """Загрузка изображений для шахматных фигур из класса chessBoard
    """
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ',
              'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(pieceDir + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def loadBoard(screen, chessboard):
    """Загрузка шахматной доски
    """
    drawBoard(screen)
    drawPieces(screen, chessboard.board)


def drawBoard(screen):
    """Рисование шахматной доски
    """
    colors = [pygame.Color("#edede9"), pygame.Color("#457b9d")]
    # for i in range(DIMENSION): for j in range(DIMENSION):
    for i, j in itertools.product(range(DIMENSION), range(DIMENSION)):
        color = colors[((i+j) % 2)]
        pygame.draw.rect(screen, color, pygame.Rect(j*SQ_SIZE, i*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, chessboard):
    """Рисование шахматных фигур
    """
    for i, j in itertools.product(range(DIMENSION), range(DIMENSION)):
        piece = chessboard[i][j]
        if piece != "--":
            screen.blit(IMAGES[piece], pygame.Rect(j*SQ_SIZE, i*SQ_SIZE, SQ_SIZE, SQ_SIZE))


 #####################################################
 #                                                   #
 #    Создание окна для работы пользователя - GUI    #
 #                                                   #
 #####################################################
class App(customtkinter.CTk):
    WIDTH = 750  # Задание ширины окна приложения
    HEIGHT = 500  # Задание высоты окна приложения

    def __init__(self):
        super().__init__()  # Определение родительского класса

        ##########################################
        #                                        #
        #    Присвение значений по умолчанию     #
        #                                        #
        ##########################################
        self.title("Игра в Шахматы")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        # self.minsize(App.WIDTH, App.HEIGHT)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        if sys.platform == "darwin":
            self.bind("<Command-q>", self.on_closing)
            self.bind("<Command-w>", self.on_closing)
            self.createcommand('tk::mac::Quit', self.on_closing)

        ########################
        #                      #
        #    Создание окон     #
        #                      #
        ########################
        # Настройка макета сетки (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        # Создание окон (1x2)
        self.frame_left_menu = customtkinter.CTkFrame(master=self, width=180, corner_radius=0)
        self.frame_left_menu.grid(row=0, column=0, sticky="nswe")
        self.frame_right_play = customtkinter.CTkFrame(master=self)
        self.frame_right_play.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        self.frame_right_info = customtkinter.CTkFrame(master=self)
        self.frame_right_info.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        ############################
        #                          #
        #    Левое окно - МЕНЮ     #
        #                          #
        ############################
        # Настройка макета сетки
        self.frame_left_menu.grid_rowconfigure(6, weight=1)
        self.frame_left_menu.grid_rowconfigure(11, minsize=10)
        self.label_menu = customtkinter.CTkLabel(master=self.frame_left_menu, text="МЕНЮ", text_font=("Roboto Medium", -16))
        self.label_menu.grid(row=0, column=0, pady=10, padx=10)
        # Кнопки
        self.button_play = customtkinter.CTkButton(master=self.frame_left_menu, text="Играть", fg_color=("gray75", "#64897e"), width=180, height=40, command=self.button_play_event)
        self.button_play.grid(row=1, column=0, pady=10, padx=20)
        self.button_info = customtkinter.CTkButton(master=self.frame_left_menu, text="О программе", fg_color=("gray75", "#64897e"), width=180, height=40, command=self.button_info_event)
        self.button_info.grid(row=2, column=0, pady=10, padx=20)
        # Переключатель темной темы
        self.switch_dark_theme = customtkinter.CTkSwitch(master=self.frame_left_menu, text="Темная тема", command=self.change_mode)
        self.switch_dark_theme.grid(row=10, column=0, pady=10, padx=20, sticky="w")

        ###############################################
        #                                             #
        #    Правое окно - информация о программе     #
        #                                             #
        ###############################################
        # Настройка макета сетки
        self.frame_right_info.rowconfigure(14, weight=10)
        self.frame_right_info.columnconfigure(0, weight=1)
        self.label_info = customtkinter.CTkLabel(master=self.frame_right_info, text="Информация о программе", text_font=("Roboto Medium", -16))
        self.label_info.grid(row=0, column=0, pady=10, padx=10)
        self.label_info_info = customtkinter.CTkLabel(master=self.frame_right_info, height=100, text_font=("Roboto Medium", -16), fg_color=("white", "gray38"), justify=tkinter.LEFT, text="\n \n")
        self.label_info_info.grid(row=1, column=0, sticky="we", padx=15, pady=15)
        self.label_info_authors = customtkinter.CTkLabel(master=self.frame_right_info, height=200, text_font=("Roboto Medium", -16), fg_color=("white", "gray38"), text="\n \n")
        self.label_info_authors.grid(row=2, column=0, sticky="we", padx=15, pady=15)
        
        ################################
        #                              #
        #    Окно для игр в шахматы    #
        #                              #
        ################################
        # Настройка макета сетки        
        # screen = pygame.display.set_mode((B_WIDTH, B_HEIGHT))
        self.frame_right_play.rowconfigure(14, weight=10)
        self.frame_right_play.columnconfigure(0, weight=1) 
        self.label_info_play = customtkinter.CTkLabel(master=self.frame_right_play, height=100, text_font=("Roboto Medium", -16), fg_color=("white", "gray38"), justify=tkinter.LEFT, text="\n \n")
        self.label_info_play.grid(row=1, column=0, sticky="we", padx=15, pady=15)
        
        screen = pygame.display.set_mode((B_WIDTH, B_HEIGHT))
        clock = pygame.time.Clock()
        screen.fill(pygame.Color("black"))  
        board = chessBoard.chessBoard()
        loadImages()
        loadBoard(screen, board)
        
        print(type(screen)) # <class 'pygame.Surface'>

        

        ##########################################
        #                                        #
        #    Присвение значений по умолчанию     #
        #                                        #
        ##########################################
        self.hide_menu_frames()
        self.frame_right_play.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        self.switch_dark_theme.select()
        if self.switch_dark_theme.get() == 1:
            self.button_play.configure(fg_color=("gray75", "#5c8da4"))
        else:
            self.button_play.configure(fg_color=("#7db8d4"))

    ###################################################
    #                                                 #
    #    Функции для вызова окон и других функций     #
    #                                                 #
    ###################################################
    def hide_menu_frames(self):
        self.frame_right_info.grid_forget()
        self.frame_right_play.grid_forget()
        self.button_info.configure(fg_color=("gray75", "gray30"))
        self.button_play.configure(fg_color=("gray75", "gray30"))

    ##################################################
    #                                                #
    #    Функции для управления параметрами окон     #
    #                                                #
    ##################################################
    def button_info_event(self):
        self.hide_menu_frames()
        self.frame_right_info.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        if self.switch_dark_theme.get() == 1:
            self.button_info.configure(fg_color=("gray75", "#5c8da4"))
        else:
            self.button_info.configure(fg_color=("#7db8d4"))

    def button_play_event(self):
        self.hide_menu_frames()
        self.frame_right_play.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        if self.switch_dark_theme.get() == 1:
            self.button_play.configure(fg_color=("gray75", "#5c8da4"))
        else:
            self.button_play.configure(fg_color=("#7db8d4"))

    def change_mode(self):
        if self.switch_dark_theme.get() == 1:
            customtkinter.set_appearance_mode("Dark")
        else:
            customtkinter.set_appearance_mode("Light")

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()


##################################
#                                #
#    Инициализация программы     #
#                                #
##################################
if __name__ == "__main__":
    pygame.init()

    # # print(board.board) # debug
    # running = True
    # while running:
    #     for e in pygame.event.get():
    #         if e.type == pygame.QUIT:
    #             running = False
    #         clock.tick(MAX_FPS)
    #         pygame.display.flip()

    app = App()
    app.start()

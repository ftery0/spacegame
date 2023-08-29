import pygame
import gameview
def startView():
    pygame.init()
    startScr = pygame.display.set_mode([500, 800])
    pygame.display.set_caption('원석 부수기')
    startBtnObj = pygame.Rect(100, 150, 300, 70)
    startinfom = pygame.Rect(200, 350, 150, 70)
    stopbt = pygame.Rect(180, 550, 150, 70)
    backGImg = pygame.image.load("../texture/back_ground_Ui.gif")
    backGImg = pygame.transform.scale(backGImg, [500, 800])
    pygame.mixer.music.load("../texture/backsound.mp3")
    pygame.mixer.music.play(-1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if startBtnObj.collidepoint(event.pos):
                    gameview.gameStart()
                if startinfom.collidepoint(event.pos):
                    gameview.gameinform()
                if stopbt.collidepoint(event.pos):
                    pygame.quit()
                    return
        startScr.blit(backGImg, [0, 0])
        font = pygame.font.Font("../font/BMDOHYEON_ttf.ttf", 50)
        startText = font.render("게임 시작하기", True, [255, 255, 255])
        if startBtnObj.collidepoint(pygame.mouse.get_pos()):
            startText = font.render("게임 시작하기", True, [255, 0, 0])
        startScr.blit(startText, [startBtnObj.x, startBtnObj.y])
        startinfomtext = font.render("정보", True, [255, 255, 255])
        if startinfom.collidepoint(pygame.mouse.get_pos()):
            startinfomtext = font.render("정보", True, [255, 0, 0])
        startScr.blit(startinfomtext, [startinfom.x, startinfom.y])
        stopbttext = font.render("나가기", True, [255, 255, 255])
        if stopbt.collidepoint(pygame.mouse.get_pos()):
            stopbttext = font.render("나가기", True, [255, 0, 0])
        startScr.blit(stopbttext, [stopbt.x, stopbt.y])
        pygame.display.flip()
startView()

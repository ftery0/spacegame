import pygame
import random
def gameStart():
    pygame.init()
    gameScr = pygame.display.set_mode([500, 800])
    fps = pygame.time.Clock()
    back = pygame.Rect(10, 750, 150, 50)
    backGroundImg = pygame.image.load("../texture/back_ground_Ui.gif")
    backGImg = pygame.transform.scale(backGroundImg, [500, 800])
    pygame.display.set_caption('원석 부수기')
    rect = pygame.Rect(250, 400, 50, 50)
    rect_img = pygame.image.load("../texture/player.png")
    rect_img = pygame.transform.scale(rect_img, (50, 50))
    stones = []
    stone_speed = 3
    stone_spawn_timer = 0
    stone_spawn_interval = 90
    stone_img = pygame.image.load("../texture/rock1.png")
    stone_img = pygame.transform.scale(stone_img, (50, 50))
    missile_img = pygame.image.load("../texture/mix.png")
    missile_img = pygame.transform.scale(missile_img, (10, 30))
    missile_sound = pygame.mixer.Sound("../texture/laser2.mp3")
    collision_img = pygame.image.load("../texture/bob.png")
    collision_img = pygame.transform.scale(collision_img, (50, 50))
    missiles = []
    score = 0
    font = pygame.font.Font("../font/BMDOHYEON_ttf.ttf", 30)
    pygame.mixer.music.load("../texture/backsound.mp3")
    pygame.mixer.music.play(-1)
    skill_available = False
    skill_count = 0
    skill_threshold = 10
    skill_img = pygame.image.load("../texture/skill.png")
    skill_img = pygame.transform.scale(skill_img, (100, 100))
    stones_to_remove = []
    missiles_to_remove = []
    def check_collision(object1, object2):
        nonlocal score, skill_count, skill_available, health, game_over, stones
        rect1 = object1["rect"]
        rect2 = object2["rect"]
        if rect1.colliderect(rect2):
            if rect1 == rect or rect2 == rect:
                health -= 1
                gameScr.blit(collision_img, stone["rect"])
                try:
                    if object1["image"] == stone_img:
                        stones.remove(object1)
                except:
                    pass
                try:
                    if object2["image"] == stone_img:
                        stones.remove(object2)
                except:
                    pass
            else:
                skill_count += 1
            if skill_count >= skill_threshold:
                skill_available = True
            if health <= 0:
                game_over = True
            return True
        return False
    def use_skill():
        nonlocal score, stones, skill_available, skill_count
        stones_to_remove = []
        for stone in stones:
            stone["stone_health"] = 0
            score += 1
            stones_to_remove.append(stone)
        for stone in stones_to_remove:
            stones.remove(stone)
        skill_available = False
        skill_count = 0

    health = 3
    heart_full_img = pygame.image.load("../texture/heart.png")
    heart_empty_img = pygame.image.load("../texture/heart2.png")
    # gameStart() 함수 내부의 하트 이미지 크기 조정
    heart_full_img = pygame.transform.scale(heart_full_img, (30, 30))
    heart_empty_img = pygame.transform.scale(heart_empty_img, (30, 30))

    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    missile_x = rect.x + rect.width / 2 - 5
                    missile_y = rect.y
                    missile_rect = pygame.Rect(missile_x, missile_y, 10, 30)
                    missile = {
                        "rect": missile_rect,
                        "image": missile_img
                    }
                    missiles.append(missile)
                    missile_sound.play()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f or event.unicode == "ㄹ":
                        if skill_available and skill_count >= skill_threshold:
                            use_skill()
                        elif not skill_available and skill_count >= skill_threshold:
                            skill_count -= skill_threshold  # 스킬 횟수 초기화
                            skill_available = False  # 스킬 사용 후 스킬 사용 가능 상태 해제

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and rect.y > 0:
                rect.y -= 5
            if keys[pygame.K_DOWN] and rect.y < 750:
                rect.y += 5
            if keys[pygame.K_LEFT] and rect.x > 0:
                rect.x -= 5
            if keys[pygame.K_RIGHT] and rect.x < 450:
                rect.x += 5

        gameScr.blit(backGImg, [0, 0])
        gameScr.blit(rect_img, rect)

        for missile in missiles:
            missile["rect"].y -= 5
            gameScr.blit(missile["image"], (missile["rect"].x, missile["rect"].y))

        stone_spawn_timer += 1
        if stone_spawn_timer >= stone_spawn_interval and not game_over:
            stone_width = random.randint(30, 50)
            stone_height = random.randint(30, 50)
            stone_x = random.randint(0, 500 - stone_width)
            stone_y = -stone_height
            stone_rect = pygame.Rect(stone_x, stone_y, stone_width, stone_height)
            stone = {
                "rect": stone_rect,
                "image": stone_img,
                "stone_health": 1
            }
            stones.append(stone)
            stone_spawn_timer = 0
            stone_spawn_interval -= 1
            if stone_spawn_interval < 40:
                stone_spawn_interval = 40
        for stone in stones:
            if check_collision(stone, {"rect":rect}):
                pass
            stone["rect"].y += stone_speed
            gameScr.blit(stone["image"], (stone["rect"].x, stone["rect"].y))

            if stone["rect"].y > 800 or stone["rect"].x > 500 or stone["rect"].x + stone["rect"].width < 0:
                stone["stone_health"] -= 1

            for missile in missiles:
                if check_collision(missile, stone):
                    gameScr.blit(collision_img, stone["rect"])
                    stone["stone_health"] -= 1
                    missiles_to_remove.append(missile)
                    stones_to_remove.append(stone)
                    score += 1

            for stone_remove in stones_to_remove:
                stones.remove(stone_remove)

            for missile_remove in missiles_to_remove:
                missiles.remove(missile_remove)

            stones_to_remove.clear()
            missiles_to_remove.clear()


        if health <= 0:
            game_over = True

        if game_over:
            game_over_text = font.render("gameover", True, [255, 0, 0])
            gameScr.blit(game_over_text, [200, 350])
            score_text = font.render("Score: " + str(score), True, [255, 0, 0])
            gameScr.blit(score_text, [210, 400])
        else:
            for i in range(health):
                gameScr.blit(heart_full_img, [10 + i * 40, 10])
            for i in range(health, 3):
                gameScr.blit(heart_empty_img, [10 + i * 40, 10])

        if skill_available:
            gameScr.blit(skill_img, [400, 650])
            skill_text = font.render("스킬: F 키 사용 가능", True, [255, 255, 255])
            gameScr.blit(skill_text, [10, 650])
        else:
            skill_text = font.render("스킬: " + str(skill_count) + " / " + str(skill_threshold), True, [255, 255, 255])
            gameScr.blit(skill_text, [10, 650])

        backText = font.render("BACK", True, [255, 255, 255])
        if back.collidepoint(pygame.mouse.get_pos()):
            backText = font.render("BACK", True, [255, 0, 0])
        gameScr.blit(backText, [10, 750])

        # gameStart() 함수 내부의 score_text 렌더링 부분 수정
        score_text = font.render("Score: " + str(score), True, [255, 255, 255])
        score_text_rect = score_text.get_rect()
        score_text_rect.center = (70, 60)  # x축 중앙, y축 아래로 이동
        gameScr.blit(score_text, score_text_rect)
        fps.tick(60)
        pygame.display.update()
    return

def gameinform():
    pygame.init()
    gameScr = pygame.display.set_mode([500, 800])
    backGroundImg = pygame.image.load("../texture/back_ground_Ui.gif")
    backGImg = pygame.transform.scale(backGroundImg, [500, 800])
    back = pygame.Rect(20, 50, 40, 50)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.collidepoint(event.pos):
                    return

        gameScr.blit(backGImg, [0, 0])

        # 돌아가기
        font = pygame.font.Font("../font/BMDOHYEON_ttf.ttf", 30)
        backText = font.render("BACK", True, [255, 255, 255])
        if back.collidepoint(pygame.mouse.get_pos()):
            backText = font.render("BACK", True, [255, 0, 0])
        gameScr.blit(backText, [back.x, back.y])

        movement_text = font.render("화살표를 눌러 위, 아래, 오른쪽을 눌러", True, [255, 255, 255])
        gameScr.blit(movement_text, [1, 200])

        movement_text = font.render("움직인다", True, [255, 255, 255])
        gameScr.blit(movement_text, [1, 260])

        movement_text = font.render("스페이스바로 미사일 발사!", True, [255, 255, 255])
        gameScr.blit(movement_text, [1, 360])

        movement_text = font.render("돌을 맞추어서 경험치를", True, [255, 255, 255])
        gameScr.blit(movement_text, [1, 440])

        movement_text = font.render("모으고", True, [255, 255, 255])
        gameScr.blit(movement_text, [1, 500])

        movement_text = font.render("f를 눌러 스킬을 사용해보자", True, [255, 255, 255])
        gameScr.blit(movement_text, [1, 560])

        movement_text = font.render("돌은 게속 빨라 진다고~~", True, [255, 255, 255])
        gameScr.blit(movement_text, [1, 620])

        movement_text = font.render("체력은 3개 밖에 없으니까", True, [255, 255, 255])
        gameScr.blit(movement_text, [1, 680])

        movement_text = font.render("잘 버텨서 점수를 높여봐", True, [255, 255, 255])
        gameScr.blit(movement_text, [1, 740])

        pygame.display.update()
    return


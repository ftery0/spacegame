"""유틸리티 함수 모음"""
import pygame
import os
import sys


def load_image(path, size=None):
    """
    이미지를 안전하게 로드

    Args:
        path: 이미지 파일 경로
        size: 리사이즈할 크기 (width, height) 튜플, None이면 원본 크기

    Returns:
        pygame.Surface: 로드된 이미지

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        pygame.error: 이미지 로드 실패 시
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {path}")

    try:
        image = pygame.image.load(path)
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        raise pygame.error(f"이미지 로드 실패 ({path}): {e}")


def load_sound(path):
    """
    사운드를 안전하게 로드

    Args:
        path: 사운드 파일 경로

    Returns:
        pygame.mixer.Sound: 로드된 사운드

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        pygame.error: 사운드 로드 실패 시
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"사운드 파일을 찾을 수 없습니다: {path}")

    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        raise pygame.error(f"사운드 로드 실패 ({path}): {e}")


def load_music(path):
    """
    배경음악을 안전하게 로드

    Args:
        path: 음악 파일 경로

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        pygame.error: 음악 로드 실패 시
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"음악 파일을 찾을 수 없습니다: {path}")

    try:
        pygame.mixer.music.load(path)
    except pygame.error as e:
        raise pygame.error(f"음악 로드 실패 ({path}): {e}")


def load_font(path, size):
    """
    폰트를 안전하게 로드

    Args:
        path: 폰트 파일 경로
        size: 폰트 크기

    Returns:
        pygame.font.Font: 로드된 폰트

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        pygame.error: 폰트 로드 실패 시
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"폰트 파일을 찾을 수 없습니다: {path}")

    try:
        return pygame.font.Font(path, size)
    except pygame.error as e:
        raise pygame.error(f"폰트 로드 실패 ({path}): {e}")


def create_button_rect(config):
    """
    설정 딕셔너리로부터 pygame.Rect 생성

    Args:
        config: {"x": int, "y": int, "width": int, "height": int} 형태의 딕셔너리

    Returns:
        pygame.Rect: 생성된 Rect 객체
    """
    return pygame.Rect(config["x"], config["y"], config["width"], config["height"])


def is_off_screen(rect, screen_width, screen_height):
    """
    객체가 화면 밖으로 나갔는지 확인

    Args:
        rect: pygame.Rect 객체
        screen_width: 화면 너비
        screen_height: 화면 높이

    Returns:
        bool: 화면 밖에 있으면 True
    """
    return (rect.y > screen_height or
            rect.x > screen_width or
            rect.x + rect.width < 0 or
            rect.y + rect.height < 0)


def safe_remove_from_list(item_list, items_to_remove):
    """
    리스트에서 안전하게 아이템 제거

    Args:
        item_list: 원본 리스트
        items_to_remove: 제거할 아이템 리스트
    """
    for item in items_to_remove:
        if item in item_list:
            item_list.remove(item)


def show_error_dialog(title, message):
    """
    에러 메시지 표시 (콘솔 및 선택적으로 GUI)

    Args:
        title: 에러 제목
        message: 에러 메시지
    """
    print(f"\n{'='*50}")
    print(f"ERROR: {title}")
    print(f"{'='*50}")
    print(message)
    print(f"{'='*50}\n")

    # 추가: tkinter를 사용한 GUI 에러 다이얼로그 (선택적)
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except:
        pass  # tkinter가 없거나 GUI 환경이 아니면 무시


def render_text_centered(font, text, color, y_pos, surface, screen_width):
    """
    텍스트를 화면 중앙에 렌더링하고 그리기

    Args:
        font: pygame.font.Font 객체
        text: 렌더링할 텍스트
        color: 텍스트 색상
        y_pos: Y 좌표
        surface: 그릴 표면 (pygame.Surface)
        screen_width: 화면 너비
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(screen_width // 2, y_pos))
    surface.blit(text_surface, text_rect)


def load_all_resources(resources_dict):
    """
    여러 리소스를 한 번에 로드

    Args:
        resources_dict: {"image_name": (path, size), "sound_name": path} 형태의 딕셔너리

    Returns:
        dict: 로드된 리소스 딕셔너리
    """
    loaded = {}
    for name, resource_info in resources_dict.items():
        try:
            if isinstance(resource_info, tuple):
                path, size = resource_info
                loaded[name] = load_image(path, size)
            else:
                # 사운드 또는 음악
                if resource_info.endswith('.mp3'):
                    loaded[name] = load_music(resource_info)
                else:
                    loaded[name] = load_sound(resource_info)
        except (FileNotFoundError, pygame.error) as e:
            print(f"Warning: {name} 로드 실패: {e}")
            loaded[name] = None

    return loaded

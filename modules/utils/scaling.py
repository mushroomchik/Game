"""Система масштабирования UI для разных разрешений экрана"""
import pygame

# Базовое разрешение (как в конфиге)
BASE_WIDTH = 1200
BASE_HEIGHT = 800

# Текущий масштаб (вычисляется при инициализации)
scale_x = 1.0
scale_y = 1.0
scale = 1.0

# Реальные размеры экрана
real_screen_width = BASE_WIDTH
real_screen_height = BASE_HEIGHT

# Смещение для центрирования
offset_x = 0
offset_y = 0

# Буфер для рендеринга (всегда базового размера)
render_surface = None

# Кэш масштабированного изображения
scaled_surface = None
last_scaled_size = (0, 0)


def init_scaling(screen_width: int, screen_height: int):
    """Инициализация масштабирования при запуске/смене режима экрана"""
    global scale_x, scale_y, scale, real_screen_width, real_screen_height, render_surface, offset_x, offset_y
    
    real_screen_width = screen_width
    real_screen_height = screen_height
    
    # Вычисляем масштаб по обеим осям
    scale_x = screen_width / BASE_WIDTH
    scale_y = screen_height / BASE_HEIGHT
    
    # Используем минимальный масштаб чтобы всё влезало (могут быть чёрные полосы)
    scale = min(scale_x, scale_y)
    
    # Смещение для центрирования
    scaled_w = int(BASE_WIDTH * scale)
    scaled_h = int(BASE_HEIGHT * scale)
    offset_x = (screen_width - scaled_w) // 2
    offset_y = (screen_height - scaled_h) // 2
    
    # Создаём surface для рендеринга (базового размера)
    render_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))


def get_render_surface() -> pygame.Surface:
    """Получить surface для рендеринга"""
    global render_surface
    if render_surface is None:
        render_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    return render_surface


def get_scale() -> float:
    """Получить текущий коэффициент масштабирования"""
    return scale


def scale_pos(x: int, y: int) -> tuple:
    """Масштабировать позицию (x, y)"""
    return int(x * scale), int(y * scale)


def scale_size(w: int, h: int = None) -> tuple:
    """Масштабировать размер (w, h)"""
    if h is None:
        h = w
    return int(w * scale), int(h * scale)


def scale_rect(x: int, y: int, w: int, h: int) -> pygame.Rect:
    """Масштабировать прямоугольник и вернуть pygame.Rect"""
    return pygame.Rect(int(x * scale), int(y * scale), int(w * scale), int(h * scale))


def get_scaled_font(font_key: str, fonts: dict) -> pygame.font.Font:
    """Получить масштабированный шрифт (увеличиваем размер если экран большой)"""
    if scale >= 1.5:
        # Для больших экранов немного увеличиваем шрифты
        size_mult = 1.2
    elif scale >= 1.2:
        size_mult = 1.1
    else:
        size_mult = 1.0
    
    base_sizes = {'large': 52, 'medium': 36, 'small': 22, 'tiny': 16}
    base_size = base_sizes.get(font_key, 16)
    new_size = int(base_size * size_mult)
    
    # Создаём новый шрифт с увеличенным размером если нужно
    if size_mult > 1.0:
        try:
            font_names = ['arial.ttf', 'dejavusans.ttf', 'freesansbold.ttf', 'verdana.ttf', None]
            for font_name in font_names:
                try:
                    return pygame.font.Font(font_name, new_size)
                except:
                    continue
            return pygame.font.Font(None, new_size)
        except:
            return fonts.get(font_key, fonts.get('tiny'))
    
    return fonts.get(font_key)


def get_centered_pos(w: int, h: int = None) -> tuple:
    """Получить центрированную позицию для элемента указанного размера"""
    if h is None:
        h = w
    scaled_w, scaled_h = int(w * scale), int(h * scale)
    x = (real_screen_width - scaled_w) // 2
    y = (real_screen_height - scaled_h) // 2
    return x, y


def get_screen_center() -> tuple:
    """Получить центр экрана"""
    return real_screen_width // 2, real_screen_height // 2


def get_mouse_pos() -> tuple:
    """Получить координаты мыши в пространстве базового экрана (1200x800)"""
    import pygame
    mx, my = pygame.mouse.get_pos()
    bx = mx - offset_x
    by = my - offset_y
    bx = int(bx / scale)
    by = int(by / scale)
    bx = max(0, min(bx, BASE_WIDTH))
    by = max(0, min(by, BASE_HEIGHT))
    return bx, by


def blit_to_screen(screen: pygame.Surface, source: pygame.Surface):
    """Масштабировать и отрисовать source на экран"""
    global scaled_surface, last_scaled_size
    
    # Вычисляем целевой размер
    scaled_w = int(BASE_WIDTH * scale)
    scaled_h = int(BASE_HEIGHT * scale)
    target_size = (scaled_w, scaled_h)
    
    # Масштабируем ( pygame.transform.scale - аппаратно ускоренная операция)
    scaled_surface = pygame.transform.scale(source, target_size)
    
    # Рисуем с учетом смещения (центрируем)
    screen.blit(scaled_surface, (offset_x, offset_y))

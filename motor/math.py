import pygame as pg
from typing import Union, Tuple

def vector2_direction_to_vector2(
    v1: Union[pg.Vector2, Tuple[float, float]], 
    v2: Union[pg.Vector2, Tuple[float, float]], 
    normalized: bool = True
) -> pg.Vector2:
    v1 = pg.Vector2(v1) if isinstance(v1, tuple) else v1
    v2 = pg.Vector2(v2) if isinstance(v2, tuple) else v2
    direction = v2 - v1
    if normalized and direction.length() > 0:
        return direction.normalize()
    return direction

def line_rect_collision(p1: pg.math.Vector2, p2: pg.math.Vector2, rect: pg.Rect) -> bool:
    """
    Verifica se a linha de p1 a p2 intersecta o retângulo rect.
    Baseado em interseção de segmento de linha com os lados do retângulo.
    """
    def line_intersects(a1: pg.math.Vector2, a2: pg.math.Vector2, b1: pg.math.Vector2, b2: pg.math.Vector2) -> bool:
        """Verifica se dois segmentos de linha (a1-a2 e b1-b2) se intersectam."""
        def ccw(A: pg.math.Vector2, B: pg.math.Vector2, C: pg.math.Vector2) -> bool:
            return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)
        
        return ccw(a1, b1, b2) != ccw(a2, b1, b2) and ccw(a1, a2, b1) != ccw(a1, a2, b2)

    # Cantos do retângulo
    rect_corners = [
        pg.math.Vector2(rect.left, rect.top),    # Topo-esquerda
        pg.math.Vector2(rect.right, rect.top),   # Topo-direita
        pg.math.Vector2(rect.right, rect.bottom),# Base-direita
        pg.math.Vector2(rect.left, rect.bottom)  # Base-esquerda
    ]

    # Verifica interseção da linha com cada lado do retângulo
    for i in range(4):
        if line_intersects(p1, p2, rect_corners[i], rect_corners[(i + 1) % 4]):
            return True
    
    # Verifica se a linha está completamente dentro do retângulo
    if (rect.collidepoint(p1.x, p1.y) and rect.collidepoint(p2.x, p2.y)):
        return True

    return False

def line_rect_collision_point(p1: pg.math.Vector2, p2: pg.math.Vector2, rect: pg.FRect) -> pg.math.Vector2 | None:
    """
    Retorna o ponto de colisão entre a linha (p1 a p2) e o retângulo, se houver.
    Caso não haja colisão, retorna None.
    """
    def line_intersection(a1: pg.math.Vector2, a2: pg.math.Vector2, b1: pg.math.Vector2, b2: pg.math.Vector2) -> pg.math.Vector2 | None:
        """Calcula o ponto de interseção entre dois segmentos de linha, se existir."""
        # Vetores direção
        d1 = a2 - a1
        d2 = b2 - b1
        
        # Verifica se as linhas são paralelas
        det = d1.x * d2.y - d1.y * d2.x
        if abs(det) < 1e-10:  # Linhas paralelas
            return None
        
        # Calcula os parâmetros t e u para a interseção
        s = b1 - a1
        t = (s.x * d2.y - s.y * d2.x) / det
        u = (s.x * d1.y - s.y * d1.x) / det
        
        # Verifica se a interseção está dentro dos segmentos
        if 0 <= t <= 1 and 0 <= u <= 1:
            # Ponto de interseção
            return a1 + d1 * t
        return None

    # Cantos do retângulo
    rect_corners = [
        pg.math.Vector2(rect.left, rect.top),    # Topo-esquerda
        pg.math.Vector2(rect.right, rect.top),   # Topo-direita
        pg.math.Vector2(rect.right, rect.bottom),# Base-direita
        pg.math.Vector2(rect.left, rect.bottom)  # Base-esquerda
    ]

    # Verifica interseção com cada lado do retângulo
    closest_point = None
    min_distance = float('inf')
    
    for i in range(4):
        intersection = line_intersection(p1, p2, rect_corners[i], rect_corners[(i + 1) % 4])
        if intersection:
            # Calcula a distância do ponto de interseção ao p1
            distance = (intersection - p1).length()
            if distance < min_distance:
                min_distance = distance
                closest_point = intersection
    
    # Se ambos os pontos estão dentro do retângulo, retorna p2 (fim da linha)
    if (rect.collidepoint(p1.x, p1.y) and rect.collidepoint(p2.x, p2.y)):
        return p2

    return closest_point
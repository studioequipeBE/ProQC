from operator import length_hint

from Point import Point


class ListePoint:
    """
    Gère la liste des points.
    """
    liste_pixel_image = None

    def __init__(self):
        """
        Initialise la liste.
        """
        self.liste_pixel_image = []

    def add_point(self, point: Point) -> None:
        """
        Ajoute un point.
        """
        self.liste_pixel_image.append(point)

    def size(self) -> int:
        """
        Taille de la liste.
        """
        return length_hint(self.liste_pixel_image)

    def get_liste(self) -> list[Point]:
        """
        La liste des points.
        """
        return self.liste_pixel_image

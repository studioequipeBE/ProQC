class Point:
    """
    Un point / pixel. Coordonnées (X, Y).
    """

    x = None
    y = None

    def __init__(self, x: int, y: int):
        """
        Initialise un point.
        """
        self.x = x
        self.y = y

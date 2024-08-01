import colorsys


class ColorIterator:
    """
    A class to iterate over colors
    """

    def __init__(self, start_hue: int = 0, saturation: float = 0.5, lightness: float = 0.5) -> None:
        """
        Initialize the color iterator
        :param start_hue: The starting hue
        :param saturation: The saturation
        :param lightness: The lightness
        """
        self.current_hue = start_hue
        self.saturation = saturation
        self.lightness = lightness

    def __iter__(self) -> 'ColorIterator':
        return self

    def __next__(self) -> str:
        """
        Get the next color
        :return: str: The color code in hex format
        """
        self.current_hue = (self.current_hue + 10) % 360
        r, g, b = colorsys.hls_to_rgb(self.current_hue / 360.0, self.lightness, self.saturation)
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

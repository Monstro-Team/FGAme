# -*-coding: utf8 -*-
from math import sqrt, acos


class Color(object):

    '''
    Objeto básico que representa uma cor.

    Examples
    --------

    Podemos iniciar uma cor pelos valores RGBA ou por seu nome (no caso das
    mais comuns)

    >>> w1 = Color(255, 255, 255)
    >>> w2 = Color('white')

    Os objetos do tipo Color são imutáveis e se comportam como uma tupla.

    >>> list(w1)
    [255, 255, 255, 255]
    >>> w1
    Color(255, 255, 255, 255)

    Além disto, o construtor reaproveita objetos, de modo que cores iguais
    preservam a identidade

    >>> w1 is w2
    True

    Podemos acessar a cor em várias representações diferentes utilizando os
    atributos adequados.

    >>> w1.rgb
    (255, 255, 255)

    >>> w1.f_rgb
    (1.0, 1.0, 1.0)

    >>> w1.u_rgb
    16777215

    '''

    __slots__ = ['_red', '_green', '_blue', '_alpha']
    _CACHE = {}
    _RANGE = (0, 1, 2, 3)

    def __new__(cls, *args):
        try:
            return cls._CACHE[args]
        except KeyError:
            color_cache = cls._CACHE
            if len(args) == 1:
                args = args[0]
            if len(args) == 3:
                try:
                    return color_cache[args]
                except KeyError:
                    color_cache[args] = new = Color(*(args + (255,)))
                    return new
            if len(args) == 4:
                try:
                    return color_cache[args]
                except KeyError:
                    color_cache[args] = new = object.__new__(cls)
                    new._red, new._green, new._blue, new._alpha = args
                    return new

            else:
                del cls._CACHE[args]

    # Componentes RGBa
    @property
    def red(self):
        return self._red

    @property
    def green(self):
        return self._green

    @property
    def blue(self):
        return self._blue

    @property
    def alpha(self):
        return self._alpha

    # Componentes HSI
    @property
    def hue(self):
        return NotImplemented

    @property
    def saturation(self):
        return NotImplemented

    @property
    def intensity(self):
        return NotImplemented

    # Representações em diferentes espaço de cores
    @property
    def rgba(self):
        return tuple(self)

    @property
    def rgb(self):
        return self[:3]

    @property
    def f_rgb(self):
        return tuple(x / 255. for x in self[:3])

    @property
    def f_rgba(self):
        return tuple(x / 255. for x in self)

    @property
    def u_rgba(self):
        c = self
        return (c[0] << 24) + (c[1] << 16) + (c[2] << 8) + c[3]

    @property
    def u_rgb(self):
        c = self
        return (c[0] << 16) + (c[1] << 8) + c[2]

    @property
    def hsi(self):
        return self.hsia[:-1]

    @property
    def hsia(self):
        # Conversão para (H)ue, (S)aturation, (I)ntensity
        # ref: https://en.wikipedia.org/wiki/RGB_color_model#Nonlinearity
        R, G, B, a = self

        I = (R + G + B) / 3
        S = 1 - min(R, G, B) / I

        # Valores normalizados
        r, g, b = R / 255, G / 255, B / 255
        h_numer = acos(((r - g) + (r - b)) / 2)
        h_denom = sqrt((r - b) ** 2 + (r - b) * (g - b))
        return h_numer / h_denom, S, I, a

    @property
    def f_hsia(self):
        return tuple(x / 255 for x in self.hsia)

    @property
    def f_hsi(self):
        return tuple(x / 255 for x in self.hsi)

    # Transformações simples de cores #########################################
    def set_red(self, value):
        '''Retorna cor com novo valor para a componente vermelha'''

        return Color(value, self._green, self._blue, self._alpha)

    def set_green(self, value):
        '''Retorna cor com novo valor para a componente verde'''

        return Color(self._red, value, self._blue, self._alpha)

    def set_blue(self, value):
        '''Retorna cor com novo valor para a componente azul'''

        return Color(self._red, self._green, value, self._alpha)

    def set_alpha(self, value):
        '''Retorna cor com novo valor para a componente alpha'''

        return Color(self._red, self._green, self._blue, value)

    # Métodos mágicos #########################################################
    def __repr__(self):
        return 'Color%s' % (tuple(self),)

    def __len__(self):
        return 4

    def __iter__(self):
        yield self._red
        yield self._green
        yield self._blue
        yield self._alpha

    def __getitem__(self, key):
        if isinstance(key, int):
            if key == 0:
                return self._red
            elif key == 1:
                return self._green
            elif key == 2:
                return self._blue
            elif key == 3:
                return self._alpha
            elif key < 0:
                key = len(self) - key
                if key < 0:
                    raise IndexError
                return self[key]
        else:
            return tuple(self[i] for i in self._RANGE[key])
        raise IndexError(key)

    def __hash__(self):
        return (self._red ^ self._green) ^ (self._blue ^ self._alpha)

Color._CACHE.update({
    # Tons de cinza
    ('white',): Color(255, 255, 255),
    ('black',): Color(0, 0, 0),

    # Cores básicas
    ('red',): Color(255, 0, 0),
    ('green',): Color(0, 255, 0),
    ('blue',): Color(0, 0, 255),
})


###############################################################################
#                          Funções e objetos úteis
###############################################################################

class color_property(property):

    '''
    Implementa uma propriedade que converte automaticamente os valores
    fornecidos em cores válidas.

    Aceita None como um valor possível
    '''

    def __init__(self, name, default=None):
        self.name = name
        self.default = (None if default is None else Color(default))
        attr = '_' + name

        def fget(self):
            return getattr(self, attr, default)

        def fset(self, value):
            if value is None:
                fdel(self)
            else:
                setattr(self, attr, Color(value))

        def fdel(self):
            if hasattr(self, attr):
                delattr(self, attr)

        super(color_property, self).__init__(fget, fset, fdel)


def rgb(color):
    '''Convert input in a tuple of (red, green, blue) colors'''

    try:
        return color.rgb
    except AttributeError:
        return Color(color or 'black').rgb


def rgba(color):
    '''Convert input in a tuple of (red, green, blue, alpha) components'''

    try:
        return color.rgba
    except AttributeError:
        return Color(color or 'black').rgba

if __name__ == '__main__':
    import doctest
    doctest.testmod()

# -*- coding: utf8 -*-
# TODO: manter este modelo de renderização?
#
# Estamos reimplementando o método paint() nos objetos por questões de
# eficiência. Talvez os objetos deste módulo virem obsoletos

import copy
from FGAme.draw import Color
from FGAme import mathutils as m
from FGAme.core import PyGameTextureManager


class Drawable(object):

    '''Classe mãe para todos os objetos que podem ser desenhados na tela'''

    __slots__ = []

    # Funções que modificam o objeto selecionado *inplace* ####################
    def irotate(self, theta, axis=None):
        '''Rotaciona o objeto pelo ângulo dado. É possível fornecer um eixo
        opcional para realizar a rotação. Caso contrário, realiza a rotação
        em torno do centro.'''

        raise NotImplementedError

    def move(self, delta):
        '''Desloca o objeto pelas coordenadas (delta_x, delta_y) fornecidas'''

        raise NotImplementedError

    def rescale(self, scale):
        '''Multiplica as dimensões do objeto por um fator de escala'''

        raise NotImplementedError

    def transform(self, M):
        '''Realiza uma transformação linear por uma matriz M'''

        raise NotImplementedError

    # Retorna versões transformadas dos objetos ###############################
    def copy(self):
        '''Retorna uma cópia do objeto'''

        return copy.copy(self)

    def rescaled(self, value):
        '''Retorna uma versão modificada por um fator de escala igual a
        `value`'''

        new = self.copy()
        new.scale(value)
        return new

    def rotate(self, theta, axis=None):
        '''Retorna uma cópia do objeto rotacionada pelo ângulo fornecido em
        torno do eixo fornecido (ou o centro do objeto)'''

        new = self.copy()
        new.irotate(theta, axis)
        return new

    def moved(self, delta):
        '''Retorna uma cópia do objeto deslocada por um fator
        (delta_x, delta_y)'''

        new = self.copy()
        new.move(delta)
        return new

    def transformed(self, M):
        '''Retorna uma cópia do objeto transformada por uma matriz M'''

        new = self.copy()
        new.transform(M)
        return new

    def update(self, dt):
        '''Update its state after elapsing a time dt'''

    @property
    def visualization(self):
        return self

###############################################################################
#                            Objetos primitivos
###############################################################################


def delegate_property(name):
    '''Propriedade que simplesmente extrai o valor do atributo .geometric'''
    @property
    def getter(self):
        return getattr(self.geometric, name)

    return getter


class Shape(Drawable):

    '''Classe pai para todos os objetos de geometria simples.'''

    __slots__ = ['geometric', 'color', 'line_color', 'line_width', 'sync']
    canvas_primitive = None

    def __init__(self, geometric,
                 color='black', line_color='black', line_width=0.0):

        self.geometric = geometric
        self.color = Color(color)
        self.line_color = Color(line_color)
        self.line_width = line_width

    @classmethod
    def from_primitive(cls, obj,
                       color='black', line_color='black', line_width=0.0):

        if isinstance(obj, m.AbstractCircle):
            obj_cls = Circle
        elif isinstance(obj, m.AbstractPoly):
            obj_cls = Poly
        elif isinstance(obj, m.AbstractAABB):
            obj_cls = AABB
        else:
            tname = type(obj).__name__
            raise ValueError('unsupported primitive: %s' % tname)

        new = Shape.__new__(obj_cls, obj, color, line_color, line_width)
        Shape.__init__(new, obj, color, line_color, line_width)
        return new

    def get_vertices(self, tol=2):
        '''Retorna uma lista de vértices que aproxima o objeto.

        Em caso de figuras poligonais, tol é ignorado e a lista de vértices
        corresponde aos vértices do objeto original. Em figuras não poligonais,
        tol corresponde a uma margem de tolerância (estimada) de quantos pixels
        as linhas do polígono podem se afastar do objeto original.'''

        raise NotImplementedError

    def __getattr__(self, attr):
        return getattr(self.geometric, attr)

    def draw(self, canvas):
        '''Desenha o objeto no objeto canvas fornecido'''

        getattr(canvas, 'draw_' + self.canvas_primitive)(self)


class Circle(Shape):

    '''Objetos da classe Circle representam círculos.'''

    __slots__ = []
    canvas_primitive = 'circle'

    def __init__(self, radius, pos=(0, 0), **kwds):

        super(Circle, self).__init__(m.Circle(radius, pos), **kwds)

    def draw(self, canvas):
        canvas.draw_circle(self)

    @property
    def radius(self):
        return self.geometric.radius

    @property
    def pos(self):
        return self.geometric.pos


class AABB(Shape):

    '''Objetos da classe RectangleAA representam retângulos alinhados aos eixos
    principais.

    É inicializado com uma tupla (x, y, dx, dy) onde (x,y) representam as
    coordenadas inferior-esquerda do retângulo e dx e dy as dimensões nos eixos
    X e Y respectivamente.

    Existem construtores alternativos: centered(), ..., etc.
    '''
    __slots__ = []
    canvas_primitive = 'aabb'

    xmin = delegate_property('xmin')
    xmax = delegate_property('xmax')
    ymin = delegate_property('ymin')
    ymax = delegate_property('ymax')
    bbox = delegate_property('bbox')
    rect = delegate_property('rect')
    shape = delegate_property('shape')
    pos = delegate_property('pos')
    pos = delegate_property('pos_sw')
    pos = delegate_property('pos_nw')
    pos = delegate_property('pos_se')
    pos = delegate_property('pos_ne')

    def __init__(self,
                 bbox=None, rect=None, shape=None, pos=None,
                 xmin=None, xmax=None, ymin=None, ymax=None, **kwds):

        obj = m.AABB(bbox=bbox, rect=rect, shape=shape, pos=pos,
                     xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
        super(AABB, self).__init__(obj, **kwds)

    def get_vertices(self, tol=1e-6):
        raise NotImplementedError

    def draw(self, canvas):
        canvas.draw_aabb(self)


class Poly(Shape):

    '''Objetos da classe Poly representam polígonos especificados por uma lista
    de vértices.'''

    __slots__ = []
    shape = delegate_property('vertices')
    canvas_primitive = 'poly'

    def __init__(self, vertices, **kwds):
        obj = m.Poly(vertices)
        super(Poly, self).__init__(obj, **kwds)

    def get_vertices(self, tol=1e-6):
        return self.geometric.vertices

    def draw(self, canvas):
        canvas.draw_poly(self)


class Rectangle(Poly):
    __slots__ = []

    def __init__(self, bbox=None, rect=None, shape=None, pos=None,
                 xmin=None, ymin=None, xmax=None, ymax=None, **kwds):

        obj = m.Rectangle(bbox=bbox, rect=rect, shape=shape, pos=pos,
                          xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
        super(Poly, self).__init__(**kwds)


class Image(AABB):
    manager = PyGameTextureManager()
    canvas_primitive = 'image'

    def __init__(self, name, pos=(0, 0)):
        self._data = self.manager.get_image(name)
        shape = self.manager.get_shape(self._data)
        super(Image, self).__init__(pos=pos, shape=shape)

    def draw(self, canvas):
        self.draw_image(self)

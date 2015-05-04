# -*- coding: utf8 -*-
class Circle(object):

    '''Representa um círculo com raio e centro dados.

    Exemplos
    --------

    >>> C = Circle(50, (50, 0))
    '''

    __slots__ = ['radius', 'pos']

    def __init__(self, radius, pos=(0, 0)):
        self.radius = radius
        self.pos = pos

    def __repr__(self):
        s_center = '%.1f, %.1f' % self.center
        return 'Circle(%.1f, (%s))' % (self.radius, s_center)

    #==========================================================================
    # Cálculo de distâncias
    #==========================================================================

    def distance_center(self, other):
        '''Retorna a distância entre centros de dois círculos.'''

    def distance_circle(self, other):
        '''Retorna a distância para um outro círculo. Zero se eles se
        interceptam'''

    #==========================================================================
    # Pontos de interceptação
    #==========================================================================

    def intersects_circle(self, other):
        '''Retorna True se o círculo intercepta outro círculo ou False, caso
        contrário'''

    def intersects_point(self, point, tol=1e-6):
        '''Retorna True se o ponto está na fronteira do círculo dada a margem
        de tolerância tol.'''

    #==========================================================================
    # Contêm ou não figuras
    #==========================================================================

    def contains_circle(self, other):
        '''Retorna True se o círculo intecepta outro círculo ou False, caso
        contrário'''

    def contains_point(self, point):
        '''Retorna True se o círculo intecepta outro círculo ou False, caso
        contrário'''

if __name__ == '__main__':
    import doctest
    doctest.testmod()

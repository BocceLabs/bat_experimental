import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Color
import math


def euclidean_distance(point1, point2):
    """
    Calculates the Euclidean distance between two points in two-dimensional space.
    The points should be given as tuples or lists of two numbers, representing the
    x and y coordinates of each point.
    """
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx*dx + dy*dy)


class CircleWidget(Widget):
    def on_touch_down(self, touch):
        with self.canvas:
            Color(1, 0, 0)  # set the color to red
            touch.ud['circle'] = Ellipse(pos=(touch.x, touch.y), size=(1, 1))
            touch.ud['center'] = (touch.x, touch.y)

    def on_touch_move(self, touch):
        circle = touch.ud['circle']
        center = touch.ud['center']
        radius = euclidean_distance((touch.x, touch.y), center)
        circle.pos = (center[0] - radius, center[1] - radius)
        circle.size = (radius*2, radius*2)


class CircleApp(App):
    def build(self):
        return CircleWidget()


if __name__ == '__main__':
    CircleApp().run()
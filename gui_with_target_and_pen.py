from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse
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

class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)

        # Create the left column of buttons
        left_col = BoxLayout(orientation='vertical')
        target_zone_button = Button(text='Target Zone',
                                    on_press=self.activate_target_zone_widget)
        pen_button = Button(text='Pen', on_press=self.activate_pen_widget)
        left_col.add_widget(target_zone_button)
        left_col.add_widget(pen_button)
        self.add_widget(left_col)

        # Create the top row of buttons
        top_row = BoxLayout(orientation='horizontal')
        red_button = Button(text='Red', on_press=self.set_color_red)
        blue_button = Button(text='Blue', on_press=self.set_color_blue)
        green_button = Button(text='Green', on_press=self.set_color_green)
        yellow_button = Button(text='Yellow', on_press=self.set_color_yellow)
        top_row.add_widget(red_button)
        top_row.add_widget(blue_button)
        top_row.add_widget(green_button)
        top_row.add_widget(yellow_button)
        self.add_widget(top_row)

        # create the canvas widget
        self.canvas_widget = Widget()
        self.add_widget(self.canvas_widget)

        # set the initial color to be red
        self.color = Color(1, 0, 0, 1)

        # set the initial active widget to be the circle widget
        self.active_widgets = []

        # set the initial active widget to be None
        self.active_widget = None
        self.active_widgets = []

    def set_color(self, r, g, b, a):
        self.color = (r, g, b, a)

    def set_color_red(self, instance):
        for widget in self.active_widgets:
            widget.color = [1, 0, 0, 1]

    def set_color_blue(self, instance):
        for widget in self.active_widgets:
            widget.color = [0, 0, 1, 1]

    def set_color_green(self, instance):
        for widget in self.active_widgets:
            widget.color = [0, 1, 0, 1]

    def set_color_yellow(self, instance):
        for widget in self.active_widgets:
            widget.color = [1, 1, 0, 1]

    def activate_target_zone_widget(self, instance):
        if isinstance(self.active_widget, TargetZone):
            # do nothing if the active widget is already a target zone
            return
        elif self.active_widget is not None and not isinstance(self.active_widget, TargetZone):
            # remove the active widget if it is not a pen
            self.canvas_widget.remove_widget(self.active_widget)
        target_zone = TargetZone(color=self.color)
        self.active_widget = target_zone
        self.active_widgets.append(target_zone)
        self.canvas_widget.add_widget(target_zone)

    def activate_pen_widget(self, instance):
        if isinstance(self.active_widget, Pen):
            # do nothing if the active widget is already a pen
            return
        elif self.active_widgets and not isinstance(self.active_widget, Pen):
            # remove the active widget if it is not a pen or target zone
            self.canvas_widget.remove_widget(self.active_widget)
        pen = Pen(color=self.color)
        self.active_widget = pen
        self.active_widgets.append(pen)
        self.canvas_widget.add_widget(pen)


class TargetZone(Widget):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self.color = [1, 1, 1, 1]
        self.bind(pos=self.update_circle, size=self.update_circle)

    def on_touch_down(self, touch):
        with self.canvas:
            Color(*self.color)
            touch.ud['circle'] = Ellipse(pos=(touch.x, touch.y), size=(1, 1))
            touch.ud['center'] = (touch.x, touch.y)

    def on_touch_move(self, touch):
        circle = touch.ud['circle']
        center = touch.ud['center']
        radius = euclidean_distance((touch.x, touch.y), center)
        circle.pos = (center[0] - radius, center[1] - radius)
        circle.size = (radius*2, radius*2)

    def update_circle(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size
        self.canvas.clear()
        with self.canvas:
            Color(*self.color)
            self.circle = Ellipse(pos=self.pos, size=self.size)

class Pen(Widget):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self.color = [1, 1, 1, 1]

    def on_touch_down(self, touch):
        with self.canvas:
            Color(*self.color)
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=2, color=self.color)

    def on_touch_move(self, touch):
        touch.ud['line'].points += [touch.x, touch.y]

    def on_touch_up(self, touch):
        pass

class MyApp(App):
    def build(self):
        return MainWidget()


if __name__ == '__main__':
    MyApp().run()

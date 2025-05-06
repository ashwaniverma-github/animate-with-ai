from manim import *
class TestAnimation(Scene):
    def construct(self):
        # Create a circle
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)

        # Create a square
        square = Square()
        square.set_fill(RED, opacity=0.5)

        # Create animations
        self.play(Create(circle))
        self.play(Transform(circle, square))
        self.play(square.animate.rotate(PI/2))
        self.play(FadeOut(square))

        # Add some text
        text = Text("Manim is working!")
        self.play(Write(text))
        self.wait()
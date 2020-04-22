from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class DepthValidator:

    def __init__(self, max_depth, ):
        if isinstance(max_depth, int):
            self.max_depth = max_depth
        else:
            self.max_depth = 3
        self.current = 0
        self.message = f"Depth cannot be more than {self.max_depth}."

    def __call__(self, value):
        self.current = 0
        if self.get_category_depth(value) <= self.max_depth:
            return True
        raise ValidationError(
            self.message.format(max_depth=self.max_depth))

    def get_category_depth(self, child):
        try:
            self.current += 1
            return self.get_category_depth(child.parent)
        except AttributeError:
            return self.current

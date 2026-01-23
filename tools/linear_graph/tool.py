from .script import linear_function

class Tool:
    name = "Linear Graph"

    def parameters(self):
        params = {
            "a": 1.0,
            "b": 0.0
        }
        return params
    
    def run(self, params: dict):
        a = params["a"]
        b = params["b"]
        x = list(range(-10, 11))
        y = linear_function(a, b, x)
        return x, y

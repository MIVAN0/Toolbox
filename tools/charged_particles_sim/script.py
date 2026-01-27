from math import sqrt

epsilon0 = 8.854187817e-12
pi = 3.14159265359
k = 1 / (4 * pi * epsilon0)
sqrt2 = 1.41421356237 

def electric_field_at_point(point, particles):
    x0, y0 = point
    Ex = Ey = 0
    for p in particles:
        dx = x0 - p["x"]
        dy = y0 - p["y"]
        if dx == dy == 0:
            continue

        r2 = dx*dx + dy*dy
        r = sqrt(r2)

        # formula: E = (1/(4πϵ0)) * q * r_vec / r^3
        Ex += k * p["q"] * dx / (r**3)
        Ey += k * p["q"] * dy / (r**3)
    return Ex, Ey

def compute_fields(particles):
    fields = []

    for i, p in enumerate(particles):
        point = (p["x"], p["y"])
        Ex, Ey = electric_field_at_point(point, particles)
        fields.append((Ex, Ey))

    return fields


def calculate_ablation_depth(sphere, cylinder, is_myopia):
    sphere_abs = abs(sphere)
    cylinder_abs = abs(cylinder)
    if is_myopia:
        return 15 * (sphere_abs + cylinder_abs)
    else:
        return 1 * (sphere_abs + cylinder_abs)

def calculate_delta_k1(sphere, is_myopia):
    sphere_abs = abs(sphere)
    if is_myopia:
        return sphere_abs * 0.8
    else:
        return sphere_abs * 1.2

def calculate_delta_k2(sphere, cylinder, is_myopia):
    sphere_abs = abs(sphere)
    cylinder_abs = abs(cylinder)
    if is_myopia:
        return (sphere_abs + cylinder_abs) * 0.8
    else:
        return (sphere_abs + cylinder_abs) * 1.2

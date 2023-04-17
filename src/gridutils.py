def space_npoints(min_value, max_value, n_points, v_type):
    """
    Creates equally distributred values between intervals
    :param min_value:
    :param max_value:
    :param n_points:
    :param v_type:
    :return:
    """
    if min_value > max_value:
        raise ValueError("min_value > max_value")
    if n_points < 2:
        return [min_value, max_value]
    step = float(max_value - min_value) / n_points

    if v_type == "I":
        step = round(step)

    out_array = [min_value]
    last = min_value
    for i in range(n_points - 2):
        last = last + step
        out_array.append(last)
    out_array.append(max_value)
    out_array = list(dict.fromkeys(out_array))
    out_array.sort()
    return out_array


def space_step(min_value, max_value, step):
    """
    Creates equally distributred values between intervals
    :param min_value:
    :param max_value:
    :param step:
    :return:
    """
    if min_value > max_value:
        raise ValueError("min_value > max_value")

    if step <= 0:
        raise ValueError("step <= 0")

    out_array = []
    last = min_value
    while last < max_value:
        out_array.append(last)
        last = last + step
    out_array.append(max_value)
    out_array = list(dict.fromkeys(out_array))
    out_array.sort()
    return out_array


def define_grid(variables):
    """
    Receives an array of structures (variables)
    each struct is {"name", "min", "max", "type"}.
    Returns arrays of allocated spaces for each variable
    :param variables: array of structures
    :return: array of arrays
    """
    grid_arrays = []
    for v in variables:
        if v["type"] == "S":
            s = space_step(v["min"], v["max"], v["step"])
            grid_arrays.append(s)
        if v["type"] == "E":
            grid_arrays.append(v["values"])
    return grid_arrays

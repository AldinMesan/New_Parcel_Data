polygon_vertices = [
    (-147.586062348169, 64.8346047435391),
    (-147.590994733664, 64.8346048004204),
    (-147.592545945626, 64.8346047876237),
    (-147.592565059763, 64.8346047793438),
    (-147.597328649644, 64.8346046376025),
    (-147.597391617667, 64.83460462493),
    (-147.601046845571, 64.8346044122413),
    (-147.601110943141, 64.8346043974916),
    (-147.607180295331, 64.8346038338846),
    (-147.607654074154, 64.8346037891643),
    (-147.607677872543, 64.8346037686571),
    (-147.611409605904, 64.8346014624936),
    (-147.611317324127, 64.8201668982246),
    (-147.596638555671, 64.8201698513501),
    (-147.596459509484, 64.8201696432909),
    (-147.585902966206, 64.8201681814723),
    (-147.585914709533, 64.8239367399961),
    (-147.585915127834, 64.8240017539122),
    (-147.585958655418, 64.8309926805803),
    (-147.586016481445, 64.8346047053345)
]

def find_polygon_corners(vertices):
    latitudes, longitudes = zip(*vertices)
    upper_left = (max(latitudes), min(longitudes))
    upper_right = (max(latitudes), max(longitudes))
    lower_left = (min(latitudes), min(longitudes))
    lower_right = (min(latitudes), max(longitudes))
    return upper_left, upper_right, lower_left, lower_right

upper_left, upper_right, lower_left, lower_right = find_polygon_corners(polygon_vertices)

print("Upper Left:", upper_left)
print("Upper Right:", upper_right)
print("Lower Left:", lower_left)
print("Lower Right:", lower_right)

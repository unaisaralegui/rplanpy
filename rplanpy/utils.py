ROOM_CLASS = {
    0: "Living room",
    1: "Master room",
    2: "Kitchen",
    3: "Bathroom",
    4: "Dining room",
    5: "Child room",
    6: "Study room",
    7: "Second room",
    8: "Guest room",
    9: "Balcony",
    10: "Entrance",
    11: "Storage",
    12: "Wall-in",
    13: "External area",
    14: "Exterior wall",
    15: "Front door",
    16: "Interior wall",
    17: "Interior door",
}

ROOM_TYPE = {
    0: 'PublicArea',
    1: 'Bedroom',
    2: 'FunctionArea',
    3: 'FunctionArea',
    4: 'FunctionArea',
    5: 'Bedroom',
    6: 'Bedroom',
    7: 'Bedroom',
    8: 'Bedroom',
    9: 'PublicArea',
    10: 'PublicArea',
    11: 'PublicArea',
    12: 'PublicArea',
    13: 'External',
    14: 'ExteriorWall',
    15: 'FrontDoor',
    16: 'InteriorWall',
    17: 'InteriorDoor',
}

ROOM_COLOR = {
    0: [244, 242, 229],
    1: [253, 244, 171],
    2: [234, 216, 214],
    3: [205, 233, 252],
    4: [244, 242, 229],
    5: [253, 244, 171],
    6: [253, 244, 171],
    7: [253, 244, 171],
    8: [253, 244, 171],
    9: [208, 216, 135],
    10: [244, 242, 229],
    11: [249, 222, 189],
    12: [128, 128, 128],
    13: [255, 255, 255],
    14: [79, 79, 79],
    15: [255, 225, 25],
    16: [128, 128, 128],
    17: [255, 225, 25],
}


def get_channel(image, n):
    return image[..., n]


def collide2d(bbox1, bbox2, th=0):
    """
    Do two boxes collide with each other?
    :param bbox1: indexes of box 1 (y0, x0, y1, x1)
    :param bbox2: indexes of box 2 (y0, x0, y1, x1)
    :param th: optional margin to add to the boxes (default 0)
    :return: True/False depending if boxes do collide
    :rtype: bool
    """
    return not(
        (bbox1[0]-th > bbox2[2]) or
        (bbox1[2]+th < bbox2[0]) or
        (bbox1[1]-th > bbox2[3]) or
        (bbox1[3]+th < bbox2[1])
    )


def point_box_relation(u, vbox):
    """
    Check in which point is located related to a box
    :param u: point to check (y, x)
    :param vbox: box to check point with (y0, x0, y1, x1)
    :return: code with the location of the point
     0   3   8
        ---
     2 | 4 | 7
       ---
     1   6   9
    """
    uy, ux = u
    vy0, vx0, vy1, vx1 = vbox
    if (ux < vx0 and uy <= vy0) or (ux == vx0 and uy == vy0):
        relation = 0  # 'left-above'
    elif vx0 <= ux < vx1 and uy <= vy0:
        relation = 3  # 'above'
    elif (vx1 <= ux and uy < vy0) or (ux == vx1 and uy == vy0):
        relation = 8  # 'right-above'
    elif vx1 <= ux and vy0 <= uy < vy1:
        relation = 7  # 'right-of'
    elif (vx1 < ux and vy1 <= uy) or (ux == vx1 and uy == vy1):
        relation = 9  # 'right-below'
    elif vx0 < ux <= vx1 and vy1 <= uy:
        relation = 6  # 'below'
    elif (ux <= vx0 and vy1 < uy) or (ux == vx0 and uy == vy1):
        relation = 1  # 'left-below'
    elif ux <= vx0 and vy0 < uy <= vy1:
        relation = 2  # 'left-of'
    elif vx0 < ux < vx1 and vy0 < uy < vy1:
        relation = 4  # 'inside'
    else:
        relation = None
    return relation


def door_room_relation(door_box, room_box):
    y0, x0, y1, x1 = room_box[:4]
    yc, xc = (y1 + y0) / 2, (x0 + x1) / 2
    y0b, x0b, y1b, x1b = door_box[:4]
    y, x = (y1b + y0b) / 2, (x0b + x1b) / 2

    if x == xc and y < yc:
        return 7
    elif x == xc and y > yc:
        return 1
    elif y == yc and x < xc:
        return 10
    elif y == yc and x > xc:
        return 4
    elif x0 < x < xc:
        if y < yc:
            return 8
        else:
            return 12
    elif xc < x < x1:
        if y < yc:
            return 6
        else:
            return 2
    elif y0 < y < yc:
        if x < xc:
            return 9
        else:
            return 5
    elif yc < y < y1:
        if x < xc:
            return 11
        else:
            return 3
    else:
        return 0

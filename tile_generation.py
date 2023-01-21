def get_line_x_from_index(self, index):
    central_line_x = self.perspective_point_x
    spacing = self.width * self.V_LINES_SPACING
    offset = index - 0.5
    line_x = central_line_x + offset * spacing + self.current_offset_x
    return line_x

def get_line_y_from_index(self, index):
    spacing_y = self.H_LINES_SPACING * self.height
    line_y = index * spacing_y - self.current_offset_y
    return line_y

def get_tile_coordinates(self, ti_x, ti_y):
    ti_y = ti_y - self.current_y_loop
    x = self.get_line_x_from_index(ti_x)
    y = self.get_line_y_from_index(ti_y)
    return x, y

def pre_fill_tile_coordinates(self):
    for i in range(0,10):
        self.tiles_coordinates.append((0,i))

import numpy as np

def generate_tiles_coordinates(self):
    last_x = 0
    last_y = 0

    for i in range(len(self.tiles_coordinates)-1, -1, -1):
        if self.tiles_coordinates[i][1] < self.current_y_loop:
            del self.tiles_coordinates[i]

    if len(self.tiles_coordinates) > 0:
        last_coordinates = self.tiles_coordinates[-1]
        last_x = last_coordinates[0]
        last_y = last_coordinates[1] + 1        

    for i in range(len(self.tiles_coordinates), self.NB_TILES):
        r = np.random.randint(0, 3)

        start_index = -int(self.V_NB_LINES/2)+1
        end_index = start_index + self.V_NB_LINES-1

        if last_x <= start_index:
            r = 1
        if last_x >= end_index - 1:
            r = 2

        self.tiles_coordinates.append((last_x, last_y))

        if r == 1:
            last_x += 1
            self.tiles_coordinates.append((last_x, last_y))
            last_y += 1
            self.tiles_coordinates.append((last_x, last_y))

        if r == 2:
            last_x -= 1
            self.tiles_coordinates.append((last_x, last_y))
            last_y += 1
            self.tiles_coordinates.append((last_x, last_y))

        last_y += 1

def update_tiles(self):
    for i in range(0, self.NB_TILES):
        tile = self.tiles[i]
        tiles_coordinates = self.tiles_coordinates[i]
        xmin, ymin = self.get_tile_coordinates(tiles_coordinates[0], tiles_coordinates[1])
        xmax, ymax = self.get_tile_coordinates(tiles_coordinates[0]+1, tiles_coordinates[1]+1)

        x1, y1 = self.transform(xmin, ymin)
        x2, y2 = self.transform(xmin, ymax)
        x3, y3 = self.transform(xmax, ymax)
        x4, y4 = self.transform(xmax, ymin)

        tile.points = [x1,y1,x2,y2,x3,y3,x4,y4]
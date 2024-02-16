def dms_str_to_float(value):
        degree_split = value.split('°')
        degrees = degree_split[0]
        ms = degree_split[1]
        s_split = ms.split("\'")[1]
        minutes = ms.split("\'")[0]
        seconds = s_split.split('\"')[0]
        degrees = float(degrees)
        minutes = float(minutes)
        seconds = float(seconds)
        output_value = degrees + minutes / 60 + seconds / 3600
        return output_value

def in_to_degrees_long(inch_value):
    return (inch_value / 12) / 288200

def in_to_degrees_latt(inch_value):
    return (inch_value / 12) / 364000

class BoundingBox:
    def __init__(self, top_lat, left_long, bottom_lat, right_long):
        self.top_corner = (dms_str_to_float(top_lat), dms_str_to_float(left_long))
        self.bottom_corner = (dms_str_to_float(bottom_lat), dms_str_to_float(right_long))

    def get_top_l_corner(self):
        return self.top_corner
    
    def get_bottom_r_corner(self):
        return self.bottom_corner
    
    def quantize_to_grid(self, min_row_height, min_col_width):
        min_row_height = in_to_degrees_latt(min_row_height)
        min_col_width = in_to_degrees_long(min_col_width)
        box_delta_y = self.top_corner[0] - self.bottom_corner[0]
        box_delta_x = self.top_corner[1] - self.bottom_corner[1]
        num_rows = int(box_delta_y / min_row_height)
        num_cols = int(box_delta_x / min_col_width)
        
        grid = []
        for i in range(0, num_rows):
            grid.append([])
            for j in range(0, num_cols):
                grid[i].append(0)
        return grid
    
CURRENT_GPS_POSITION_X = '33°46\'44.6"N'
CURRENT_GPS_POSITION_Y = '84°24\'20.5"W'

def get_current_gps_position():
    return (dms_str_to_float(CURRENT_GPS_POSITION_X), dms_str_to_float(CURRENT_GPS_POSITION_Y))
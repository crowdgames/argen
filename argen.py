import datetime, random
from PIL import Image, ImageChops, ImageDraw

# generation parameters
GRID_SZ =      22 # size of grid
PX_RES =       24 # size of each grid cell, in pixels
PCT_ON =       30 # percent of cells on (0 - 100)
PADDING =       2 # empty padding around edge
NGEN =         24 # number of tags to generate
NGEN_TUT =      6 # number of tutorial tags to generate
OPT_ITERS =   100 # iterations of optimizaton to make tags different

TILE_DIMENSION = 2.0 # in



# function to generate a tag grid
def gen_tag(istut):
    # create grid
    grid = [[0 for i1 in xrange(GRID_SZ)] for i2 in xrange(GRID_SZ)]

    # set grid cells randomly
    setting = []
    for ii in xrange(GRID_SZ * GRID_SZ):
        if ii <= float(PCT_ON) / 100 * GRID_SZ * GRID_SZ:
            setting.append(True)
        else:
            setting.append(False)
    random.shuffle(setting)

    for ii in xrange(GRID_SZ):
        for jj in xrange(GRID_SZ):
            if setting[ii + jj * GRID_SZ]:
                grid[ii][jj] = 1

    # draw an arrow in the corner
    for ii in xrange(8):
        for jj in xrange(8):
            grid[ii][jj] = 1 if (ii < 7 and jj < 7) else 0

    if istut:
        for ii in xrange(5):
            grid[ii + 1][1] = 0
            grid[6 / 2][ii + 1] = 0
    else:
        for ii in xrange(6):
            for jj in xrange(ii):
                grid[6 - ii][1 + jj] = 0

    # draw squares in other corners
    if True:
        for ii in xrange(4):
            for jj in xrange(4):
                grid[-1-ii][jj] = 0
                grid[ii][-1-jj] = 0
                grid[-1-ii][-1-jj] = 0

        for ii in xrange(3):
            for jj in xrange(3):
                grid[-1-ii][jj] = 1
                grid[ii][-1-jj] = 1
                grid[-1-ii][-1-jj] = 1

        for ii in xrange(1):
            for jj in xrange(1):
                grid[-1-ii -1][jj +1] = 0
                grid[ii +1][-1-jj -1] = 0
                grid[-1-ii -1][-1-jj -1] = 0

    return grid



# draw a cell on the grid
def put_cell(draw, x, y, clr):
    draw.rectangle((PX_RES * (x + PADDING), PX_RES * (y + PADDING), PX_RES * (x + 1 + PADDING) - 1, PX_RES * (y + 1 + PADDING) - 1), clr)

# turn a grid into an image
def grid2img(grid, filename):
    im_res = PX_RES * (GRID_SZ + 2 * PADDING)
    im = Image.new('L', (im_res, im_res), 0)
    draw = ImageDraw.Draw(im)

    for ii in xrange(GRID_SZ):
        for jj in xrange(GRID_SZ):
            put_cell(draw, ii, jj, grid[ii][jj] * 255)

    im.save(filename)



# turn a grid into an svg
def grids2svg(grids, filename):
    svg_padding = PADDING + 2

    COLS = 3
    ROWS = len(grids) / COLS
    if len(grids) % COLS != 0:
        ROWS += 1

    TILE_SPACING = 2 * PX_RES

    tile_res = PX_RES * (GRID_SZ + 2 * svg_padding)

    PPI = tile_res / TILE_DIMENSION

    im_w = COLS * tile_res + (COLS - 1) * TILE_SPACING
    im_h = ROWS * tile_res + (ROWS - 1) * TILE_SPACING

    with open(filename, 'w') as outfile:
        outfile.write('<svg width="%0.2fin" height="%0.2fin" version="1.1" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">\n' % (im_w / PPI, im_h / PPI, im_w, im_h))

        for number, grid in enumerate(grids):
            x_off = (number % COLS) * (TILE_SPACING + tile_res)
            y_off = (number / COLS) * (TILE_SPACING + tile_res)

            outfile.write('<rect fill="none" stroke="black" stroke-width="0.001in" x="%d" y="%d" width="%d" height="%d" rx="%d" ry="%d"/>\n' % (x_off, y_off, tile_res, tile_res, PX_RES, PX_RES))

            for x in xrange(GRID_SZ):
                for y in xrange(GRID_SZ):
                    if grid[x][y]:
                        outfile.write('<rect fill="black" stroke="none" x="%d" y="%d" width="%d" height="%d"/>\n' % (x_off + PX_RES * (x + svg_padding), y_off + PX_RES * (y + svg_padding), PX_RES, PX_RES))

            DIGITS = 6
            binary = ('%%%ds' % DIGITS) % ('{0:b}'.format(number + 1))
            for ii in xrange(DIGITS):
                x = x_off + int(tile_res / 2.0 - PX_RES * DIGITS / 2.0 + PX_RES * (ii + 0.5))
                y = y_off + int(tile_res - 2.0 * PX_RES)
                w = (PX_RES / 2)
                h = (PX_RES / 2)
                if binary[ii] == '1':
                    outfile.write('<path fill="none" stroke="black" stroke-width="0.01in" d="M %d %d v %d"/>\n' % (x, y, h))
                else:
                    outfile.write('<rect fill="none" stroke="black" stroke-width="0.01in" x="%d" y="%d" width="%d" height="%d" rx="%d" ry="%d" />\n' % (x - w / 2, y, w, h, w/4, w/4))

        outfile.write('</svg>\n')



# set random seed
random.seed(15487469)


def tut_tag(number):
    return number >= NGEN

# generate initial tags
tags = []
for ii in xrange(NGEN + NGEN_TUT):
    tags.append(gen_tag(tut_tag(ii)))



# function to calculate the objective function for a list of tags
def calc_obj(obj_tags):
    obj = GRID_SZ * GRID_SZ
    for aa, tag_aa in enumerate(obj_tags):
        for bb, tag_bb in enumerate(obj_tags[aa + 1:]):
            othis = 0
            for ii in xrange(GRID_SZ):
                for jj in xrange(GRID_SZ):
                    if tag_aa[ii][jj] >= tag_bb[ii][jj]:
                        othis += 1
            obj += othis
    return obj

# try optimizing for given number of iters
for oo in xrange(OPT_ITERS):
    # calc initial objective value
    obj = calc_obj(tags)
    print oo + 1, obj

    # go through each tag
    for ii in xrange(len(tags)):
        # make a new list of tags with that tag updated
        new_tags = list(tags)
        new_tags[ii] = gen_tag(tut_tag(ii))

        # check the new objective value
        new_obj = calc_obj(new_tags)

        # use the new tags if better
        if new_obj > obj:
            tags = new_tags



# save out the tags
filename = 'tile-%s' % (datetime.date.today().strftime('%Y%m%d'))
grids2svg(tags, filename + '.svg')
for number, tag in enumerate(tags):
    ty = 'T' if tut_tag(number) else 'D'
    grid2img(tag, filename + ('-%s%03d.png' % (ty, number + 1)))

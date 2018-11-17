import random
from PIL import Image, ImageChops, ImageDraw

# generation parameters
GRID_SZ =      21 # size of grid
PX_RES =       20 # size of each grid cell, in pixels
PCT_ON =       40 # percent of cells on (0 - 100)
PADDING =       4 # empty padding around edge
NGEN =         24 # number of tags to generate
OPT_ITERS =     5 # iterations of optimizaton to make tags different



# draw a cell on the grid
def put_cell(draw, x, y, clr):
    draw.rectangle((PX_RES * (x + PADDING), PX_RES * (y + PADDING), PX_RES * (x + 1 + PADDING) - 1, PX_RES * (y + 1 + PADDING) - 1), clr)
    
# function to generate a tag image
def gen_tag():
    # create an image big enough for the grid and border
    im_res = PX_RES * (GRID_SZ + 2 * PADDING)
    im = Image.new('L', (im_res, im_res), 0)
    draw = ImageDraw.Draw(im)

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
                put_cell(draw, ii, jj, 255)

    # draw a frame
    if False:
        for ii in xrange(GRID_SZ):
            put_cell(draw, ii, 0, 255)
            put_cell(draw, 0, ii, 255)
            put_cell(draw, ii, GRID_SZ - 1, ((ii + 1) % 2) * 255)
            put_cell(draw, GRID_SZ - 1, ii, ((ii + 1) % 2) * 255)
        
    # draw a box in the corner
    if True:
        for ii in xrange(7):
            for jj in xrange(7):
                put_cell(draw, ii, jj, 255)

        for ii in xrange(3):
            for jj in xrange(3):
                put_cell(draw, ii + 2, jj + 2, 0)

    return im



# set random seed
random.seed(15487469)

# generate initial tags
tags = []
for ii in xrange(NGEN):
    tags.append(gen_tag())



# function to calculate the objective function for a list of tags
def calc_obj(obj_tags):
    obj = 0
    for ii, tag_ii in enumerate(obj_tags):
        for jj, tag_jj in enumerate(obj_tags[ii + 0:]):
            obj += ImageChops.difference(tag_ii, tag_jj).histogram()[-1]
    return obj

# try optimizing for given number of iters
for oo in xrange(OPT_ITERS):
    # calc initial objective value
    obj = calc_obj(tags)
    print obj

    # go through each tag
    for ii in xrange(len(tags)):
        # make a new list of tags with that tag updated
        new_tags = list(tags)
        new_tags[ii] = gen_tag()

        # check the new objective value
        new_obj = calc_obj(new_tags)

        # use the new tags if better
        if new_obj > obj:
            tags = new_tags



# save out the tags
for ii, tag in enumerate(tags):
    tag.save('tag-%03d.png' % ii)

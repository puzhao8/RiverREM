

from riverrem.REMMaker import REMMaker

test_dem = './input/COP30_Colombia_small.tif'

if __name__ == "__main__":
    rem_maker = REMMaker(dem=test_dem)
    # rem_maker.make_rem()
    rem_maker.make_rem_viz(cmap='Blues', z=1)

# source: https://gdal.org/drivers/raster/vrt.html#just-in-time-compilation
# Trick for compatibility with and without numba
try:
    from numba import jit
    print('Using numba')
    g_max_iterations = 100
except:
    class jit(object):
        def __init__(self, nopython = True, nogil = True):
            pass

        def __call__(self, f):
            return f

    print('Using non-JIT version')
    g_max_iterations = 25


# Use a wrapper for the entry point regarding GDAL, since GDAL cannot access
# the jit decorated function with the expected signature.
def mandelbrot(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize, raster_ysize, r, gt, **kwargs):
    mandelbrot_jit(out_ar, xoff, yoff, xsize, ysize, raster_xsize, raster_ysize, g_max_iterations)


# Will make sure that the code is compiled to pure native code without Python
# fallback.
@jit(nopython=True, nogil=True, cache=True)
def mandelbrot_jit(out_ar, xoff, yoff, xsize, ysize, raster_xsize, raster_ysize, max_iterations):
    ovr_factor_y = float(out_ar.shape[0]) / ysize
    ovr_factor_x = float(out_ar.shape[1]) / xsize
    for j in range( out_ar.shape[0]):
        y0 = 2.0 * (yoff + j / ovr_factor_y) / raster_ysize - 1
        for i in range(out_ar.shape[1]):
            x0 = 3.5 * (xoff + i / ovr_factor_x) / raster_xsize - 2.5
            x = 0.0
            y = 0.0
            x2 = 0.0
            y2 = 0.0
            iteration = 0
            while x2 + y2 < 4 and iteration < max_iterations:
                y = 2*x*y + y0
                x = x2 - y2 + x0
                x2 = x * x
                y2 = y * y
                iteration += 1
            out_ar[j][i] = iteration * 255 / max_iterations


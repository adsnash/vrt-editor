# source: https://gdal.org/drivers/raster/vrt.html#vrt-that-computes-hillshading-using-an-external-library
# Licence: X/MIT
# Copyright 2016, Even Rouault
import math


def hillshade_int(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize, raster_ysize, radius, gt, z, scale):
    ovr_scale_x = float(out_ar.shape[1] - 2 * radius) / xsize
    ovr_scale_y = float(out_ar.shape[0] - 2 * radius) / ysize
    ewres = gt[1] / ovr_scale_x
    nsres = gt[5] / ovr_scale_y
    inv_nsres = 1.0 / nsres
    inv_ewres = 1.0 / ewres

    az = 315
    alt = 45
    degreesToRadians = math.pi / 180

    sin_alt = math.sin(alt * degreesToRadians)
    azRadians = az * degreesToRadians
    z_scale_factor = z / (8 * scale)
    cos_alt_mul_z_scale_factor = math.cos(alt * degreesToRadians) * z_scale_factor
    cos_az_mul_cos_alt_mul_z_scale_factor_mul_254 = 254 * math.cos(azRadians) * cos_alt_mul_z_scale_factor
    sin_az_mul_cos_alt_mul_z_scale_factor_mul_254 = 254 * math.sin(azRadians) * cos_alt_mul_z_scale_factor
    square_z_scale_factor = z_scale_factor * z_scale_factor
    sin_alt_mul_254 = 254.0 * sin_alt

    for j in range(radius, out_ar.shape[0]-radius):
        win_line = in_ar[0][j-radius:j+radius+1, :]

        for i in range(radius, out_ar.shape[1]-radius):
            win = win_line[:, i-radius:i+radius+1].tolist()
            x = inv_ewres * ((win[0][0] + win[1][0] + win[1][0] + win[2][0]) -
                            (win[0][2] + win[1][2] + win[1][2] + win[2][2]))
            y = inv_nsres * ((win[2][0] + win[2][1] + win[2][1] + win[2][2]) -
                            (win[0][0] + win[0][1] + win[0][1] + win[0][2]))
            xx_plus_yy = x * x + y * y
            cang_mul_254 = (sin_alt_mul_254 -
                (y * cos_az_mul_cos_alt_mul_z_scale_factor_mul_254 -
                    x * sin_az_mul_cos_alt_mul_z_scale_factor_mul_254)) / \
                math.sqrt(1 + square_z_scale_factor * xx_plus_yy)
            if cang_mul_254 < 0:
                out_ar[j, i] = 1
            else:
                out_ar[j, i] = 1 + round(cang_mul_254)


def hillshade(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize, raster_ysize, radius, gt, **kwargs):
    z = float(kwargs['z_factor'])
    scale = float(kwargs['scale'])
    hillshade_int(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize, raster_ysize, radius, gt, z, scale)


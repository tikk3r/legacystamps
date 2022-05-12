#!/usr/bin/env python
''' Simple Python library to download postage stamps of the Legacy Survey'''
__version__ = 'v1.2.2'
__author__ = 'Frits Sweijen'
__license__ = 'GPLv3'


import os
import sys
import warnings

import tqdm
import requests

class FileDownloader(object):
    ''' From https://medium.com/better-programming/python-progress-bars-with-tqdm-by-example-ce98dbbc9697

    Copyright 2019 tiptapcode Authors. All Rights Reserved.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    '''
    def get_url_filename(self, url):
        """
        Discover file name from HTTP URL, If none is discovered derive name from http redirect HTTP content header Location
        :param url: Url link to file to download
        :type url: str
        :return: Base filename
        :rtype: str
        """
        try:
            filename = os.path.basename(url)
            basename, ext = os.path.splitext(filename)
            if ext:
                return filename
            header = requests.head(url, allow_redirects=False).headers
            return os.path.basename(header.get('Location')) if 'Location' in header else filename
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
            raise errh
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
            raise errc
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
            raise errt
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            raise err

    def download_file(self, url, filename=None, target_dir=None):
        """
        Stream downloads files via HTTP
        :param url: Url link to file to download
        :type url: str
        :param filename: filename overrides filename defined in Url param
        :type filename: str
        :param target_dir: target destination directory to download file to
        :type target_dir: str
        :return: Absolute path to target destination where file has been downloaded to
        :rtype: str
        """
        if target_dir and not os.path.isdir(target_dir):
            raise ValueError('Invalid target_dir={} specified'.format(target_dir))
        local_filename = self.get_url_filename(url) if not filename else filename

        req = requests.get(url, stream=True, verify=True)
        req.raise_for_status()
        file_size = int(req.headers['Content-Length'])
        chunk_size = 1024  # 1 MB
        num_bars = int(file_size / chunk_size)

        base_path = os.path.abspath(os.path.dirname(__file__))
        target_dest_dir = os.path.join(base_path, local_filename) if not target_dir else os.path.join(target_dir, local_filename)
        with open(target_dest_dir, 'wb') as fp:
            for chunk in tqdm.tqdm(req.iter_content(chunk_size=chunk_size), total=num_bars, unit='KB', leave=True, file=sys.stdout):
                fp.write(chunk)

        return target_dest_dir

def download(ra, dec, bands, size=0.01, mode='jpeg', layer='ls-dr9', pixscale=0.262, autoscale=False, ddir=''):
    """ Stream downloads files via HTTP

    :param ra: Right ascension to centre cutout on.
    :type ra: float
    :param dec: Declination to centre cutout on.
    :type dec: float
    :param size: Size of the cutout in degrees.
    :type size: float
    :param bands: Band(s) to download. Multiple bands can be given as a single string, e.g. grz.
    :type bands: str
    :param mode: What file type to download. Can be jpeg or fits.
    :type mode: str
    :param layer: Layer to download. Default is ls-dr9. See the Legacy Survey documentation for possible layers.
    :type layer: str
    :param pixscale: Pixel scale in arcsec to download. Set to 0.262 by default.
    :type pixscale: float
    :param autoscale: Automatically scale image size and pixel scale if cutout excees server capacity.
    :type autoscale: bool
    :param ddir: Directory to store downloaded files in.
    :type ddir: str
    :return: Filename of the downloaded file.
    :rtype: str
    """
    size_pix = int(size * 3600 / pixscale)
    dlpixscale = pixscale
    dlsize_pix = size_pix
    if (size_pix > 3000) and autoscale:
        # Jump to the next available pixel size by scaling from the (approximate) native pixel scale.
        new_pixscale = pixscale
        new_size_pix = int(size * 3600 / new_pixscale)
        while new_size_pix > 3000:
            new_pixscale += 0.262
            new_size_pix = int(size * 3600 / new_pixscale)
        warnings.warn('Image size of {:.2f} deg with pixel scale {:.3f} exceeds server limit of 3000 pixels! Automatically adjusting pixel scale to {:.3f} giving {:d} pixels.'.format(size, pixscale, new_pixscale, new_size_pix), Warning, stacklevel=2)
        dlpixscale = new_pixscale
        dlsize_pix = new_size_pix
    elif (size_pix > 3000):
        warnings.warn('Image size of {:.2f} deg with pixel scale {:.3f} exceeds server limit of 3000 pixels! Image will be truncated! Use --autoscale or pass autoscale=True to automatically switch pixel scales.'.format(size, pixscale), Warning, stacklevel=2)
    url = 'https://www.legacysurvey.org/viewer/{mode:s}-cutout/?ra={ra:f}&dec={dec:f}&layer={layer:s}&pixscale={pixscale:.3f}&bands={bands:s}&size={size_pix:d}'.format(mode=mode, ra=ra, dec=dec, layer=layer, bands=bands, pixscale=dlpixscale, size_pix=dlsize_pix)
    print('URL to obtain cutout: ' + url)
    if ddir:
        fname = ddir + '/legacystamps_{ra:f}_{dec:f}_{layer:s}.{mode:s}'.format(ra=ra, dec=dec, layer=layer, mode=mode)
    else:
        print('Download directory not specified, downloading to ' + os.getcwd() + ' instead.')
        fname = os.getcwd() + '/legacystamps_{ra:f}_{dec:f}_{layer:s}.{mode:s}'.format(ra=ra, dec=dec, layer=layer, mode=mode)
    dl = FileDownloader()
    dl.download_file(url, filename=fname)
    print('Cutout saved to {fname:s}.'.format(fname=fname))
    return fname

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Legacystamps {:s} by {:s}'.format(__version__, __author__))
    parser.add_argument('--ra', type=float, required=True, help='Right ascension of cutout centre in degrees.')
    parser.add_argument('--dec', type=float, required=True, help='Declination of cutout centre in degrees.')
    parser.add_argument('--bands', type=str, required=True, help='Bands to download. Allowed values are g, r and z. Multiple bands can be specified as a single string. In the case of a JPEG image a colour image will be generated. In the case of a FITS image a FITS cube will be downloaded.')
    parser.add_argument('--mode', type=str, required=False, default='jpeg', help='Image type to retrieve. Can be "jpeg", "fits" or "both" to retrieve either a JPEG image, FITS file or both. Default value is jpeg.')
    parser.add_argument('--size', type=float, required=False, default=0.01, help='Cutout size in degrees.')
    parser.add_argument('--layer', type=str, required=False, default='ls-dr9', help='Layer to make a cutout from. Default value is ls-dr9. Examples are ls-dr9, sdss or unwise-neo4. See Legacy documentation for all possibilies.')
    parser.add_argument('--autoscale', required=False, default=False, dest='autoscale', action='store_true', help='Automatically change the pixel size if the resulting image would exceed the server maximum of 3000x3000 pixels.')
    parser.add_argument('--download-dir', type=str, required=False, default='', dest='ddir', help='Directory to store downloaded files. If not given will download to $PWD.')
    args = parser.parse_args()
    download(args.ra, args.dec, args.bands, mode=args.mode, size=args.size, layer=args.layer, autoscale=args.autoscale, ddir=args.ddir)

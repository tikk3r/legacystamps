#!/usr/bin/env python
''' Simple Python library to download postage stamps of the Legacy Survey'''
__version__ = 'v1.0'
__author__ = 'Frits Sweijen'

import os
import sys

import tqdm
import requests


class FileDownloader(object):
    ''' From https://medium.com/better-programming/python-progress-bars-with-tqdm-by-example-ce98dbbc9697
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

        req = requests.get(url, stream=True)
        file_size = int(req.headers['Content-Length'])
        chunk_size = 1024  # 1 MB
        num_bars = int(file_size / chunk_size)

        base_path = os.path.abspath(os.path.dirname(__file__))
        target_dest_dir = os.path.join(base_path, local_filename) if not target_dir else os.path.join(target_dir, local_filename)
        with open(target_dest_dir, 'wb') as fp:
            for chunk in tqdm.tqdm(req.iter_content(chunk_size=chunk_size), total=num_bars, unit='KB', leave=True, file=sys.stdout):
                fp.write(chunk)

        return target_dest_dir

def download(ra, dec, bands, size=0.01, mode='jpeg', layer='dr8', pixscale=0.262, useavm=False):
    size_pix = int(size * 3600 / pixscale)
    url = f'https://www.legacysurvey.org/viewer/{mode:s}-cutout/?ra={ra:f}&dec={dec:f}&layer={layer:s}&pixscale=0.262&bands={bands:s}&size={size_pix:d}'
    fname = f'legacystamps_{ra:f}_{dec:f}_{layer:s}.{mode:s}'
    dl = FileDownloader()
    dl.download_file(url, filename=fname)
    print(f'Cutout saved to {fname:s}.')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Legacystamps {:s} by {:s}'.format(__version__, __author__))
    parser.add_argument('--ra', type=float, required=True, help='Right ascension of cutout centre in degrees.')
    parser.add_argument('--dec', type=float, required=True, help='Declination of cutout centre in degrees.')
    parser.add_argument('--bands', type=str, required=True, help='Bands to download. Allowed values are g, r and z. Multiple bands can be specified as a single string. In the case of a JPEG image a colour image will be generated. In the case of a FITS image a FITS cube will be downloaded.')
    parser.add_argument('--mode', type=str, required=False, default='jpeg', help='Image type to retrieve. Can be "jpeg", "fits" or "both" to retrieve either a JPEG image, FITS file or both. Default value is jpeg.')
    parser.add_argument('--size', type=float, required=False, default=0.01, help='Cutout size in degrees.')
    args = parser.parse_args()
    download(args.ra, args.dec, args.bands, mode=args.mode, size=args.size)

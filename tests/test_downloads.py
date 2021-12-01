import legacystamps

def test_smallimg():
    print('Easy small cutout')
    legacystamps.download(ra=154.7709, dec=46.4537, bands='grz', mode='jpeg', size=0.01, layer='ls-dr9')

def test_bigimg_noauto():
    print('Cutout exceeding 3000 pixels WITHOUT autoscale')
    legacystamps.download(ra=154.7709, dec=46.4537, bands='grz', mode='jpeg', size=0.3, layer='ls-dr9')

def test_bigimg_auto():
    print('Cutout exceeding 3000 pixels WITH autoscale')
    legacystamps.download(ra=154.7709, dec=46.4537, bands='grz', mode='jpeg', size=0.3, layer='ls-dr9', autoscale=True)

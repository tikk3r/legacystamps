import legacystamps
print('Cutout exceeding 3000 pixels WITHOUT autoscale')
legacystamps.download(ra=154.7709, dec=46.4537, bands='grz', mode='jpeg', size=0.3, layer='ls-dr9')

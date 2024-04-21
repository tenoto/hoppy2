#!/usr/bin/env python

__version__ = '0.1'

import os
import argparse
from argparse import ArgumentParser
import xspec
import yaml
from astropy.io import fits

parser = argparse.ArgumentParser('fit_iron_lines.py',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description="""
	Fit the iron Fe Kalpha and Kbeta lines. 
	""")
version = '%(prog)s ' + __version__
parser.add_argument('--version', '-v', action='version', 
	version=version, help='show version of this command')
parser.add_argument('--inputpha', '-i', type=str, 
	help='input pha file.')	
parser.add_argument('--rmf', '-r', type=str, 
	help='input rmf file.')	
parser.add_argument('--arf', '-a', type=str, 
	help='input arf file.')	
parser.add_argument('--param', '-p', type=str, 
	help='input parameter file.')	
parser.add_argument('--outname', '-o', type=str, 
	help='output file basename.')	
args = parser.parse_args()

with open(args.param, 'r') as f:
    param = yaml.load(f, Loader=yaml.SafeLoader)

hdu = fits.open(args.inputpha) 
param['EXPOSURE'] = hdu[0].header['EXPOSURE']
param['TELESCOP'] = hdu[0].header['TELESCOP']
param['INSTRUME'] = hdu[0].header['INSTRUME']
param['OBS_ID'] = hdu[0].header['OBS_ID']
param['DATE-OBS'] = hdu[0].header['DATE-OBS']
param['DATE-END'] = hdu[0].header['DATE-END']
param['OBJECT'] = hdu[0].header['OBJECT']

# -------------------------
# Xspec read and setup
# -------------------------
flogfile = '%s_xspec.log' % args.outname
logfile = xspec.Xset.openLog(flogfile)
try:
    spec = xspec.Spectrum(args.inputpha)
except:
    print (f"Cannot read %s in XSPEC" % args.inputpha)
    raise Exception

spec.response = args.rmf
spec.response.arf = args.arf
spec.ignore("**-%.3f,%.3f-**" % (param['emin'],param['emax']))

model = xspec.Model(param['model'])
print(model)

# -------------------------
# Set parameters
# -------------------------
#ncomp = len(model.componentNames)
for icomp in model.componentNames:
	print (icomp,eval(f'model.{icomp}.parameterNames'))

model.pegpwrlw.PhoIndex = param['pegpwrlw']['PhoIndex']
model.pegpwrlw.eMin = param['pegpwrlw']['eMin']
model.pegpwrlw.eMax = param['pegpwrlw']['eMax']
#model.pegpwrlw.PhoIndex.frozen = True
model.pegpwrlw.norm = param['pegpwrlw']['norm']

model.gaussian.LineE = param['gaussian']['LineE']
model.gaussian.Sigma = param['gaussian']['Sigma']
model.gaussian.norm = param['gaussian']['norm']

model.gaussian_3.LineE = param['gaussian_3']['LineE']
model.gaussian_3.Sigma = param['gaussian_3']['Sigma']
model.gaussian_3.norm = param['gaussian_3']['norm']

model.show()
xspec.Fit.show()

# -------------------------
# Fitting 
# -------------------------
xspec.Fit.statMethod = param["statMethod"]
xspec.Xset.abund = param["abund"]

xspec.Fit.nIterations = 100
xspec.Fit.query = 'yes'
xspec.Fit.renorm()

xspec.Fit.perform()

param_num = 0
for icomp in model.componentNames:
	for ipar in eval(f'model.{icomp}.parameterNames'):
		param_num += 1
		if not eval(f'model.{icomp}.{ipar}.frozen'):
			print(ipar, eval(f'model.{icomp}.{ipar}.values[0]'))
			#print(param['error_level'],param_num)
			xspec.Fit.error("%.2f %d" % (param['error_level'],param_num))
			print(eval(f'model.{icomp}.{ipar}.error'))

			center = eval(f'model.{icomp}.{ipar}.values[0]')
			param[icomp][ipar] = center
			name = '%s_errl' % ipar 
			param[icomp][name] = eval(f'model.{icomp}.{ipar}.error[0]')	- center	
			name = '%s_erru' % ipar 
			param[icomp][name] = eval(f'model.{icomp}.{ipar}.error[1]')	- center				

model.show()
xspec.Fit.show()

param['statistic'] = xspec.Fit.statistic
param['dof'] = xspec.Fit.dof
param['rchi2'] = xspec.Fit.testStatistic/xspec.Fit.dof

out_yaml = '%s.yaml' % args.outname
with open(out_yaml, 'w') as outfile:
    yaml.dump(param, outfile, default_flow_style=False)

# -------------------------
# Plot 
# -------------------------
cmd = 'rm -f %s.ps' % args.outname
print(cmd);os.system(cmd)

title = '%s %s %s %.1fks' % (param['OBJECT'],param['OBS_ID'],param['DATE-OBS'],param['EXPOSURE']/1000.)

#xspec.Plot("?")
xspec.Plot.setRebin(minSig=param["minSig"],maxBins=param["maxBins"])
#xspec.Plot.device = '/null'
xspec.Plot.device = f'%s.ps/cps' % args.outname
xspec.Plot.xAxis = "keV"
xspec.Plot.add = True
xspec.Plot.xLog = False
xspec.Plot.yLog = False
xspec.Plot.addCommand("lab top \"%s\"" % title)
xspec.Plot.addCommand("csize 1.2")
xspec.Plot.addCommand("label pos y 2.2")
xspec.Plot.addCommand("lwidth 4")
xspec.Plot.addCommand("lwidth 4 on 1..100")
xspec.Plot.addCommand("time off")
xspec.Plot.addCommand("rescale y1 %.2f %.2f" % (param['y1_min'],param['y1_max']))
xspec.Plot.addCommand("rescale y2 %.2f %.2f" % (param['y2_min'],param['y2_max']))
xspec.Plot.addCommand("col 2 on 2")
xspec.Plot.addCommand("win 2")
xspec.Plot.addCommand("LAB 2 COL 2 LIN 0 100 JUS Lef POS 6.00000 0 \" \"")
xspec.Plot('data','del')


# -------------------------
# clear all
# -------------------------
xspec.Xset.closeLog()
spec = None
xspec.Plot.commands = ()
xspec.AllData.clear()



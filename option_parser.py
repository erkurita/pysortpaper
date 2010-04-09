#!/bin/python

from optparse import OptionParser

def CreateParser(usage = 'python %prog [OPTIONS] TARGET1 [TARGET2 TARGET3 ...]'):

	parser = OptionParser(usage=usage)

	parser.add_option('--res-sep',type='str',action='store',dest='res_separator',help='character used to separate the width and height of the resolution Defaults to \'x\'',default='x')
	parser.add_option('--res','--resolutions',type='str',action='store',dest='resolutions',help='resolutions to be extracted. The format is "WIDTHxHEIGHT:WIDTHxHEIGHT"   E.g.: "1920x1080:1920x1200:1440x900"   Requires option --dest to be used',default=None)
	parser.add_option('--dest',type='str',action='append',dest='destination',help='destination folder. Required if --res is set and must exist (for now)'
	# and there\'s only one (1) argument.  If more than one TARGET is passed as argument, and this option is not set, each argument will be its own destination Likewise, a list of destinations can be passed separated by : (colon) If the number of destinations is less than the number of targets, the rest will default to its own folder. There can be empty targets as well. \nFor example: "--dest=folder1::folder3"'
	,default=None)
	parser.add_option('-r',action='store_true',dest='top_level',help='process TARGET recursively',default=False)
	#parser.add_option('--ratio',type='str',action='store',dest='ratios',help='ratios to be processed',default='16:9,16:10,4:3')
	parser.add_option('-f',action='store_true',dest='folder_create',help='do not create a folder per resolution / ratio. Defaults to False',default=False)
	parser.add_option('--nd','--no-delete',action='store_true',dest='delete_f',help='do not delete folders or move files. Requires --dest  Defaults to False',default=False)
	parser.add_option('-s','--spider',action='store_true',dest='spider',help='crawls in TARGET and performs all operations except copy, delete and removal of files. Hit \'n run, basically. Defaults to False',default=False)
	parser.add_option('-q','--quiet',action='store_true',dest='quiet',help='prints as little as possible',default=False)
	parser.add_option('-t','--threshold',action='store',type='str',dest='threshold',help='Specifies how far the program deviates to considerate an image belongs to one ratio. Bear in mind that a high threshold (above 0.01) could lead to false positives, thus misplacing the images. Defaults to 0.0001',default='0.0001')
	parser.add_option('--no-overwrite',action='store_false',dest='overwrite',help='Do not overwrite files. Defaults to True (overwrites)',default=True)

	return parser


def ParseOptions(parser):
	if not isinstance(parser,OptionParser):
		raise TypeError('Wrong data type for ParseOptions(). Requested OptionParser, got ',type(parser))
	else:
		(options,args) = parser.parse_args()
		if len(args) < 1:
			raise ValueError('No arguments passed.')
		options = options.__dict__
		from os import path
		if options.get('resolutions') != None:
			if len(options.get('res_separator')) > 1:
				options['res_separator'] = 'x'
			if options.get('resolutions').count(options.get('res_separator')[0]) == 0:
				raise TypeError('Resolutions are not in a proper format')
			if isinstance(options.get('resolutions'),str):
				options['resolutions'] = str(options.get('resolutions')).split(':')
				try:
					while(1):
						options['resolutions'].remove('')
				except ValueError:
					pass
			try:
				options['threshold'] = float(options.get('threshold'))
			except ValueError:
				options['threshold'] = 0.0001
			if options.get('destination') and len(options.get('destination')) >= 1:
				options['destination'] = [options.get('destination')[0],]
			else:
				raise ValueError('No TARGET specified for the resolutions')
#		elif options.get('ratios') == None and options.get('resolutions') == None:

		if options.get('destination') and len(options.get('destination')) == 1:
			options['destination'] = [path.abspath(options.get('destination')[0]),]
		if len(args) > 1 and options.get('destination'):
			destinations = []
			for i in options.get('destination'):
				for j in i.split(':'):
					destinations.append(j)
			options['destination'] = destinations
		elif options.get('destination') == None:
			options['destination'] = [path.realpath(args[0]),]
		
		new_args = []
		for i in args:
			new_args.append(path.abspath(i))

		if len(new_args) != len(options.get('destination')):
			raise ValueError('Number of TARGETS is different to the number of DEST')
		return (options,new_args)


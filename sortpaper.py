#!/usr/bin/env python

#Usage: python new_sort_wp.py [OPTIONS] TARGET1 [TARGET2 TARGET3 ...]
#
#Options:
#  -h, --help            show this help message and exit
#  --res-sep=RES_SEPARATOR
#                        character used to separate the width and height of the
#                        resolution Defaults to 'x'
#  --res=RESOLUTIONS, --resolutions=RESOLUTIONS
#                        resolutions to be extracted. The format is
#                        "WIDTHxHEIGHT:WIDTHxHEIGHT"   E.g.:
#                        "1920x1080:1920x1200:1440x900"   Requires option
#                        --dest to be used
#  --dest=DESTINATION    destination folder. Defaults to TARGET if not
#                        specified and there's only one (1) argument.  If more
#                        than one TARGET is passed as argument, and this option
#                        is not set, each argument will be its own destination
#                        Likewise, a list of destinations can be passed
#                        separated by : (colon) If the number of destinations
#                        is less than the number of targets, the rest will
#                        default to its own folder There can be empty targets
#                        as well.  For example: "--dest=folder1::folder3"
#  --tld, --top-level    processes only the files in TARGET
#  --ratio=RATIOS        ratios to be processed
#  -f                    do not create a folder per resolution / ratio.
#                        Defaults to False
#  --nd, --no-delete     do not delete folders or move files. Requires --dest
#                        Defaults to False
#  -s, --spider          crawls on TARGET and performs all operations except
#                        copy, delete and removal of files. Hit 'n run,
#                        basically. Defaults to False
#  -q, --quiet           prints as little as possible
#  -t THRESHOLD, --threshold=THRESHOLD
#                        Specifies how far the program deviates to considerate
#                        an image belongs to one ratio. Bear in mind that a
#                        high threshold (above 0.01) could lead to false
#                        positives, thus misplacing the images. Defaults to
#                        0.0001

import os
from wp_class import *
from option_parser import *

def PrintMsg(msg):
	if not options.get('quiet'):
		print msg

def ProcessImage(images,tld):
	def MeetsCriteria(tld):
		result = None
		# We're checking either for resolutions
		try:
			if options.get('resolutions'):
				# We get the resolution of the current image.
				res = images.GetResolution(options.get('res_separator'))
				result = options['resolutions'][options.get('resolutions').index(res)]
			# Or for ratios
			else:
				result = ratios[images.ratio]
		except (ValueError,KeyError):
			result = None
		return result
	def MoveImage(destination):
		from os import path
		result = True
		dest = BuildDirTree(destination.get('dir_tree'),destination.get('dest')[0])
		prev_path = images.path
		if not options.get('spider'):
			result = images.Relocate(dest,copy = options.get('delete_f'),overwrite = options.get('overwrite'))
		if result:
			PrintMsg('Relocating '+prev_path+' to '+path.join(dest,images.filename))
	
	destination = None
	# We get the type of image according to our criteria
	result = MeetsCriteria(tld)
	# We only want to move to Non-Matching if we're not dealing with resolutions
	if not options.get('resolutions') or result:
		# We build a destination according to the results of the testing
		# This step is needed, because it gets us the directory tree,
		# along with the dictionary
		destination = images.GetDestination(result,tld)
		# If we so desire another destination, we change it accordingly
		if options.get('destination'):
			destination['dest'] = options.get('destination')
		# And finally move the image.
		MoveImage(destination)

def ProcessFolder(directorio,tld=None):
	if tld == None:
		raise ValueError('ProcessFolder(): Path provided is not accessible')
	if isinstance(directorio,Directory):
		files = directorio.GetDictionary('files')
		directories = directorio.GetDictionary('directories')

		PrintMsg('Processing directory '+directorio.path)
		if files != None:
			for images in directorio.GetDictionary('files').values():
				ProcessImage(images,tld)

		if directories != None:
			for dirs in directorio.GetDictionary('directories').values():
				ProcessFolder(dirs,tld)
				if dirs.IsEmpty():
					PrintMsg('Removing '+dirs.dir_name+' since it\'s empty')
					if not options.get('spider'):
						directorio.RemoveDir(dirs)
	else:
		raise TypeError('ProcessFolder(): Argument must be an instance of Directory')

################
# Main program #
################

## @defgroup main
#  @brief Main program entry
#
#  This is the main entry point of this script. We initialize here the variables we're going to
#  need, and execute the main loop @{
if __name__ == '__main__':

	## @brief usage variable, which will appear upon calling the program with no arguments
	#
	# @details This variable is passed to @c CreateParser() to indicate the usage when calling
	# @c OptionParser()
	usage = 'python %prog [OPTIONS] TARGET1 [TARGET2 TARGET3 ...]'

	## @brief a parser, to parse the operations and options to be done and used with the arguments
	#
	parser = CreateParser(usage)

	try:
		## the options and the arguments, parsed 
		#
		(options,args,ratios) = ParseOptions(parser)
		
		if ratios == None:
			ratios = STOCK_RATIOS
		if len(args) < 1:
			raise ValueError('No target directory passed')
	except ValueError,err:
		print 'main: '+err.message
		parser.print_help()
		exit(BAD_ARGUMENTS)
	except OSError,err:
		print err,work_dir
		exit(-1)
	
	## @brief count of invalid arguments
	#
	invalid_arguments = 0
	
	## @brief a @c list of directories to process
	#
	directories_to_process = []

	## @}
	#

	## After reading the arguments and options, we begin to process the number of directories which
	#  we'll work on
	for argument in args:
		# If the argument is valid, that is, a valid and existant directory
		#
		if os.path.isdir(argument):
			## We append a Directory object to the @var directory_to_process
			#
			directories_to_process.append(Directory(argument,options.get('top_level')))
		else:
			## But if it isn't, we increment the @var invalid_arguments by one
			#
			invalid_arguments += 1

	## Once all the arguments are processed, if all the arguments are invalid (that is, none are
	#  directories) there's nothing to do here, so we exit with a @c BAD_ARGUMENTS error
	if invalid_arguments == len(args):
		print 'The TARGET or TARGETS must be a path to a directory'
		exit(BAD_ARGUMENTS)

	## Now the true main program begins: we start to process each @a TARGET
	#

	for directorio in directories_to_process:
		try:
			## Using the @a path of the directory as the top level directory
			#
			ProcessFolder(directorio,tld=directorio.path)
		## It may happen that though the folder exists, the @a path is not accessible,
		#  thus we throw a @c ValueError exception and catch it here
		#
		except ValueError,err:
			print 'main: '+err
		## And finally, if the directory we just processed got emptied, 
		#
		if directorio.IsEmpty() and not options.get('delete_f'):
			PrintMsg('Removing'+directorio.dir_name+'since it\'s empty')
			if not options.get('spider'):
				## We remove it
				#
				os.rmdir(directorio.path)
	## @}
	#
	exit(0)


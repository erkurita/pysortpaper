## @var RECURSIVE
#  @brief Flag to indicate recursivity when loading the directory trees
#
#  @details Sometimes we want to process only the topmost level (that is, the path(s) passed as arguments)
#  when calling the program. So when we need the function Directory::GetDirectories() to only return the 
#  files (and not folders) inside the arguments, we pass @c False or @b not @c RECURSIVE to the function
#  as argument.
#
#  @note This is purely to keep track of the values used as boolean flags, to give them significance
#
RECURSIVE = False

## @var COPY_IMAGE
#  @brief Flag to indicate whether to copy the image instead of moving it.
#
#  @details When the option --no-delete is set, the images that matches the criteria for relocation will 
#  be copied to their destination instead of moved. This is useful when extracting a select group of 
#  images (such as a determined resolution or ratio).
#
#  @note This is purely to keep track of the values used as boolean flags, to give them significance
#
COPY_IMAGE = True

## @var OVERWRITE_FILES
#  @brief Flag to indicate whether to overwrite files
#
#  @details In the event you don't want the files to be overwritten, set the option --no-overwrite. 
#
#  @note This is purely to keep track of the values used as boolean flags, to give them significance
#
OVERWRITE_FILES = True

## @var STOCK_RATIOS
#  @brief Dictionary containing the ratios normally used
#
#  @details This dictionary groups the 3 mainly used aspect ratios in computers:
#  @li @c 16:9, @a "HDTV"
#  @li @c 16:10, I'll call this @a "Wide Screen"
#  @li @c 4:3, and I'll this @a "Normal Screen"
#  @details These 3 aspect ratios will be the stock ratios; if left alone, the script will only process the images
#  to match these 3 ratios. You can alter (add, delete) aspect ratios following this syntax:
#  @li @c key = the ratio in float
#  @li @c value = the name of the ratio, which will also be used as the folder name
#
STOCK_RATIOS = {float(16)/9 : 'HDTV',float(16)/10 : 'Wide Screen',float(4)/3 : 'Normal Screen', float(5)/4: 'Normal Screen',None : 'Non-matching'}

BAD_ARGUMENTS = 1

## @brief Builds a directory tree starting from a given @a directory and a @c list of directories
#
#  @details Since we want to keep the folder hierarchy when relocating files, we need to build the folder tree it was located at previously.
#  That is, we need to keep things in order while moving them. This procedure will build the tree part by part, until the desired path is built.\n
#  @b E.g. Suppose we pass @a "Wallpaper/sorted" as @a directory and @c ['Animals','Cats'] as @a dir_tree, which you can obtain from GetDirTree().
#  This function would build the path @a "Wallpaper/sorted/Animals/Cats"
#
#  @param dir_tree The directory tree, a @c list or @c tuple containing the names of the directories to be build, one inside the other
#  @param directory The directory to start the tree building.
#
#  @return Nothing
#
#  @exception TypeError if the @a dir_tree supplied is not a list or a tuple, we cannot process it properly.
#
#  @exception ValueError if the @a directory does not exists, or is not a directory, we can't build the directory tree.
#
def BuildDirTree(dir_tree,directory):
	import os
	directory = os.path.abspath(directory)
	if os.path.isdir(directory):
		if isinstance(dir_tree,(list,tuple)):
			path = directory
			for dirs in dir_tree:
				path = os.path.join(path,dirs)
				if not os.path.lexists(path):
					os.mkdir(path)	
			return path
		else:
			raise TypeError('BuildDirTree(): Argument dir_tree is not a tuple or list, got '+type(dir_tree).__name__)
	else:
		raise ValueError('BuildDirTree(): Argument directory passed is not an existing directory, got '+directory)


## @brief Determines the path hierarchy of a given @a path relative to a given directory
#  
#  @details This function is used to obtain the directories needed to get from a reference path to 
#  another path. Its main use is to keep the folder hierarchy when moving it from its current position
#  to another folder. \n @b E.g. we want to move a file from @a Wallpapers/unsorted/Animals/cats to @a Wallpapers/sorted/.
#  We pass @a "Wallpapers/unsorted/" as the top level directory (since it's being sorted now, right?)
#  and @a "Wallpapers/unsorted/Animals/cats" as the path. The return value would be a @c list containing @c "[Animals,cats]",
#  which could then be passed to BuildDirTree() to construct the destination, passing along the same top level directory.
#  
#  @param top_level_dir the directory to use as reference
#  @param path the path to determine the hierarchy relative to @a top_level_dir
#
#  @return the path tree needed to reach @a path from @a top_level_dir
#
#  @retval [] An empty @c list, returned only when @a path is the same as @a top_level_dir
#  @retval path As a list, if the given @a path is not inside @a top_level_dir
#  @retval dir_tree A list containing the directory tree needed to walk to reach @a path starting from @a top_level_dir
#
#  @exception TypeError This exception is raised when either @a path and @a top_level_dir are not a string, or 
#  @a top_level_dir is not an existing directory
#
def GetDirTree(top_level_dir,path):
	import os
	if isinstance(path,str) and isinstance(top_level_dir,str) and os.path.isdir(top_level_dir):
		dir_tree = []
		if (top_level_dir == path):
			return dir_tree
		path = os.path.normpath(path)
		top_level_dir = os.path.normpath(top_level_dir)
		while(path != top_level_dir and path != '/'):
			dir_tree.append(os.path.split(path)[1])
			path = os.path.split(path)[0]
		dir_tree.reverse()
		if dir_tree != []:
			if ('/'+reduce(os.path.join,dir_tree)) == path:
				dir_tree = []
		return dir_tree
	else:
		raise TypeError('GetDirTree(): Either passed top directory level is not a string (got '+type(top_level_dir).__name__+') or an existing directory, got '+top_level_dir)+'; or path is not a string (got '+type(path).__name__+')'

## @class ImageFile
#
#  @brief @c ImageFile is a rather-small class to handle image files
#
#  @details This class can handle every kind of image files, with a resolution equal or greater than 640x480
#  It's got information about the ratio, the resolution, its location on the filesystem and more things.
#  \n It derives from @c clsObject
class ImageFile(object):
	img = None
	path = ''
	dir_path = ''
	filename = ''
	size = ()
	resolution = ()
	ratio = float(0)
	destination = None
	separator = None

	## @brief the constructor of a @c ImageFile object
	#
	#  @details This is the constructor for an @c ImageFile object. It'll set most of the variables
	#  to be used, such as the ratio, the resolution, its path and directory.
	#
	#  @param path the path of the image to create an object for
	#
	#  @return a new instance of @c ImageFile
	#
	#  @retval None If @a path is not an image
	#  @retval ImageFile An instance of @c ImageFile, containing information about @a path
	#
	#  @exception ValueError if the image file is too small (less than 640x480), we can't consider it a wallpaper,
	#  so no @c ImageFile object for it.
	#
	def __new__(clsObject,path):
		import Image
		import os
		base = super(ImageFile,clsObject).__new__(clsObject)
		path_d = os.path.abspath(path)
		try:
			img = Image.open(path_d)
			if (img.size[0] < 640) or (img.size[1] < 480):
				raise ValueError('ImageFile.__init__():	Image '+os.path.split(path_d)[1]+' too small to be a wallpaper')
		except IOError:
			base = None
			return base
		base.path = path_d
		base.dir_path = os.path.split(path_d)[0]
		base.filename = os.path.split(path_d)[1]
		base.size = img.size
		base.resolution = map(str,img.size)
		try:
			base.ratio = float(img.size[0])/img.size[1]
		except ZeroDivisionError:
			base.ratio = 0
		img = None
		return base

	def GetResolution(self,separator='x'):
		return self.resolution[0]+separator+self.resolution[1]

	def SetSeparator(self,separator):
		if isinstance(separator,str):
			self.separator = separator[0]
		else:
			raise TypeError('SetSeparator(): Argument must be a string, got '+type(separator).__name__)

	def GetSeparator(self,data):
		if self.separator != None:
			if data.count(self.separator) > 0:
				return self.separator		
		if isinstance(data,str):
			separator = None
			try:
				for char in data:
					sep = int(char)
			except ValueError:
				separator = char
			return separator
		else:
			raise TypeError('GetSeparator(): Argument must be a string, got '+type(data).__name__)

	def SameResolution(self,resolution):
		if isinstance(resolution,str):
			separator = self.GetSeparator(resolution)
			if separator == None:
				raise ValueError
			else:
				return (resolution.split(separator) == self.resolution)
		elif isinstance(resolution,(list,tuple)):
			return (map(str,resolution) == self.resolution)
		else:
			raise TypeError('SameResolution(): Argument must be a tuple, list or string, got '+type(resolution).__name__)

	def CalcRatio(self,size):
		try:
			return float(size[0])/size[1]
		except ZeroDivisionError:
			return 0

	def SameRatio(self,ratio):
		if isinstance(ratio,str):
			separator = self.GetSeparator(ratio)
			if separator == None:
				raise ValueError('SameRatio(): Not a proper ratio (2 numbers separated by a non-numeric character), passed '+size)
			else:
				return (self.CalcRatio(map(float,ratio.split(separator))) == self.ratio)
		elif isinstance(ratio,(list,tuple)):
			if not map(lambda x: isinstance(x,(int,str)),ratio).count(False):
				return (self.CalcRatio(map(float,ratio)) == self.ratio)
		elif isinstance(ratio,float):
			return ratio == self.ratio
		else:
			raise TypeError('SameRatio(): Argument must be a tuple, list, float or string, got '+type(ratio).__name__)

	def Reopen(self):
		import Image
		try:
			self.img = Image.open(self.path)
		except IOError,err:
			print err.strerror

	import shutil
	def CopyMove(self,destination = None,function = shutil.move):
		import inspect
		if not inspect.isfunction(function):
			raise TypeError('CopyMove(): Argument function is not a function, got '+type(function).__name__)
		from os import path
		if self.destination != None:
			destination = self.destination
		try:
			function(self.path,destination)
		except IOError,err:
			raise AttributeError('CopyMove(): Error moving/copying '+self.path+': '+err.strerror)

	def Relocate(self,destination = None,copy = not COPY_IMAGE, overwrite = not OVERWRITE_FILES):
		import os
		import shutil
		if self.destination == None and destination == None:
			raise ValueError('Relocate(): No destination avaliable')
		if not isinstance(destination,str):
			raise TypeError('Relocate(): Destination must be a string, got '+type(destination).__name__)
		elif not os.path.exists(destination):
			raise ValueError('Relocate(): The destination \''+destination+'\' does not exist')
		elif not os.path.isdir(destination):
			raise ValueError(destination+' is not a directory')
		else:
			destination = os.path.abspath(destination)
			if not os.path.samefile(destination,self.dir_path):
				dest_file = os.path.join(destination,self.filename)
				self.destination = destination
				file_exists = os.path.lexists(dest_file)
				if file_exists and overwrite:
					os.remove(dest_file)
					file_exists = False
				if not file_exists:
					if copy:
						self.CopyMove(None,shutil.copy2)
					else:
						self.CopyMove(None,shutil.move)
					self.path = os.path.join(destination,self.filename)
					self.dir_path = destination
					return True
			else:
				return False

	def GetDestinationRatio(self,threshold):
		if not isinstance(threshold,float):
			raise TypeError('GetDestinationRatio(): argument is not a float, got '+type(threshold).__name__)
		dest_ratio = None
		if self.ratio in STOCK_RATIOS:
			dest_ratio = STOCK_RATIOS[self.ratio]
		else:
			try:
				for ratio in STOCK_RATIOS.keys():
					if (abs(ratio-self.ratio) < threshold):
						dest_ratio = STOCK_RATIOS[ratio]
						raise Exception
			except Exception,err:
				print err
		return dest_ratio

	# Pre-cond:	type_ratio tiene que bien estar contenida en las llaves de STOCK_RATIOS, valer None o
	#		ser una resolucion
	#		top_level_dir tiene que existir y ser un directorio
	#		ImageFile.dir_path tiene que contener a top_level_dir
	def GetDestination(self,type_ratio,top_level_dir):
		from os import path
		#We get the directory hierarchy of the image according to the TLD
		dir_tree = GetDirTree(top_level_dir,self.dir_path)

		# Next we check if the resulting dir_tree's first element has one
		# of the stock ratios
		if dir_tree != [] and dir_tree[0] in STOCK_RATIOS.values():
			dir_tree.pop(0)
		
		# And we insert the corresponding folder into the directory tree.
		# If type_ratio is None, it will insert 'Non-matching'
		try:
			dir_tree.insert(0,STOCK_RATIOS[type_ratio])
		except KeyError:
			dir_tree.insert(0,type_ratio)
		
		# We return the resulting operation as a dictionary
		result = {'dest' : top_level_dir,'dir_tree': dir_tree }
		
		return result

class Directory(object):
	path = None
	dir_name = None
	listing = {
			'directories' : None,
			'files' : None
		  }

	def GetDirectories(self,recursivity = RECURSIVE):
		import os
		if os.path.isdir(self.path):
			directories = {}
			filess = {}
			listing = {}
			cwd = os.getcwd()
			os.chdir(self.path)
			files = os.listdir(os.getcwd())
			for files in files:
				filename = os.path.split(files)[1]
				if os.path.isdir(files) and recursivity:
					directory = Directory(files)
					if directory.path != None:
						directories[filename] =  directory
					else:
						directory = None
				else:
					import Image
					try:
						im = Image.open(files)
						im = None
						filess[filename] = ImageFile(files)
					except IOError:
						pass
					except ValueError,err:
						print err
			os.chdir(cwd)
			if directories != {}:
				listing['directories'] = directories
			if filess != {}:
				listing['files'] = filess
			return listing

	def GetDictionary(self,tipo):
		if tipo == 'directories' or tipo == 'files':
			try:
				return self.listing[tipo]
			except (TypeError,KeyError),err:
				pass
		return None

	def __init__(self,directory,recursive = RECURSIVE):
		from os import path
		self.path = path.abspath(directory)
		if path.isdir(self.path):
			try:			
				self.listing = self.GetDirectories(recursive)
			except OSError,err:
				self.listing = None
				self.path = None
		else:
			self.path = None
		try:
			self.dir_name = path.split(self.path)[1]
		except AttributeError:
			self.dir_name = None

	## Method to print a list of all the directories and files (in that order) on screen
	#  
	#  @todo implement logging of this function
	def PrintDirectories(self):
		self.PrintDirs(0)

	def PrintDirs(self,depth):
		def SetSeparator(depth):
			separator = ''
			if depth != 0:
				if depth > 1:
					separator = "\t"*(depth-1)+'|'+('-'*(5*(depth-1)))+'>'
				else:
					separator = '|'+('-'*(5*depth))+'>'
			return separator
		separator = SetSeparator(depth)
		print separator,self.path
		depth += 1
		separator = SetSeparator(depth)
		try:
			if self.listing['directories'] != None:
				for direc in self.listing['directories'].values():
					direc.PrintDirs(depth)
		except KeyError:
			pass
		try:
			if self.listing['files'] != None:
				for files in self.listing['files'].values():
				     print separator,files.filename
		except KeyError:
			pass

	def IsEmpty(self):
		import os
		return os.listdir(self.path) == []

	def RemoveFile(self,image_file):
		if not isinstance(image_file,str):
			raise TypeError('RemoveFile(): Argument must be a string, got '+type(image_file).__name__)
		if image_file in self.self.listing['files']:
			self.listing['files'].get(image_file).img = None
			self.listing['files'].pop(image_file)

	def RemoveDir(self,directorio):
		if not isinstance(directorio,Directory):
			raise TypeError('RemoveDir(): Argument must be a directory, got '+type(directorio).__name__)
		directories = self.GetDictionary('directories')
		if directories != None and directorio.dir_name in directories:
			import os
			dir_name = directorio.path
			self.GetDictionary('directories').pop(directorio.dir_name)
			os.rmdir(dir_name)

	def DirHasFile(self,image_file):
		if not isinstance(image_file,str):
			raise TypeError('DirHasFile(): Argument must be a string, got '+type(image_file).__name__)
		return image_file in self.GetDictionary('files')


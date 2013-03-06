import os, platform
import shutil
import sublime, sublime_plugin

class ObjectType:
	folder = None
	packageTag = None
	hasMetadataFile = None
	def __init__(self, folder, packageTag, hasMetadataFile):
		self.folder = folder
		self.packageTag = packageTag
		self.hasMetadataFile = hasMetadataFile


class iforce_quick_compileCommand(sublime_plugin.WindowCommand):
	currentFile = None
	prjFolder = None
	payloadFolderName = 'payload'
	payloadFolder = None
	pathSep = None
	antBin = None

	def run(self, *args, **kwargs):
		objectType = None # Type of object being compiled

		if self.window.active_view().is_dirty():
			self.window.active_view().run_command('save')

		if platform.system() == 'Windows':
			self.pathSep = '\\'
			self.antBin = 'ant.bat'
		else:
			self.pathSep = '/'
			self.antBin = 'ant'

		self.prjFolder = self.window.folders()[0]
		print 'iForce: Project folder path' + self.prjFolder
		self.payloadFolder = self.prjFolder + '/' + self.payloadFolderName
		print 'iForce: Payload folder name' + self.payloadFolder

		try:
			shutil.rmtree(self.payloadFolder)
			print 'iForce: Old payload deleted'
		except Exception, e:
			print 'iForce: Couldn\'t delete old payload dir:', str(e)

		try:
			self.currentFile = self.window.active_view().file_name()
			print 'iForce: Current File: ' + self.currentFile

			fileHead, fileTail = os.path.split(self.currentFile)
			print 'iForce: Filename: '+ fileTail + ' head: '+fileHead

			# Identify the type of object being compiled
			objectTypes = [
				ObjectType('classes'        , 'ApexClass'     , True),
				ObjectType('components'     , 'ApexComponent' , True),
				ObjectType('objects'        , 'CustomObject'  , False),
				ObjectType('pages'          , 'ApexPage'      , True),
				ObjectType('staticresources', 'StaticResource', True),
				ObjectType('triggers'       , 'ApexTrigger'   , True)
			]

			for ot in objectTypes:
				if self.pathSep + ot.folder in self.currentFile:
					print 'iForce: file of type ' + ot.packageTag
					objectType = ot;
					break

			if objectType == None:
				print 'iForce: Invalid file type'
				return
			else:
				print 'iForce: payloadmeta ' + ot.packageTag

			# create dir
			os.makedirs(self.payloadFolder);
			os.makedirs(self.payloadFolder + '/' + objectType.folder);
			destFile = self.payloadFolder + '/' + objectType.folder + '/' + fileTail
			print 'iForce: DestFile '+destFile
			shutil.copyfile(self.currentFile, destFile)

			pfilename, pfileext = os.path.splitext(fileTail)
			print 'iForce: filename without extension ' + pfilename


			# try to copy existing meta file
			# if it does not exist, create one
			if objectType.hasMetadataFile:
				pmetapath = self.currentFile + '-meta.xml'
				if os.path.exists(pmetapath):
					pmetaname = os.path.basename(pmetapath)
					destFile = self.payloadFolder + '/' + objectType.folder + '/' + pmetaname
					shutil.copyfile(pmetapath, destFile)
				else:
					# write meta file
					if objectType.packageTag == 'ApexPage':
						metaFileContent = '<?xml version="1.0" encoding="UTF-8"?>\n<ApexPage xmlns="http://soap.sforce.com/2006/04/metadata"><apiVersion>25.0</apiVersion><description>'+pfilename+'</description><label>'+pfilename+'</label></ApexPage>'
					else:
						metaFileContent = '<?xml version="1.0" encoding="UTF-8"?>\n<'+objectType.packageTag+' xmlns="http://soap.sforce.com/2006/04/metadata"><apiVersion>25.0</apiVersion><status>Active</status></'+objectType.packageTag+'>'
					metaFile = self.payloadFolder + '/' + objectType.folder + '/' + fileTail + '-meta.xml'
					fhandle = open(metaFile,'w')
					fhandle.write(metaFileContent)
					fhandle.close()

			# write package file
			packageFileContent = '<?xml version="1.0" encoding="UTF-8"?>\n<Package xmlns="http://soap.sforce.com/2006/04/metadata"> <types> <members>'+pfilename+'</members> <name>'+objectType.packageTag+'</name> </types> <version>22.0</version> </Package>'
			packageFile = self.payloadFolder + '/package.xml'


			fhandle = open(packageFile,'w')
			fhandle.write(packageFileContent)
			fhandle.close()

			self.window.run_command('exec', {'cmd': [self.antBin, "-file", "iForce_build.xml", "-propertyfile", "iForce_build.properties", "qcompile"], 'working_dir':self.prjFolder})

		except Exception, e:
			print 'iForce: You should run with a file open: ', str(e)

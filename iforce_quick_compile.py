import os, platform
import shutil
import sublime, sublime_plugin

class iforce_quick_compileCommand(sublime_plugin.WindowCommand):
	currentFile = None
	prjFolder = None
	payloadFolderName = 'payload'
	payloadFolder = None
	payloadType = None
	payloadMetaTag = None
	pathSep = None
	antBin = None

	def run(self, *args, **kwargs):

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
			print 'iForce: Couldn\'t delete old payload dir'

		try:
			self.currentFile = self.window.active_view().file_name()
			print 'iForce: Current File: ' + self.currentFile
			
			fileHead, fileTail = os.path.split(self.currentFile)
			print 'iForce: Filename: '+ fileTail + ' head: '+fileHead

			if self.pathSep + 'classes' in self.currentFile:
				print 'iForce: file of type class'
				self.payloadType = 'classes'
				payloadMetaTag = 'ApexClass'
			elif self.pathSep + 'pages' in self.currentFile:
				print 'iForce: file of type page'
				self.payloadType = 'pages'
				payloadMetaTag = 'ApexPage'
			elif self.pathSep + 'triggers' in self.currentFile:
				print 'iForce: file of type trigger'
				self.payloadType = 'triggers'
				payloadMetaTag = 'ApexTrigger'
			else:
				print 'iForce: you can only compile class/page/trigger'
			
			print 'iForce: payloadmeta ' + payloadMetaTag

			# create dir
			os.makedirs(self.payloadFolder);
			os.makedirs(self.payloadFolder + '/' + self.payloadType);
			destFile = self.payloadFolder + '/' + self.payloadType + '/' + fileTail
			print 'iForce: DestFile '+destFile
			shutil.copyfile(self.currentFile, destFile)

			pfilename, pfileext = os.path.splitext(fileTail)
			print 'iForce: filename without extension ' + pfilename
			

			# write meta file	
			if payloadMetaTag == 'ApexPage':
				metaFileContent = '<?xml version="1.0" encoding="UTF-8"?>\n<ApexPage xmlns="http://soap.sforce.com/2006/04/metadata"><apiVersion>25.0</apiVersion><description>'+pfilename+'</description><label>'+pfilename+'</label></ApexPage>'
			else:
				metaFileContent = '<?xml version="1.0" encoding="UTF-8"?>\n<'+payloadMetaTag+' xmlns="http://soap.sforce.com/2006/04/metadata"><apiVersion>25.0</apiVersion><status>Active</status></'+payloadMetaTag+'>'
			metaFile = self.payloadFolder + '/' + self.payloadType + '/' + fileTail + '-meta.xml'
			fhandle = open(metaFile,'w')
			fhandle.write(metaFileContent) 
			fhandle.close()

			# write package file
			packageFileContent = '<?xml version="1.0" encoding="UTF-8"?>\n<Package xmlns="http://soap.sforce.com/2006/04/metadata"> <types> <members>'+pfilename+'</members> <name>'+payloadMetaTag+'</name> </types> <version>22.0</version> </Package>'
			packageFile = self.payloadFolder + '/package.xml' 
			

			fhandle = open(packageFile,'w')
			fhandle.write(packageFileContent) 
			fhandle.close()

			self.window.run_command('exec', {'cmd': [self.antBin, "qcompile"], 'working_dir':self.prjFolder})

		except Exception, e:
			print 'iForce: You should run with a file open.'

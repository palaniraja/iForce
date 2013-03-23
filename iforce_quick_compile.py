import os, platform
import shutil
import sublime, sublime_plugin
import logging

antBin = 'ant.bat' if platform.system() == 'Windows' else 'ant'

class ObjectType:
	folder = None
	packageTag = None
	extension = None
	hasMetadataFile = None
	def __init__(self, folder, packageTag, extension, hasMetadataFile):
		self.folder = folder
		self.packageTag = packageTag
		self.extension = extension
		self.hasMetadataFile = hasMetadataFile

# Identify the type of object being compiled
objectTypes = [
	ObjectType('classes'        , 'ApexClass'     , 'cls'      , True),
	ObjectType('components'     , 'ApexComponent' , 'component', True),
	ObjectType('objects'        , 'CustomObject'  , 'object'   , False),
	ObjectType('pages'          , 'ApexPage'      , 'page'     , True),
	ObjectType('staticresources', 'StaticResource', 'resource' , True),
	ObjectType('triggers'       , 'ApexTrigger'   , 'trigger'  , True)
]

typesByFolder = {}
for ot in objectTypes:
	typesByFolder[ot.folder] = ot;

def create_metadata_file(sourcefile):
	# If metadata file already exists, do nothing
	metaFile = sourcefile + '-meta.xml'
	if os.path.exists(metaFile):
		return

	# Get required info
	folderpath, filename = os.path.split(sourcefile)
	srcpath, folder = os.path.split(folderpath)
	objectType = typesByFolder[folder]
	if objectType.packageTag == 'ApexPage':
		metaFileContent = '<?xml version="1.0" encoding="UTF-8"?>\n<ApexPage xmlns="http://soap.sforce.com/2006/04/metadata"><apiVersion>25.0</apiVersion><description>'+filename+'</description><label>'+filename+'</label></ApexPage>'
	else:
		metaFileContent = '<?xml version="1.0" encoding="UTF-8"?>\n<'+objectType.packageTag+' xmlns="http://soap.sforce.com/2006/04/metadata"><apiVersion>25.0</apiVersion><status>Active</status></'+objectType.packageTag+'>'

	# Create the file
	fhandle = open(metaFile,'w')
	fhandle.write(metaFileContent)
	fhandle.close()


def copy_to_payload(sourcefile, payload_path):
	# Get required information
	path, filename = os.path.split(sourcefile)
	path, foldername = os.path.split(path)
	objectType = typesByFolder.get(foldername)
	if objectType == None:
		raise LookupError('The file does not appear to be a Force.com file: ' + filename)

	# Copy files
	targetfolder = payload_path + os.sep + foldername
	targetfile = targetfolder + os.sep + filename
	os.makedirs(targetfolder)
	shutil.copyfile(sourcefile, targetfile)
	if objectType.hasMetadataFile:
		create_metadata_file(sourcefile)
		shutil.copyfile(sourcefile + '-meta.xml', targetfile + '-meta.xml')

def generate_package_xml(payload_path):
	package_path = payload_path + os.sep + 'package.xml'

	# Remove package file if it exists already
	if os.path.exists(package_path):
		os.remove(package_path)

	# Open the file and add required headers
	fhandle = open(package_path, 'w')
	fhandle.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	fhandle.write('<Package xmlns="http://soap.sforce.com/2006/04/metadata">')

	# For each recognized type of artifact, add them to the package file
	for ot in objectTypes:
		folder = payload_path + os.sep + ot.folder
		if (os.path.exists(folder)):
			fhandle.write('<types>')

			# For each file in that folder, add it's entry
			for f in os.listdir(folder):
				fname, fext = os.path.splitext(f)
				if fext == '.' + ot.extension:
					fhandle.write('<members>' + fname + '</members>')

			fhandle.write('<name>' + ot.packageTag + '</name>')
			fhandle.write('</types>');

	# Close the file
	fhandle.write('<version>25.0</version>')
	fhandle.write('</Package>')
	fhandle.close()


class iforce_quick_compileCommand(sublime_plugin.WindowCommand):
	currentFile = None
	prjFolder = None
	payloadFolderName = 'payload'
	payloadFolder = None

	def run(self, *args, **kwargs):
		objectType = None # Type of object being compiled

		if self.window.active_view().is_dirty():
			self.window.active_view().run_command('save')

		self.prjFolder = self.window.folders()[0]
		print 'iForce: Project folder path' + self.prjFolder
		self.payloadFolder = self.prjFolder + os.sep + self.payloadFolderName
		print 'iForce: Payload folder name' + self.payloadFolder

		try:
			shutil.rmtree(self.payloadFolder)
			print 'iForce: Old payload deleted'
		except Exception, e:
			print 'iForce: Couldn\'t delete old payload dir:', str(e)

		# create dir
		os.makedirs(self.payloadFolder)

		# Copy current file to payload folder
		try:
			self.currentFile = self.window.active_view().file_name()
			copy_to_payload(self.currentFile, self.payloadFolder)
		except LookupError, e:
			logging.exception('iForce: Unable to copy file to payload.')
			sublime.error_message('Unable to copy file to payload:\n' + str(e))
			return

		# write package file
		generate_package_xml(self.payloadFolder)

		self.window.run_command('exec', {'cmd': [antBin, "-file", "iForce_build.xml", "-propertyfile", "iForce_build.properties", "qcompile"], 'working_dir':self.prjFolder})

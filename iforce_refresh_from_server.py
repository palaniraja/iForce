import os, platform
import sublime, sublime_plugin


class iforce_refresh_from_serverCommand(sublime_plugin.WindowCommand):
	currentProjectFolder = None
	antBin = None

	def run(self, *args, **kwargs):
		if platform.system() == 'Windows':
			self.antBin = 'ant.bat'
		else:
			self.antBin = 'ant'
		
		self.currentProjectFolder = self.window.folders()[0]
		print 'iForce: Prj Path: ' + self.currentProjectFolder
		# os.chdir(folder)
		self.window.run_command('exec', {'cmd': [self.antBin, "getLatest"], 'working_dir':self.currentProjectFolder})


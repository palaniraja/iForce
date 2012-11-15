import os
import urllib
import zipfile

import sublime, sublime_plugin


def getunzipped(theurl, thedir):
  # print 'url:' + theurl
  # print 'thedir' + thedir
  # print 'test' + test
  name = os.path.join(thedir, 'temp.zip')
  try:
    name, hdrs = urllib.urlretrieve(theurl, name)
  except IOError, e:
    print "iForce: Can't retrieve %r to %r: %s" % (theurl, thedir, e)
    return
  try:
    extract(name, thedir)
    os.unlink(name)
  except zipfile.error, e:
    print "iForce: Bad zipfile (from %r): %s" % (theurl, e)
    return
  
def extract(zipfilepath, extractiondir):
    zip = zipfile.ZipFile(zipfilepath)
    zip.extractall(path=extractiondir) 

class iforce_start_new_projectCommand(sublime_plugin.WindowCommand):

  sfTempArchive = ''
  outputdir = ''

  def __init__(self, *args, **kwargs):
    super(iforce_start_new_projectCommand, self).__init__(*args, **kwargs)

  def on_done(self, dirname):
    # print 'dirname: ' + dirname
    self.outputdir = dirname
    # print 'outputdir: '+ self.outputdir
    extract(self.sfTempArchive, self.outputdir)
    print 'iForce: iforce_start_new_project [DONE]'
    

  def run(self, *args, **kwargs):
    initialFolder = self.window.folders()[0]
    # self.getunzipped('http://localhost/sublime/SFtemp.zip', os.getcwd())
    #getunzipped('http://localhost/sublime/SFtemp.zip', os.getcwd())
    self.sfTempArchive = sublime.packages_path() + kwargs.get('file')
    # print 'Archive: ' + self.sfTempArchive
    self.window.show_input_panel(
                "iForce: Select a location to setup this project: ",
                initialFolder,
                self.on_done,
                None,
                None
            )
    
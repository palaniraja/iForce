import os
import urllib
import shutil

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

class iforce_start_new_projectCommand(sublime_plugin.WindowCommand):

  def __init__(self, *args, **kwargs):
    super(iforce_start_new_projectCommand, self).__init__(*args, **kwargs)

  def on_done(self, dirname):
    # print 'dirname: ' + dirname
    outputdir = dirname
    iforce_path = sublime.packages_path() + '/iForce'

    # copy build files to folder
    shutil.copy(iforce_path + '/iForce_build.xml', outputdir)
    shutil.copy(iforce_path + '/iForce_build.properties', outputdir)

    # copy package.xml and generate project folders
    shutil.copy(iforce_path + '/package.xml', outputdir)
    for folder in ['classes', 'components', 'pages', 'triggers']:
      if not os.path.exists(outputdir + '/' + folder):
        os.makedirs(outputdir + '/' + folder)

    # print 'outputdir: '+ self.outputdir
    print 'iForce: iforce_start_new_project [DONE]'


  def run(self, *args, **kwargs):
    initialFolder = self.window.folders()[0]
    # print 'Archive: ' + self.sfTempArchive
    self.window.show_input_panel(
                "iForce: Select a location to setup this project: ",
                initialFolder,
                self.on_done,
                None,
                None
            )

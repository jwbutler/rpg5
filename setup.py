from distutils.core import setup
import glob, os, pygame, py2exe, shutil

PYGAMEDIR = os.path.split(pygame.base.__file__)[0]
SDL_DLLS = glob.glob(os.path.join(PYGAMEDIR,'*.dll'))

if setup(windows=['main.py'],
      data_files = [
                    ("tga", glob.glob("tga\\*.tga")),
                    ("tga\levels", glob.glob("tga\\levels\\*.tga")),
                    ("sounds", glob.glob("sounds\\*.ogg")),
                   ],
      options = {"py2exe": {
                          "optimize": 2,
                          "compressed": 1,
                          "bundle_files": 3,
                          "excludes": ['numpy', 'tcl', 'tk']}
              },
      zipfile = None
     ):

  print "*** Copying SDL DLLS ***"
  for f in SDL_DLLS:
    fname = os.path.basename(f)
    try:
      shutil.copyfile(f,os.path.join('dist',fname))
      print "Copied", f, "successfully"
    except:
      print "Couldn't copy", f

  print "*** Copying runtimes, shortcuts, documentation ***"
  filenames = glob.glob("runtimes//*.*") + ["windowed.bat", "README", "COPYING"]
  for f in filenames:
    fname = os.path.basename(f)
    try:
      shutil.copyfile(f, os.path.join("dist", fname))
      print "Copied", f, "successfully"
    except:
      print "Error copying " + f

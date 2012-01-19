################################################################################
# Ganga Project. http://cern.ch/ganga
#
# $Id: LCGStorageElementFile.py,v 0.1 2011-02-12 15:40:00 idzhunov Exp $
################################################################################

from Ganga.GPIDev.Schema import *

from OutputFile import OutputFile

class LCGStorageElementFile(OutputFile):
    """LCGStorageElementFile represents a class marking an output file to be written into LCG SE
    """
    _schema = Schema(Version(1,1), {
        'name'        : SimpleItem(defvalue="",doc='name of the file'),
        'se'          : SimpleItem(defvalue='', copyable=1, doc='the LCG SE hostname'),
        #'se_type'     : SimpleItem(defvalue='srmv2', copyable=1, doc='the LCG SE type'),
        #'se_rpath'    : SimpleItem(defvalue='generated', copyable=1, doc='the relative path to the VO directory on the SE'),
        'se_type'     : SimpleItem(defvalue='', copyable=1, doc='the LCG SE type'),
        'se_rpath'    : SimpleItem(defvalue='', copyable=1, doc='the relative path to the VO directory on the SE'),
        'lfc_host'    : SimpleItem(defvalue='', copyable=1, doc='the LCG LFC hostname'),
        'srm_token'   : SimpleItem(defvalue='', copyable=1, doc='the SRM space token, meaningful only when se_type is set to srmv2')
})
    _category = 'outputfiles'
    _name = "LCGStorageElementFile"
    _location = []
    _exportmethods = [ "location" , "setLocation" , "get" ]

    def __init__(self,name='', **kwds):
        """ name is the name of the output file that has to be written into LCG SE
        """
        super(LCGStorageElementFile, self).__init__(name, **kwds)

        from Ganga.Utility.Config import getConfig
        lcgSEConfig = getConfig('LCGStorageElementOutput')

        self.lfc_host = lcgSEConfig['LFC_HOST']
        self.se = lcgSEConfig['dest_SRM']

    def __setattr__(self, attr, value):
        if attr == 'se_type' and value not in ['','srmv1','srmv2','se']:
            raise AttributeError('invalid se_type: %s' % value)
        super(LCGStorageElementFile,self).__setattr__(attr, value)

    def __construct__(self,args):
        super(LCGStorageElementFile,self).__construct__(args)

            
    def __repr__(self):
        """Get the representation of the file."""

        return "LCGStorageElementFile(name='%s')"% self.name

    def setLocation(self, location):
        """
        Return list with the locations of the post processed files (if they were configured to upload the output somewhere)
        """
        if location not in self._location:
            self._location.append(location)
        
    def location(self):
        """
        Return list with the locations of the post processed files (if they were configured to upload the output somewhere)
        """
        return self._location

    def get(self, dir):
        """
        Retrieves locally all files matching this LCGStorageElementFile object pattern
        """
        import os
        import subprocess
        
        # system command executor with subprocess
        def execSyscmdSubprocess(cmd):

            exitcode = -999
            mystdout = ''
            mystderr = ''

            try:
                child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (mystdout, mystderr) = child.communicate()
                exitcode = child.returncode
            finally:
                pass

            return (exitcode, mystdout, mystderr)

        if not os.path.isdir(dir):
            print "%s is not a valid directory.... " % dir
            return

        #set lfc host
        os.environ['LFC_HOST'] = self.lfc_host

        from Ganga.Utility.Config import getConfig 
        vo = getConfig('LCG')['VirtualOrganisation']  

        for location in self._location:
            destFileName = os.path.join(dir, location[-10:])
            cmd = 'lcg-cp --vo %s %s file:%s' % (vo, location, destFileName)
            print 'executing ... %s' % cmd
            (exitcode, mystdout, mystderr) = execSyscmdSubprocess(cmd)

            if exitcode == 0:
                print 'job output downloaded here %s' % destFileName
            else:
                print 'command %s failed to execute , reason for failure is %s' % (cmd, mystderr)


# add LCGStorageElementFile objects to the configuration scope (i.e. it will be possible to write instatiate LCGStorageElementFile() objects via config file)
import Ganga.Utility.Config
Ganga.Utility.Config.config_scope['LCGStorageElementFile'] = LCGStorageElementFile

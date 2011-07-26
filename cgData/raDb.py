

class raDb:
	
    
    def initSchema(self):
        """
		`name` varchar(255) default NULL,
		`downSampleTable` varchar(255) default NULL,
		`sampleTable` varchar(255) default NULL,
		`clinicalTable` varchar(255) default NULL,
		`columnTable` varchar(255) default NULL,
		`shortLabel` varchar(255) default NULL,
		`longLabel` varchar(255) default NULL,
		`expCount` int(10) unsigned default NULL,
		`groupName` varchar(255) default NULL,
		`microscope` varchar(255) default NULL,
		`aliasTable` varchar(255) default NULL,
		`dataType` varchar(255) default NULL,
		`platform` varchar(255) default NULL,
		`security` varchar(255) default NULL,
		`profile` varchar(255) default NULL,
		"""
		raDbHandle.write( "INSERT into raDb( name, sampleTable, clinicalTable, columnTable, aliasTable, shortLabel) VALUES ( '%s', '%s', '%s', '%s', '%s', '%s');\n" % \
			( "genomic_" + genomicName, "sample_" + sampleName, "clinical_" + clinicalNames[0], "clinical_" + clinicalNames[0] + "_colDb", "genomic_" + genomicName + "_alias", genomicName ))
		raDbHandle.flush()
	

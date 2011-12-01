
formatTable = {
    "probeMap" : 
        {
            "name" : "probeMap",
            "type" : "type",
            "form" : "table",
            "columnDef" : [
            "probeName",
            "aliasList",
            "chrom",
            "chromStart",
            "chromEnd",
            "strand"
            ],
            "primaryKey" : "probeName"
        },
        
    "genomicMatrix" : 
        {
            "name" : "genomicMatrix",
            "type" : "type",
            "form" : "matrix",
            "rowType" : "probeMap",
            "colType" : "idMap",
            "valueType" : "float",
            "nullString" : "NA"
        },
        
    "clinicalMatrix" : 
        {
            "name" : "clinicalMatrix",
            "type" : "type",
            "form" : "matrix",
            "rowType" : "idMap",
            "colType" : "clinicalFeature",
            "valueType" : "str",
            "nullString" : ""
        },
        
    "idMap" : 
        {
            "name" : "idMap",
            "type" : "type",
            "form" : "table",
            "columnDef" : [
                "id",
                "child"
            ],
            "groupKey" : "id",
            "optional" : "child"
        },
        
    "genomicSegment" : 
        {
            "name" : "genomicSegment",
            "type" : "type",
            "form" : "table",
            "columnDef" : [
                "id",
                "chrom",
                "chromStart",
                "chromEnd",
                "strand",
                "value"
            ],
            "groupKey" : "id"
        },
        
    "clinicalFeature" : 
        {
            "name" : "clinicalFeature",
            "type" : "type",
            "form" : "table",
            "columnDef" : [
                "featureName",
                "predicate",
                "value"
            ],
            "groupKey" : "featureName"
        },
        
    "genomicMutation" : 
        {
            "name" : "genomicMutation",
            "type" : "type",
            "form" : "table",
            "columnDef" : [
                "id",
                "chrom",
                "chromStart",
                "chromeEnd",
                "altSeq",
                "coverage",
                "frequency",
                "baseQuality",
                "rnaCoverage",
                "rnaFrequency",
                "rnaBaseQuality",
                "gsType",
                "patientName"
            ],
            "groupKey" : "id"
        },
        
    "vcf" : 
        {
            "name" : "vcf",
            "type" : "type",
            "form" : "custom"
        }

}
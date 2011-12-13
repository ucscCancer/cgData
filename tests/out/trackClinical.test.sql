drop table if exists clinical_test;
CREATE TABLE clinical_test (
	sampleID int,
	sampleName ENUM ('sample1','sample4','sample17','sample63','sample101'),
	`age` FLOAT default NULL,
	`status` ENUM( 'Negative','Positive' ) default NULL
    ) engine 'MyISAM';
    INSERT INTO clinical_test VALUES ( 0, 'sample1', '3','Negative' );
INSERT INTO clinical_test VALUES ( 1, 'sample4', '56','Positive' );
INSERT INTO clinical_test VALUES ( 2, 'sample17', '89','Positive' );
INSERT INTO clinical_test VALUES ( 3, 'sample63', '67','Negative' );
INSERT INTO clinical_test VALUES ( 4, 'sample101', '30','Negative' );
DELETE from colDb where clinicalTable = 'clinical_test';INSERT INTO colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( 'sampleName', 'sample name', 'sample name', 'sampleName', 'clinical_test', 'coded', 'on',1);
INSERT INTO colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( 'age', 'age', 'age', 'age', 'clinical_test', 'minMax', 'on', 1.000000);
INSERT INTO colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( 'status', 'status', 'status', 'status', 'clinical_test', 'coded', 'on', 1.000000);

drop table if exists clinical_test;
CREATE TABLE clinical_test (
	sampleID int,
	sampleName ENUM ('1','101','17','4','sample63'),
	`age` FLOAT default NULL,
	`status` ENUM( 'Negative','Positive' ) default NULL
    ) engine 'MyISAM';
    INSERT INTO clinical_test VALUES ( 0, '1', '3','Negative' );
INSERT INTO clinical_test VALUES ( 1, '101', '30','Negative' );
INSERT INTO clinical_test VALUES ( 2, '17', '89','Positive' );
INSERT INTO clinical_test VALUES ( 3, '4', '56','Positive' );
INSERT INTO clinical_test VALUES ( 4, 'sample63', '67','Negative' );
DELETE from colDb where clinicalTable = 'clinical_test';INSERT INTO colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( 'sampleName', 'sample name', 'sample name', 'sampleName', 'clinical_test', 'coded', 'on',1);
INSERT INTO colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( 'age', 'age', 'age', 'age', 'clinical_test', 'minMax', 'on', 1.000000);
INSERT INTO colDb(name, shortLabel,longLabel,valField,clinicalTable,filterType,visibility,priority) VALUES( 'status', 'status', 'status', 'status', 'clinical_test', 'coded', 'on', 1.000000);
